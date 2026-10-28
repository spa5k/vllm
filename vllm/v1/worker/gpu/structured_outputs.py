# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
from collections.abc import Callable

import numpy as np
import torch

import vllm.envs as envs
from vllm.config import VllmConfig
from vllm.triton_utils import tl, triton
from vllm.utils.math_utils import cdiv
from vllm.utils.torch_utils import PIN_MEMORY, async_tensor_h2d
from vllm.v1.core.sched.output import GrammarOutput
from vllm.v1.worker.gpu.input_batch import InputBatch

# Overridden on CPU in vllm/v1/worker/cpu/shm.py.
GRAMMAR_BITMASK_BLOCK_SIZE = 8192


def get_sparse_logits_callback(
    model: torch.nn.Module, config: VllmConfig
) -> Callable[[torch.Tensor, torch.Tensor], torch.Tensor | None] | None:
    if (
        config.structured_outputs_config.enable_sparse_lm_head
        and config.parallel_config.tensor_parallel_size == 1
        and config.lora_config is None
        and config.speculative_config is None
        and config.cache_config.kv_cache_memory_bytes is None
        and not envs.VLLM_ENABLE_STARTUP_PLAN
        and not envs.VLLM_BATCH_INVARIANT
    ):
        return getattr(model, "compute_logits_sparse", None)
    return None


def _projection_token_ids(
    input_batch: InputBatch, grammar_output: GrammarOutput, vocab_size: int
) -> np.ndarray | None:
    req_ids = input_batch.req_ids
    grammar_ids = grammar_output.structured_output_request_ids
    if (
        input_batch.num_draft_tokens != 0
        or not req_ids
        or len(grammar_ids) != len(req_ids)
        or set(grammar_ids) != set(req_ids)
        or not np.all(np.diff(input_batch.cu_num_logits_np) == 1)
    ):
        return None
    bitmask = grammar_output.grammar_bitmask
    if bitmask.dtype != np.int32 or bitmask.shape != (
        len(req_ids),
        cdiv(vocab_size, 32),
    ):
        return None
    limit = min(4096, vocab_size // 8)
    words = np.bitwise_or.reduce(bitmask, axis=0).astype("<u4", copy=False)
    if vocab_size % 32:
        words[-1] &= np.uint32((1 << (vocab_size % 32)) - 1)
    live_words = np.flatnonzero(words)
    if live_words.size > limit:
        return None
    unpacked = np.unpackbits(words[live_words].view(np.uint8), bitorder="little")
    if np.count_nonzero(unpacked) > limit:
        return None
    bits = np.flatnonzero(unpacked)
    token_ids = live_words[bits // 32] * 32 + bits % 32
    token_ids = token_ids[token_ids < vocab_size]
    return token_ids if token_ids.size <= limit else None


def grammar_invalid_drafts(
    input_batch: InputBatch,
    grammar_req_ids: list[str],
    num_acceptable_drafts: list[int] | None,
) -> torch.Tensor | None:
    """Mask over logit rows whose draft was verified against a permissive row.

    Draft i sits at local position i + 1, and drafts from `num_acceptable_drafts`
    on met `_full_mask`. Local positions come from the device `cu_num_logits`, so
    this stays right when adaptive verification trims drafts on device.
    Returns None when there is nothing to invalidate.
    """
    if not grammar_req_ids or input_batch.num_draft_tokens == 0:
        return None
    req_id_to_idx = {req_id: i for i, req_id in enumerate(input_batch.req_ids)}
    limit = np.full(input_batch.num_reqs, np.iinfo(np.int32).max, dtype=np.int32)
    for i, req_id in enumerate(grammar_req_ids):
        req_idx = req_id_to_idx.get(req_id)
        if req_idx is not None:
            # None (an older scheduler, or warmup): invalidate the whole window.
            limit[req_idx] = (
                num_acceptable_drafts[i] if num_acceptable_drafts is not None else 0
            )
    # Adaptive verification only trims drafts, so this bound holds either way.
    num_drafts = input_batch.num_draft_tokens_per_req
    if num_drafts is not None and (limit >= num_drafts).all():
        return None
    local_pos = input_batch.expanded_local_pos
    cu_num_logits = input_batch.cu_num_logits
    row_limit = torch.repeat_interleave(
        async_tensor_h2d(limit, device=local_pos.device),
        cu_num_logits[1:] - cu_num_logits[:-1],
        output_size=local_pos.shape[0],
    )
    return local_pos > row_limit


class StructuredOutputsWorker:
    def __init__(
        self,
        max_num_logits: int,
        vocab_size: int,
        device: torch.device,
        mask_stride: int,
        compute_logits: Callable[[torch.Tensor], torch.Tensor | None],
        compute_sparse_logits: Callable[
            [torch.Tensor, torch.Tensor], torch.Tensor | None
        ]
        | None = None,
    ):
        self.logits_indices = torch.zeros(
            max_num_logits, dtype=torch.int32, device=device
        )
        self.grammar_bitmask = torch.zeros(
            (max_num_logits, cdiv(vocab_size, 32)), dtype=torch.int32, device=device
        )
        self.device = device
        self.copy_stream = torch.cuda.Stream()
        self.mask_stride = mask_stride
        self.vocab_size = vocab_size
        self._compute_logits = compute_logits
        self._compute_sparse_logits = compute_sparse_logits

    def profile_sparse_logits(self, hidden_states: torch.Tensor) -> None:
        if self._compute_sparse_logits is not None:
            token_ids = torch.arange(
                min(4096, self.vocab_size // 8),
                device=hidden_states.device,
                dtype=torch.int64,
            )
            self._compute_sparse_logits(hidden_states, token_ids)

    def compute_logits(
        self,
        hidden_states: torch.Tensor,
        input_batch: InputBatch,
        grammar_output: GrammarOutput | None,
    ) -> torch.Tensor | None:
        if self._compute_sparse_logits is not None and grammar_output is not None:
            token_ids = _projection_token_ids(
                input_batch, grammar_output, self.vocab_size
            )
            if token_ids is not None:
                ids = async_tensor_h2d(
                    token_ids, device=hidden_states.device, dtype=torch.int64
                )
                return self._compute_sparse_logits(hidden_states, ids)
        return self._compute_logits(hidden_states)

    def apply_grammar_bitmask(
        self,
        logits: torch.Tensor,
        input_batch: InputBatch,
        grammar_req_ids: list[str],
        grammar_bitmask: np.ndarray,
    ) -> None:
        if not grammar_req_ids:
            return

        # Asynchronously copy the bitmask to GPU.
        with torch.cuda.stream(self.copy_stream):
            bitmask = async_tensor_h2d(
                grammar_bitmask, out=self.grammar_bitmask[: grammar_bitmask.shape[0]]
            )

        # Each grammar request owns `mask_stride` bitmask rows. Key them by
        # (request, position); the kernel skips positions beyond the device
        # cu_num_logits, which adaptive verification may trim.
        req_id_to_idx = {req_id: i for i, req_id in enumerate(input_batch.req_ids)}
        mapping = [
            req_id_to_idx[req_id] * self.mask_stride + position
            for req_id in grammar_req_ids
            for position in range(self.mask_stride)
        ]

        # Asynchronously copy the mapping to GPU.
        with torch.cuda.stream(self.copy_stream):
            logits_indices = torch.tensor(
                mapping, dtype=torch.int32, device="cpu", pin_memory=PIN_MEMORY
            )
            logits_indices = self.logits_indices[: len(mapping)].copy_(
                logits_indices, non_blocking=True
            )

        # Ensure all async copies are complete before launching the kernel.
        current_stream = torch.cuda.current_stream()
        current_stream.wait_stream(self.copy_stream)

        num_masks = bitmask.shape[0]
        assert num_masks == len(mapping)
        vocab_size = logits.shape[-1]
        BLOCK_SIZE = GRAMMAR_BITMASK_BLOCK_SIZE
        grid = (num_masks, triton.cdiv(vocab_size, BLOCK_SIZE))
        _apply_grammar_bitmask_kernel[grid](
            logits,
            logits.stride(0),
            logits_indices,
            input_batch.cu_num_logits,
            bitmask,
            bitmask.stride(0),
            vocab_size,
            MASK_STRIDE=self.mask_stride,
            BLOCK_SIZE=BLOCK_SIZE,
        )

        # Ensure the copy stream waits for the device tensors to finish being used
        # before it re-uses or deallocates them
        self.copy_stream.wait_stream(current_stream)


# Adapted from
# https://github.com/mlc-ai/xgrammar/blob/main/python/xgrammar/kernels/apply_token_bitmask_inplace_triton.py
@triton.jit
def _apply_grammar_bitmask_kernel(
    logits_ptr,
    logits_stride,
    logits_indices_ptr,
    cu_num_logits_ptr,
    bitmask_ptr,
    bitmask_stride,
    vocab_size,
    MASK_STRIDE: tl.constexpr,
    BLOCK_SIZE: tl.constexpr,
):
    bitmask_idx = tl.program_id(0)
    mapping_idx = tl.load(logits_indices_ptr + bitmask_idx)
    req_idx = mapping_idx // MASK_STRIDE
    position_idx = mapping_idx % MASK_STRIDE
    logits_idx = tl.load(cu_num_logits_ptr + req_idx)
    num_req_logits = tl.load(cu_num_logits_ptr + req_idx + 1) - logits_idx
    logits_idx += position_idx
    position_is_active = position_idx < num_req_logits

    # Load the bitmask.
    block_id = tl.program_id(1)
    bitmask_offset = (block_id * BLOCK_SIZE) // 32 + tl.arange(0, BLOCK_SIZE // 32)
    packed_bitmask = tl.load(
        bitmask_ptr + bitmask_idx * bitmask_stride + bitmask_offset,
        mask=bitmask_offset < bitmask_stride,
    )
    # Unpack the bitmask.
    bitmask = ((packed_bitmask[:, None] >> (tl.arange(0, 32)[None, :])) & 1) == 0
    bitmask = bitmask.reshape(BLOCK_SIZE)

    # Apply the bitmask to the logits.
    block_offset = block_id * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    tl.store(
        logits_ptr + logits_idx * logits_stride + block_offset,
        -float("inf"),
        mask=position_is_active & bitmask & (block_offset < vocab_size),
    )

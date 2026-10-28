# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Which speculative drafts a structured-output request may accept.

`StructuredOutputManager.grammar_bitmask` fills row i before it inspects
`req_tokens[i]`, so with the first -1 placeholder at index j rows 0..j carry a
real mask and rows j+1.. carry the all-permissive `_full_mask`. Drafts j..K-1
must therefore be rejected, or the request samples with no grammar constraint
at a position the model really does sample.
"""

from types import SimpleNamespace

import numpy as np
import pytest
import torch

from vllm.config import DeviceConfig, VllmConfig, set_current_vllm_config
from vllm.model_executor.layers.logits_processor import LogitsProcessor
from vllm.model_executor.layers.vocab_parallel_embedding import (
    UnquantizedEmbeddingMethod,
)
from vllm.v1.worker.gpu.structured_outputs import (
    StructuredOutputsWorker,
    _projection_token_ids,
    get_sparse_logits_callback,
    grammar_invalid_drafts,
)


def _input_batch(req_ids, num_drafts, num_admitted=None):
    """`num_admitted` is what adaptive verification kept on device."""
    num_admitted = num_drafts if num_admitted is None else num_admitted
    rows = [n + 1 for n in num_admitted]
    return SimpleNamespace(
        req_ids=list(req_ids),
        num_reqs=len(req_ids),
        num_draft_tokens=sum(num_drafts),
        num_draft_tokens_per_req=np.array(num_drafts, dtype=np.int32),
        cu_num_logits=torch.tensor([0, *np.cumsum(rows)], dtype=torch.int32),
        expanded_local_pos=torch.cat(
            [torch.arange(n, dtype=torch.int32) for n in rows]
        ),
    )


def _invalid_rows(batch, grammar_req_ids, num_acceptable):
    mask = grammar_invalid_drafts(batch, grammar_req_ids, num_acceptable)
    return None if mask is None else mask.nonzero().flatten().tolist()


def test_reject_whole_window_when_nothing_was_backfilled():
    # Request "g" is at rows 0..3 (1 + 3 drafts), so its drafts are rows 1..3.
    batch = _input_batch(["g", "p"], [3, 3])
    assert _invalid_rows(batch, ["g"], [0]) == [1, 2, 3]


def test_keep_the_drafts_the_bitmask_could_see():
    batch = _input_batch(["g", "p"], [3, 3])
    assert _invalid_rows(batch, ["g"], [2]) == [3]


def test_follow_the_device_layout_under_adaptive_verification():
    # Scheduled 3 drafts each, but adaptive verification admitted 2 for "a" and
    # 3 for "b": the real rows are a=0..2, b=3..6, not the scheduled 0..3, 4..7.
    batch = _input_batch(["a", "b"], [3, 3], num_admitted=[2, 3])
    assert _invalid_rows(batch, ["a", "b"], [1, 0]) == [2, 4, 5, 6]


@pytest.mark.parametrize("vocab_size", [32, 33, 65, 128256, 151936])
def test_projection_union_preserves_token_ids_and_ignores_padding(vocab_size):
    batch = _input_batch(["a", "b"], [0, 0])
    batch.cu_num_logits_np = batch.cu_num_logits.numpy()
    mask = np.zeros((2, (vocab_size + 31) // 32), dtype=np.int32)
    tokens = sorted({0, 31, vocab_size - 1})
    for i, token in enumerate(tokens):
        mask[i % 2, token // 32] |= np.uint32(1 << (token % 32)).view(np.int32)
    if vocab_size % 32:
        mask[:, -1] |= np.int32(-1 << (vocab_size % 32))
    grammar = SimpleNamespace(
        structured_output_request_ids=["b", "a"], grammar_bitmask=mask
    )
    np.testing.assert_array_equal(
        _projection_token_ids(batch, grammar, vocab_size), tokens
    )


@pytest.mark.parametrize(
    "case", ["unconstrained_row", "drafts", "extra_logits", "wide", "wrong_width"]
)
def test_projection_falls_back_for_unsupported_batches(case):
    batch = _input_batch(["a", "b"], [0, 0])
    batch.cu_num_logits_np = batch.cu_num_logits.numpy()
    grammar = SimpleNamespace(
        structured_output_request_ids=["b", "a"],
        grammar_bitmask=np.ones((2, 3), dtype=np.int32),
    )
    if case == "unconstrained_row":
        grammar.structured_output_request_ids.pop()
    elif case == "drafts":
        batch.num_draft_tokens = 1
    elif case == "extra_logits":
        batch.cu_num_logits_np[-1] += 1
    elif case == "wide":
        grammar.grammar_bitmask[:] = -1
    else:
        grammar.grammar_bitmask = grammar.grammar_bitmask[:, :1]
    assert _projection_token_ids(batch, grammar, 65) is None


@pytest.mark.parametrize("num_tokens", [0, 4096, 4097, 128256])
def test_projection_support_limit_preserves_dense_fallback(num_tokens):
    vocab_size = 128256
    batch = _input_batch(["a"], [0])
    batch.cu_num_logits_np = batch.cu_num_logits.numpy()
    bits = np.arange(vocab_size)[None, :] < num_tokens
    grammar = SimpleNamespace(
        structured_output_request_ids=["a"],
        grammar_bitmask=np.packbits(bits, axis=1, bitorder="little").view(np.int32),
    )
    ids = _projection_token_ids(batch, grammar, vocab_size)
    if num_tokens > 4096:
        assert ids is None
    else:
        np.testing.assert_array_equal(ids, np.arange(num_tokens))


@pytest.mark.parametrize("vocab_size", [65, 32768, 151936])
@pytest.mark.parametrize("enabled", [False, True])
def test_projection_profile_covers_the_largest_eligible_union(vocab_size, enabled):
    hidden = torch.zeros((8, 17), dtype=torch.bfloat16)
    calls = []

    def sparse(states, ids):
        assert states is hidden
        assert ids.device == hidden.device
        assert ids.dtype == torch.int64
        calls.append(ids.tolist())

    worker = StructuredOutputsWorker.__new__(StructuredOutputsWorker)
    worker.vocab_size = vocab_size
    worker._compute_sparse_logits = sparse if enabled else None
    worker.profile_sparse_logits(hidden)
    assert calls == ([list(range(min(4096, vocab_size // 8)))] if enabled else [])


@pytest.mark.parametrize(
    "case", ["narrow", "empty", "mixed", "wide", "disabled", "no_grammar"]
)
def test_projection_worker_selects_scores_and_dense_fallback(case, monkeypatch):
    from vllm.model_executor.layers import logits_processor

    # Exercise the actual projection on CPU; only platform selection and H2D
    # transport are replaced. CUDA tests check the device implementation.
    monkeypatch.setattr(logits_processor.current_platform, "is_cuda", lambda: True)
    monkeypatch.setattr(logits_processor.current_platform, "is_cpu", lambda: True)
    monkeypatch.setattr(logits_processor.current_platform, "is_rocm", lambda: False)
    monkeypatch.setattr(
        "vllm.v1.worker.gpu.structured_outputs.async_tensor_h2d",
        lambda data, *, device, dtype: torch.as_tensor(
            data, device=device, dtype=dtype
        ),
    )
    with set_current_vllm_config(VllmConfig(device_config=DeviceConfig("cpu"))):
        processor = LogitsProcessor(65, soft_cap=30.0, scale=-0.3)
    head = SimpleNamespace(
        weight=torch.arange(65 * 17, dtype=torch.float32)
        .reshape(65, 17)
        .remainder(11)
        .to(torch.bfloat16),
        quant_method=UnquantizedEmbeddingMethod(),
        cpu_linear=torch.nn.functional.linear,
        tp_size=1,
    )
    hidden = torch.ones((2, 17), dtype=torch.bfloat16)
    calls = []

    def dense(hidden):
        calls.append("dense")
        return processor(head, hidden)

    def sparse(hidden, ids):
        calls.append("sparse")
        return processor(head, hidden, allowed_token_ids=ids)

    worker = StructuredOutputsWorker.__new__(StructuredOutputsWorker)
    worker.vocab_size = 65
    worker._compute_logits = dense
    worker._compute_sparse_logits = None if case == "disabled" else sparse
    batch = _input_batch(["a", "b"], [0, 0])
    batch.cu_num_logits_np = batch.cu_num_logits.numpy()
    mask = np.zeros((2, 3), dtype=np.int32)
    mask[:, 0] = 1
    if case == "empty":
        mask[:] = 0
    elif case == "wide":
        mask[:] = -1
    grammar = SimpleNamespace(
        structured_output_request_ids=["a", "b"], grammar_bitmask=mask
    )
    if case == "mixed":
        grammar.structured_output_request_ids.pop()
        grammar.grammar_bitmask = mask[:1]
    elif case == "no_grammar":
        grammar = None
    result = worker.compute_logits(hidden, batch, grammar)
    assert result is not None
    assert calls == ["sparse" if case in ("narrow", "empty") else "dense"]
    expected = processor(head, hidden)
    if case in ("narrow", "empty"):
        forbidden = torch.ones(65, dtype=torch.bool)
        if case == "narrow":
            forbidden[0] = False
        result[:, forbidden] = expected[:, forbidden] = -float("inf")
    torch.testing.assert_close(result, expected)


@pytest.mark.parametrize(
    "case",
    [
        "cpu",
        "fp32",
        "weight_dtype",
        "head_dtype",
        "processor",
        "head",
        "tp",
        "invariant",
    ],
)
def test_projection_processor_preserves_unsupported_dense_result(case, monkeypatch):
    from vllm.model_executor.layers import logits_processor

    class CustomProcessor(LogitsProcessor):
        pass

    monkeypatch.setattr(
        logits_processor.current_platform, "is_cuda", lambda: case != "cpu"
    )
    monkeypatch.setattr("vllm.envs.VLLM_BATCH_INVARIANT", case == "invariant")
    with set_current_vllm_config(VllmConfig(device_config=DeviceConfig("cpu"))):
        processor = (CustomProcessor if case == "processor" else LogitsProcessor)(65)
    hidden = torch.zeros(
        (1, 17), dtype=torch.float32 if case == "fp32" else torch.bfloat16
    )
    head = SimpleNamespace(
        weight=torch.zeros(
            (65, 17), dtype=torch.float32 if case == "weight_dtype" else torch.bfloat16
        ),
        quant_method=object() if case == "head" else UnquantizedEmbeddingMethod(),
        tp_size=2 if case == "tp" else 1,
    )
    if case == "head_dtype":
        processor.head_dtype = torch.float32
    expected = torch.zeros((1, 65))
    monkeypatch.setattr(processor, "_get_logits", lambda *args: expected)
    assert processor(head, hidden, allowed_token_ids=torch.tensor([0])) is expected


@pytest.mark.parametrize(
    "case",
    [
        "enabled",
        "disabled",
        "tp",
        "lora",
        "spec",
        "manual_kv",
        "startup_plan",
        "invariant",
        "model",
    ],
)
def test_projection_capability_respects_engine_settings(case, monkeypatch):
    monkeypatch.setattr("vllm.envs.VLLM_BATCH_INVARIANT", case == "invariant")
    monkeypatch.setattr("vllm.envs.VLLM_ENABLE_STARTUP_PLAN", case == "startup_plan")
    callback = lambda hidden, ids: hidden
    model = (
        SimpleNamespace()
        if case == "model"
        else SimpleNamespace(compute_logits_sparse=callback)
    )
    config = SimpleNamespace(
        structured_outputs_config=SimpleNamespace(
            enable_sparse_lm_head=case != "disabled"
        ),
        parallel_config=SimpleNamespace(tensor_parallel_size=2 if case == "tp" else 1),
        lora_config=object() if case == "lora" else None,
        speculative_config=object() if case == "spec" else None,
        cache_config=SimpleNamespace(
            kv_cache_memory_bytes=1024 if case == "manual_kv" else None
        ),
    )
    assert get_sparse_logits_callback(model, config) is (
        callback if case == "enabled" else None
    )

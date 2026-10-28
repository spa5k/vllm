# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

from types import MethodType, SimpleNamespace
from typing import Any

import numpy as np
import pytest
import torch

pytest.importorskip("triton")
if not torch.cuda.is_available():
    pytest.skip(
        "CUDA required for Model Runner V2 logits processor tests",
        allow_module_level=True,
    )

from vllm.config import VllmConfig, set_current_vllm_config
from vllm.model_executor.layers.logits_processor import LogitsProcessor as HeadProcessor
from vllm.model_executor.layers.vocab_parallel_embedding import (
    UnquantizedEmbeddingMethod,
)
from vllm.platforms import current_platform
from vllm.sampling_params import SamplingParams
from vllm.v1.worker.gpu.sample.logits_processor import (
    LogitsContext,
    LogitsProcessor,
)
from vllm.v1.worker.gpu.sample.sampler import Sampler
from vllm.v1.worker.gpu.states import RequestState

DEVICE = torch.device("cuda")
VOCAB_SIZE = 128
TARGET_TOKEN = 7
BIAS = 5.0
BOOST = 100.0
TEMPERATURE = 2.0


class MockReasoningConfig:
    reasoning_start_token_ids = [90]
    reasoning_end_token_ids = [91]
    natural_reasoning_end_token_ids = [91]


class RecordingProcessor(LogitsProcessor):
    """Adds BOOST to TARGET_TOKEN and records every lifecycle callback."""

    def __init__(self, vllm_config: Any, req_state: Any):
        self.events: list[str] = []
        self.seen_logits: torch.Tensor | None = None

    def add_request(self, req_idx: int, sampling_params: SamplingParams) -> bool:
        self.events.append(f"add_request:{req_idx}")
        return True

    def apply_staged_writes(self) -> None:
        self.events.append("apply_staged_writes")

    def apply(self, logits: torch.Tensor, ctx: LogitsContext) -> torch.Tensor:
        self.events.append("apply")
        self.seen_logits = logits.clone()
        logits[:, TARGET_TOKEN] += BOOST
        return logits


def _make_sampler(processor: RecordingProcessor) -> Sampler:
    req_states = RequestState(
        max_num_reqs=4,
        max_model_len=64,
        max_num_batched_tokens=16,
        num_speculative_steps=1,
        vocab_size=VOCAB_SIZE,
        device=DEVICE,
    )
    return Sampler(
        vllm_config=SimpleNamespace(reasoning_config=MockReasoningConfig()),
        max_num_reqs=4,
        vocab_size=VOCAB_SIZE,
        device=DEVICE,
        req_states=req_states,
        custom_logits_processors=[processor],
    )


def test_custom_processor_lifecycle_and_pipeline_position():
    """A custom processor's hooks fire in order, it runs after the built-in
    bias stage, and before temperature scaling."""
    proc = RecordingProcessor(None, None)
    sampler = _make_sampler(proc)
    sampler.add_request(
        0,
        SamplingParams(logit_bias={TARGET_TOKEN: BIAS}, temperature=TEMPERATURE),
    )
    sampler.apply_staged_writes()

    num_reqs = 1
    idx_mapping = torch.arange(num_reqs, dtype=torch.int32, device=DEVICE)
    raw = torch.zeros(num_reqs, VOCAB_SIZE, device=DEVICE)
    out = sampler.apply_sampling_params(
        raw,
        expanded_idx_mapping=idx_mapping,
        idx_mapping=idx_mapping,
        idx_mapping_np=np.arange(num_reqs, dtype=np.intp),
        pos=torch.zeros(num_reqs, dtype=torch.int32, device=DEVICE),
        input_ids=torch.zeros(num_reqs, dtype=torch.int32, device=DEVICE),
        expanded_local_pos=torch.zeros(num_reqs, dtype=torch.int32, device=DEVICE),
        seq_lens_upper_bound_np=np.ones(num_reqs, dtype=np.int64),
    )

    assert proc.events == [
        "add_request:0",
        "apply_staged_writes",
        "apply",
    ]
    # The processor sees the built-in bias applied but no temperature scaling.
    assert proc.seen_logits is not None
    assert proc.seen_logits[0, TARGET_TOKEN].item() == BIAS
    # Its own modification is then temperature-scaled by the sampler.
    assert out[0, TARGET_TOKEN].item() == (BIAS + BOOST) / TEMPERATURE


@pytest.mark.skipif(not current_platform.is_cuda(), reason="Sparse head requires CUDA")
@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16])
@pytest.mark.parametrize("batch_size", [1, 4, 16])
@pytest.mark.parametrize("soft_cap,scale", [(None, 1.0), (30.0, -0.3), (30.0, 0.0)])
def test_sparse_head_preserves_legal_scores_after_grammar(
    dtype, batch_size, soft_cap, scale
):
    with set_current_vllm_config(VllmConfig()):
        processor = HeadProcessor(257, soft_cap=soft_cap, scale=scale)
    generator = torch.Generator(device=DEVICE).manual_seed(17853)
    hidden = torch.randn(
        (batch_size, 65), device=DEVICE, dtype=dtype, generator=generator
    )
    head = SimpleNamespace(
        weight=torch.randn((264, 65), device=DEVICE, dtype=dtype, generator=generator),
        quant_method=UnquantizedEmbeddingMethod(),
        tp_size=1,
    )
    bias = torch.randn((264,), device=DEVICE, dtype=dtype, generator=generator)
    ids = torch.tensor([0, 1, 31, 32, 64, 256], device=DEVICE)
    forbidden = torch.ones(257, device=DEVICE, dtype=torch.bool)
    forbidden[ids] = False
    previous_precision = torch.get_float32_matmul_precision()
    try:
        torch.set_float32_matmul_precision("highest")
        for _ in range(2):
            dense = processor(head, hidden, bias)
            sparse = processor(head, hidden, bias, allowed_token_ids=ids)
            if soft_cap is None:
                assert torch.isneginf(sparse[:, forbidden]).all()
            # The ordinary grammar mask runs after softcap and scale.
            dense[:, forbidden] = -float("inf")
            sparse[:, forbidden] = -float("inf")
            torch.testing.assert_close(sparse, dense, rtol=0.01, atol=0.03)
            assert torch.equal(sparse.argmax(-1), dense.argmax(-1))
            head.weight[ids] += 0.5
    finally:
        torch.set_float32_matmul_precision(previous_precision)


@pytest.mark.skipif(not current_platform.is_cuda(), reason="Sparse head requires CUDA")
@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16])
@pytest.mark.parametrize("with_bias", [False, True])
def test_sparse_head_keeps_precision_when_large_terms_cancel(dtype, with_bias):
    with set_current_vllm_config(VllmConfig()):
        processor = HeadProcessor(257)
    generator = torch.Generator(device=DEVICE).manual_seed(17853)
    hidden = (
        torch.randint(-8, 9, (4, 2560), device=DEVICE, generator=generator).to(dtype)
        / 8
    )
    weight = (
        torch.randint(-8, 9, (264, 2560), device=DEVICE, generator=generator).to(dtype)
        / 8
    )
    ids = torch.arange(0, 256, 8, device=DEVICE)
    ids[-1] = 256
    expected = hidden.double() @ weight[ids].double().T
    bias = None
    if with_bias:
        bias = torch.zeros(264, device=DEVICE, dtype=dtype)
        bias[ids] = -expected[0].to(dtype)
        bias[ids[-1]] += 32
        expected += bias[ids].double()
    head = SimpleNamespace(
        weight=weight, quant_method=UnquantizedEmbeddingMethod(), tp_size=1
    )
    previous_precision = torch.get_float32_matmul_precision()
    try:
        torch.set_float32_matmul_precision("highest")
        actual = processor(head, hidden, bias, allowed_token_ids=ids)
    finally:
        torch.set_float32_matmul_precision(previous_precision)
    # Binary fractions keep this reference sum exactly representable in FP32.
    torch.testing.assert_close(actual[:, ids], expected.to(dtype), rtol=0, atol=0)
    assert actual.dtype == dtype
    assert torch.equal(actual[:, ids].argmax(-1), expected.to(dtype).argmax(-1))
    if with_bias:
        assert actual[0].argmax() == ids[-1]


@pytest.mark.skipif(not current_platform.is_cuda(), reason="Sparse head requires CUDA")
@pytest.mark.parametrize(
    "unsupported",
    [
        "fp32_head",
        "custom_processor",
        "invariant",
        "high",
        "medium",
        "precision_conflict",
        "tf32_override",
        "autocast",
    ],
)
def test_sparse_head_keeps_the_dense_path_when_unsupported(unsupported, monkeypatch):
    class CustomProcessor(HeadProcessor):
        pass

    with set_current_vllm_config(VllmConfig()):
        processor_cls = (
            CustomProcessor if unsupported == "custom_processor" else HeadProcessor
        )
        processor = processor_cls(65)
    head = SimpleNamespace(
        weight=torch.zeros((65, 17), device=DEVICE, dtype=torch.bfloat16),
        quant_method=UnquantizedEmbeddingMethod(),
        tp_size=1,
    )
    if unsupported == "fp32_head":
        processor.head_dtype = torch.float32
    elif unsupported == "invariant":
        monkeypatch.setattr("vllm.envs.VLLM_BATCH_INVARIANT", True)
    elif unsupported in ("high", "medium"):
        monkeypatch.setattr(torch, "get_float32_matmul_precision", lambda: unsupported)
    elif unsupported == "precision_conflict":

        def conflicting_precision():
            raise RuntimeError("Incompatible precision settings")

        monkeypatch.setattr(
            torch, "get_float32_matmul_precision", conflicting_precision
        )
    elif unsupported == "tf32_override":
        monkeypatch.setenv("TORCH_ALLOW_TF32_CUBLAS_OVERRIDE", "1")
    elif unsupported == "autocast":
        monkeypatch.setattr(torch, "is_autocast_enabled", lambda device: True)
    expected = torch.full((1, 65), 3.0, device=DEVICE)
    monkeypatch.setattr(processor, "_get_logits", lambda *args: expected)
    result = processor(
        head, head.weight[:1], allowed_token_ids=torch.tensor([1], device=DEVICE)
    )
    assert result is expected


@pytest.mark.skipif(not current_platform.is_cuda(), reason="Sparse head requires CUDA")
@pytest.mark.parametrize("family", ["llama", "qwen3"])
@pytest.mark.parametrize("override", [None, "compute_logits", "processor"])
def test_sparse_model_capability_preserves_custom_logits(family, override):
    from vllm.model_executor.models.llama import LlamaForCausalLM
    from vllm.model_executor.models.qwen3 import Qwen3ForCausalLM

    model_class = LlamaForCausalLM if family == "llama" else Qwen3ForCausalLM
    with set_current_vllm_config(VllmConfig()):
        processor = HeadProcessor(65)
    expected = torch.full((1, 65), 3.0, device=DEVICE)
    model = SimpleNamespace(
        logits_processor=processor,
        lm_head=SimpleNamespace(
            weight=torch.ones((128, 17), device=DEVICE, dtype=torch.bfloat16),
            quant_method=UnquantizedEmbeddingMethod(),
            tp_size=1,
        ),
    )
    method = model_class.compute_logits
    if override == "compute_logits":
        method = lambda self, hidden: expected
    elif override == "processor":
        model.logits_processor = lambda head, hidden: expected
    model.compute_logits = MethodType(method, model)
    hidden = torch.ones((1, 17), device=DEVICE, dtype=torch.bfloat16)
    ids = torch.tensor([1], device=DEVICE)
    result = model_class.compute_logits_sparse(model, hidden, ids)
    assert result is not None
    if override is not None:
        assert result is expected
    else:
        assert result.shape == model.compute_logits(hidden).shape
        assert result[0, 1] == 17
        result[:, ids] = -float("inf")
        assert torch.isneginf(result).all()

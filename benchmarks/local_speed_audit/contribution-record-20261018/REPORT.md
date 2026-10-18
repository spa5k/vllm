# vLLM contribution research record

Recorded on 18 October 2026. This report covers the research saved through
12:40 UTC. Further work belongs to the deep-fix phase described in
[NEXT_PHASE.md](NEXT_PHASE.md).

This is a research record. The patch files are review drafts. No upstream PR,
issue, comment or review was created. Human changed-line review and the missing
validation below are still required before submission.

## Main findings

Three correctness changes have actual original/candidate evidence. One pooling
optimization has native GPU component measurements and trained-model pooling
output checks. One MRV2 optimization has source review only.

| Priority | Finding | Strongest evidence | Main open condition |
| --- | --- | --- | --- |
| 1 | ARM GPT-OSS W4A8 gate/up layout | Native numerical failure becomes a pass; official ARM suite passes 169 tests | Trained GPT-OSS and reporter-format validation |
| 2 | Responses output allowance resets across built-in-tool turns | Real ASGI/Harmony JSON/SSE original/candidate pair; compact candidate suite passes 18 cases | Real model/tool evaluation and adjacent PR coordination |
| 3 | Offline prompt-embedding dtype is absent from the prefix-cache key | Real manager changes from a wrong 32-token hit to no hit; nine candidate suite cases pass | Public worker/model path and cache compatibility validation |
| 4 | Direct segmented mean pooling | 84 correctness cases, L4 component timing and three trained MiniLM pooling outputs | Actual vLLM worker dispatch, model throughput and PR coordination |
| 5 | MRV2 table/slot preparation fusion | Independent source review of dirty-row clearing and draft-consumer seed | Native device, model and performance checks |

The short size of a fix does not measure its effect. The next phase will seek
defects whose cause spans module boundaries. It will not add files to increase
the apparent size of a change.

## Source pins and evidence limits

The main test runtime is upstream
[837e87e1](https://github.com/vllm-project/vllm/commit/837e87e1c5024843b66383ef1bd60ca5672a9575).
The latest reviewed main in this report is
[072c0886](https://github.com/vllm-project/vllm/commit/072c0886d53d933a7e1d3da7e8a3a91670cf181d).

Four complete drafts were applied in memory to eleven exact source preimages at
953fa442. Complete comparisons through 49466394 and 072c0886 change none of those
preimages. This proves selected patch applicability. It does not prove that a
current-main build or runtime passed. CMake, Docker and configuration changes
outside those preimages prevent that broader claim.

The four-draft check covers ARM, Responses, prompt dtype and prompt width.
MeanPool and MRV2 are outside that check.

The report worktree also passes `git apply --check` for each of the four drafts
at 072c0886. The drafts remain patch artifacts. No production change is applied
in that worktree, and this check runs no production tests.

TraceDecay graph coverage was stale, unavailable or deadline-limited for the
selected current-source questions. The new deep-phase context request also
timed out. No empty graph result was treated as absence of code or callers.
Context7 reached its quota in the retained research evidence. Where current
documentation was needed, the research saved exact official-source fallbacks.

The local research archive contains the full raw outputs, source snapshots and
immutable manifests. This Git record contains compact evidence descriptions and
drafts. It excludes model data, wheels, environments and large runtime trees.
[evidence-index.json](evidence-index.json) gives the source paths, complete
identities and saved commands. Its archive paths refer to the retained local
scout directory. They are not files bundled in this report.

## 1. ARM GPT-OSS W4A8 activation layout

### Problem and cause

GPT-OSS SWIGLUOAI uses alternating gate and up rows:

```text
gate0, up0, gate1, up1, ...
```

The loader transpose and INT4 packing preserve this order. The native ARM MoE
operator treated the output as two contiguous halves. It therefore paired the
wrong gate and up values.

For example, an output `[2, 3, 5, 7]` represents gates `[2, 5]` and ups
`[3, 7]`. The original split instead used gates `[2, 3]` and ups `[5, 7]`.

### Draft change

The native kind-1 activation branch selects alternating columns. Other
activation kinds keep their existing half split. Quantization, packed weights,
the GPT-OSS clamp and alpha, the down projection and routing accumulation stay
outside the change.

The draft also extends the existing CPU INT4 MoE test and its reference helper.
It corrects reference bias placement after matrix multiplication. It preserves
the existing SILU defaults.

The exact changed paths are recorded in the evidence index. The primary draft
changes one production C++ file and one existing test file.

### Observed results

| Check | Original | Candidate |
| --- | --- | --- |
| Targeted pytest against public native operator | 35 of 1,024 values exceed the existing tolerance; maximum absolute error 0.03759765625 | Pass |
| Existing SILU controls in the same pair | Two pass | Two pass |
| Official ARM source-tree build and normal test file | Separate original proof above | 169 tests pass |
| Synthetic checkpoint through DefaultModelLoader and CPUExpertsInt4.apply | Not the paired direct case | Pass with two distinct experts |

The tolerance is `atol=rtol=0.02`. The synthetic loader/native case is separate
evidence. Its maximum absolute error is 0.03125; the relative allowance also
applies. Its error is a separate observation from the public-op pytest pair.

The official build loads native extension SHA256
`acf122dde16999627ff616ba9c1d671968d372c9ea79697e8a593a4a96a91ee2`.
All three normal conftests load. The official test result has no skip, failure
or error. It validates this component build and test file, not a full wheel,
editable install or all CPU tests.

### Ownership and remaining work

[Issue 59457](https://github.com/vllm-project/vllm/issues/59457) was open and
unassigned in the saved ownership review.
[PR 61593](https://github.com/vllm-project/vllm/pull/61593) adds another activation
in the same native file. Its saved scope differs, but integration needs review.

The reporter's generated checkpoint format and a trained GPT-OSS output
evaluation remain missing. The synthetic checkpoint is not evidence that the
reporter's compression recipe works. No model-quality or throughput gain is
claimed.

Draft: [arm-w4a8.patch](patches/arm-w4a8.patch).

## 2. Responses cumulative output allowance

### Problem and cause

A Responses request can make several engine calls while the server executes
built-in tools. The original loop restores the request's output cap on each
follow-up. It does not subtract output already generated for that response.

For example, an effective cap of 62 and 38 generated tokens should leave 24.
The original loop can give the next engine call another 62.

The official Responses contract defines a response-wide upper bound that also
includes reasoning tokens. Tool result text is later prompt input. It does not
consume this output allowance.

### Draft change

The draft keeps the initial effective sampling cap separate from each turn's
remaining cap. It uses the accumulated output counter in both Harmony and
Parsable paths. It stops before another tool or engine call if no allowance
remains. It does not start an engine call with `max_tokens=0`.

A context flag distinguishes exhausted pending tool work from a natural final
answer that ends exactly at the cap. The final response becomes incomplete
with reason `max_output_tokens` when that pending work cannot continue.
The outer sampling object retains the original effective cap for the public
response field. The local minimum token setting is clamped to the remaining
maximum.

This is a coordinated three-file draft: response context, response serving and
the existing serving test file.

### Observed results

| Validation | Result |
| --- | --- |
| Original real ASGI/Harmony JSON/SSE pair | Six intended budget failures; two natural-final controls pass |
| Candidate with the same HTTP cases | Eight pass |
| Compact candidate selection with normal conftests | 18 pass; no failures, errors or skips |
| Static format successor | Production diff stays equal; test ASTs and comments stay equal; format checks pass |

The HTTP cases use the real ASGI route, request/response serialization,
Harmony parsing and JSON/SSE finalization. The engine, tokenizer and tool
sessions are scripted. No real model, external tool server or network server
is proved by these tests.

The 18-case run is candidate-only. The separate eight-case HTTP pair supplies
the original/candidate comparison. The final format-corrected draft has static
equivalence evidence; its formatting successor was not rerun.

### Ownership and remaining work

The bounded reviewed set contained no exact cumulative output-cap fix.
Three open PRs touch adjacent surfaces:
[47112](https://github.com/vllm-project/vllm/pull/47112) changes tool-call count,
[54064](https://github.com/vllm-project/vllm/pull/54064) changes usage/finalization,
and [58018](https://github.com/vllm-project/vllm/pull/58018) changes item lifecycle.
Their exact saved heads and patches need reconciliation before submission.

Run a supported real model with reasoning and built-in-tool follow-ups.
Check cumulative usage, cap exhaustion, natural completion, JSON/SSE terminal
events and tool-session closure. Full applicable hooks remain.

Draft: [responses-output-budget.patch](patches/responses-output-budget.patch).

## 3. Offline prompt-embedding cache identity

### Problem and cause

Two tensors can have equal shapes and identical bytes but different numerical
values because their dtypes differ. The original offline prompt-embedding
cache digest does not include dtype.

The fixed witness repeats word `0x3c00`. It represents FP16 1.0 and BF16
0.0078125. Both tensors have shape 33 by 64 and identical bytes. A reused
prefix based only on those bytes can identify different embeddings as equal.

### Draft change

The digest includes the dtype name and a zero-byte separator before the tensor
bytes. Existing same-dtype reuse remains valid. The draft updates the shared
hashing path and the relevant existing tests.

The public HTTP loader normalizes dtype. The evidence concerns the supported
offline embedding input path.

### Observed results

| Check | Original | Candidate |
| --- | --- | --- |
| Real manager cross-dtype lookup | Wrong 32-token prefix hit | Zero-token hit |
| Same-dtype lookup, sha256 and sha256_cbor | Valid 32-token reuse | Valid 32-token reuse |
| Selected normal-suite cases | Two intended failures; seven controls pass | Nine pass |

The 33-token request allocates all 33 tokens. Its two complete prefix blocks
supply the 32 reusable tokens. No actual KV tensor contents or model output
was checked.

Affected embedding cache keys and reviewed offload file names change.
Event field shapes stay unchanged. This is source compatibility analysis,
not a live rolling-upgrade, cross-version store or model result.

### Failed public-worker follow-up

The input and CPU Torch stages finish in the saved worker-import attempt.
A research hook then rejects a cpuinfo/platform helper's process launch.
An earlier rejected socket bind has no retained caller. The target exits
without OOM and its exact container is removed.

This is an environment or research-policy failure. It is not a vLLM bug
reproduction, CPUWorker import pass or model test. No denial exemption was
added.

### Ownership and remaining work

[PR 56656](https://github.com/vllm-project/vllm/pull/56656) changes a different
mask issue in the same helper.
[PR 53769](https://github.com/vllm-project/vllm/pull/53769) adds broader
conformance tests. Coordinate those surfaces.

A permitted public worker/model path and live cache compatibility checks remain.
Draft: [prompt-embedding-dtype.patch](patches/prompt-embedding-dtype.patch).

## 4. Direct segmented mean pooling

The candidate reduces intermediate work by pooling token segments directly.
The accepted component evidence includes 84 correctness cases and 16 cold-L2
L4 timing rows. Separate warm BF16 cases and trained MiniLM outputs add narrower
checks.

| Measurement scope | Saved result |
| --- | --- |
| Cold-L2 isolated component timing | 2.88–6.93 times faster |
| Six warm BF16 component shapes | 4.18–33.51 times faster |
| Three trained MiniLM pooled outputs | Maximum error 5.96e-8; minimum cosine 0.9999999404 |

The timing scopes differ. These values are not vLLM model-throughput gains.
The trained pooling check does not prove dispatch through an actual vLLM
worker.

[PR 60035](https://github.com/vllm-project/vllm/pull/60035) overlaps the area.
Coordination, native worker dispatch and a complete model benchmark remain.
The evidence index records the retained candidate location. No performance PR
is ready from the component measurements alone.

## 5. MRV2 table and slot preparation fusion

The retained fusion design combines table/slot preparation. A current adjacent
change adds prior-dirty-row clearing and draft-consumer state. An older fusion
draft omitted part of that state and is rejected.

The corrected source draft restores the eight-row draft-consumer seed and
retains the current dirty-row behavior. Independent source review accepts that
narrow correction.

This has no native device correctness, model output or performance result.
It is fifth in the record because its evidence is weaker than the other
ranked work. [PR 60767](https://github.com/vllm-project/vllm/pull/60767) is an
integration and ownership boundary. The evidence index identifies the retained
source draft. No speed claim or ready-to-submit fix follows.

## Other useful findings that remain held

| Lead | Evidence | Why it is held |
| --- | --- | --- |
| Direct offline prompt-embedding width | Source and draft-validator review; direct path can omit the serialized-path width rule | Renderer collection stopped at a denied cpuinfo import; all four direct and four serialized cases remain unrun |
| Mixed CUDA architecture targets | Eleven real CMake helper observations; independent saved-result review; NVIDIA compatibility documentation | Same source-removal cause as active PR56582; no generated cubin or device-loading test |
| Tiny-logit top-k stop | Two independent scalar FP32 models retain one token where exact top-2 retains two | Native Triton/compiler behavior is untested; PR59804 overlaps shared mask/tie code |
| PLE ngram state after prefix return | Retained source mechanism survives merged PR61454 | Reporter fixes and ownership coordination remain; no native AMD/model proof |
| Saved scoring template versus per-call override | Constructor can fail before a per-call template arrives | Recovery from malformed checkpoint metadata is not an established supported contract |

The width draft is
[prompt-embedding-width.patch](patches/prompt-embedding-width.patch).
Width one can broadcast in MRV1. Logical indexing evidence in MRV2 does not
prove a physical out-of-bounds CUDA access.

For the CMake case, source `10.0` and targets `10.0a;10.3a` return only
`10.0a`. The isolated target calls return `10.0a` and `10.0`.
NVIDIA documents baseline sm_100 compatibility with later minor capability
10.3; sm_100a is exact 10.0 only. This supports the missing fallback argument.
It does not measure a failing wheel on a device. The eleven checks assert
current outputs, not a candidate fix. Keep this as new-case evidence for the
existing owner.

For sampling, the witness is one FP32 row of vocabulary size 1024. Four finite
values are approximately `[0, 1e-12, 2e-12, 1e-10]`; the rest are `-inf`.
With k=2, p=None and temperature 1, the reference retains indices 2 and 3.
Each scalar source model retains only index 3 after an absolute 1e-9 stop.
The three positive values are normal FP32 values. They are distinct.
This is separate from underflow and tied maxima. A future native check must
force the monolithic filter and use the existing top-k test suite.

External corrections preserve the original sealed reports. The four-value
unmasked sampling row also exhibits the scalar counterexample. A CMake
source-list threshold is compiler 13.4, not 13.1. Neither correction changes
the saved full-13.0 CMake case.

## Rejected work and useful negative results

The research rejected active duplicate fixes before making parallel patches.
Examples include:

- Administrative abort conversion: PR57089 owns the fix for issue57082.
- Background Responses termination: PR49721 owns the selected fix.
- Built-in tool-count enforcement: PR47112 owns it.
- All-masked sampling: PR58101 and PR59144 cover the selected issue.
- Standalone top-p overflow: PR60104 owns the selected fix.
- Video source-FPS guard: PR62261 covers issue62260.
- Tool argument and escaping reports have current owners, including PR62259
  and PR62271.

Other selected audits found no supported counterexample:

- Packed Llama rotary layouts retain separate Q/K token strides and head counts.
- Chat cancellation of a pending read aborts its own internal request.
- The inspected INT8 callers flatten rank-three tensors or pass expert slices.
- Empty completion and embedding inputs reach existing validation.
- Embedding dimensions already reach the relevant checks.
- Failed remote-KV receive and common abort orders release target state under
  the documented completion-marker contract.
- The selected structured-output admission/abort paths clean up their normal
  request state. Native compilation lifetime is a separate, already owned area.

These are scoped source, arithmetic or synthetic-method negatives. They are
not proof that an entire backend or server has no bugs. Complete issue comments,
issue-linked open PR searches and area searches are saved where a candidate
was considered. Keyword searches do not prove global absence of duplicate work.

## Validation infrastructure, cost and storage

Many validation attempts stopped before the intended test. Saved failures
include missing generated interfaces, provider metadata mismatches, offline
model-path gaps, import/process guard denials and harness result predicates.
Their reservations and raw results remain recorded. They are not counted as
successful vLLM tests.

The shared compute ceiling remains USD10 across both research phases.
The guarded ledger total at this report checkpoint is USD2.9192748.
This is a conservative accounting value, not an invoice or account balance.
No new paid compute was used in the last source/CMake batch.

The last saved cloud inventory covers 26 exact owned Modal apps, all stopped
with zero tasks at its recorded historical timestamp. It is not a fresh
inventory from this reporting step. The last renderer container was removed
and three complete absence observations passed. No other chat's resources
were changed.

New paid work remains blocked by the existing controller ownership review.
Every later paid launch must use `control/run_bounded.py`, a reviewed exact
manifest and a locked full worst-case reservation. This report gives no new
launch authority.

SSD free space at the 12:40 checkpoint is 82,161,754,112 bytes.
The policy retains at least 20 GiB after an 8 GiB conservative local peak.
Earlier owned duplicate payloads were converted to APFS copy-on-write storage,
with byte, mode and mtime checks. No model, source evidence or other chat's data
was deleted to make this report.

## Drafts and use of this record

| Bundled draft | SHA256 | Status |
| --- | --- | --- |
| ARM W4A8 | `6df2e88a4956c998c6319cf4cbf3ab2dd80cf177b3902d57ca039fac9e114e79` | Actual component tests; trained-model validation missing |
| Responses | `d4bdc319f2b89281c4a2b77acf85aab5b613fe6fdf9cf5735529100252f77027` | Tested production change; final test-format successor has static equivalence only |
| Prompt dtype | `f7359d31d5cb59986725de1dc0f3a5c996df64f67e3055cc85d1ca0ae910551e` | Real manager and suite evidence; worker/model path missing |
| Prompt width | `c34bbbfd4504ab50c496407cabada390d321bead94fee7c8fcb450c004b1c5e8` | Source review only; renderer assertions unrun |

Do not apply all drafts as one production change. They address different
problems and have different ownership and validation conditions.

For a recording, use the cause, before/after example and result table for each
finding. State the evidence level with the result. For submission, refresh the
exact upstream source and duplicate checks, review every changed line, run
relevant tests and model evaluations, and run the vLLM PR checklist. State the
AI assistance used.

The next phase is recorded in [NEXT_PHASE.md](NEXT_PHASE.md).

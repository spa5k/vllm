# Dynamic adapter lifetime audit

Decision: **REJECT_ACTIVE_OWNER_OVERLAP**. This batch found no new unowned contribution. No patch or runtime action follows.

The primary main receipt is `ff01a6b14f329ccd4162fce309913542e2abcd5b`, committed at `2026-10-18T16:49:42Z`. Fifteen named current source and documentation files are pinned in `source-identities.json`. API bytes, lengths and Git blob SHA1 values were checked before AST parsing. The source was not imported or executed.

## LoRA contract and real path

The current public documentation describes dynamic load and unload endpoints. It also describes `load_inplace=True` replacement under the same name, including use during ongoing inference. The endpoint is gated by `VLLM_ALLOW_RUNTIME_LORA_UPDATING`, and its router warns that it is for local development. It is incorrect to reject every in-place use as an unsupported mutation. This audit does not assume that arbitrary concurrent calls or weight-file mutation are supported.

The pinned route is `api_router` → `OpenAIServingModels.load_lora_adapter` → `AsyncLLM.add_lora` → `AsyncMPClient.add_lora_async` utility → `EngineCore.add_lora` → executor/worker → `LoRAModelRunnerMixin` → worker adapter manager. The manager's actual add/activation bodies and the named existing endpoint test were read. The executor utility failure path is prior owned work; it is not a new defect here.

The source shows two substantive gaps, both already owned:

- Unload holds the same-name resolver lock and deletes the frontend registry row. It makes no engine removal call. [Issue #54839](https://github.com/vllm-project/vllm/issues/54839) and its complete one-comment response discuss this exact boundary. Open [#54939](https://github.com/vllm-project/vllm/pull/54939), head `6d40336cc15a3639905a6d92e4f891a29d1b386c`, adds that call and error handling. Its three changed-file patches were read. The issue comment also raises the live-request ownership question. Do not carve a competing unload-lifetime patch out of that discussion.
- `LoRAModelManager.activate_adapter` writes active-ID and slot metadata before layer copies can fail. Open [#61618](https://github.com/vllm-project/vllm/pull/61618), head `73be6d45dcc0a15e93edb882ad272d2478f5399a`, moves these exact two writes after successful loading. Its complete one-file patch was read. Its reported CPU/GPU results belong to that PR. They were not run in this task.

The load path holds a same-name lock and commits its frontend registry after the awaited engine add. This is not a transaction across all workers. This packet does not prove a new supported cancellation schedule or partial-RPC recovery case. Such a claim needs an actual public caller cancellation path and a clear engine acknowledgement/ownership contract. The old collective-RPC and utility-future work cannot be relabelled as a new adapter defect. Prefix-cache replacement PR #48352 is adjacent excluded work from the saved frontier; this task did not review or reopen its implementation.

The current endpoint test uses a mocked EngineClient. Its unload success check covers the frontend registry, not physical worker cleanup. That gap is already part of #54939. No new test patch is proposed.

## One documented switch: worker memory profiling

Because the adapter boundaries were owned, I checked one other resource lifetime boundary: device-wide memory samples while a co-tenant releases allocations during worker startup. Current `CacheConfig` documents a per-instance memory fraction and multiple instances on one GPU. This does not itself prove every dynamic interference pattern safe.

[Issue #56830](https://github.com/vllm-project/vllm/issues/56830) supplies the supported co-tenant/host-release report. All three comments were read. They link the direct open fix [#55828](https://github.com/vllm-project/vllm/pull/55828), head `0f1b2a70f5c501bb94c6d90757828b82ac8ff732`. Its complete five-file patch changes the same process/device accounting and the worker assertion. Area results also contain [#45534](https://github.com/vllm-project/vllm/pull/45534), head `0d42366df653f0fa49a5217ae8084ff2faec28fe`, with an opt-in approach. Its complete three-file patch was read. These are ownership evidence, not an endorsement of either repair.

The exact current source derives total consumed memory from the decrease in device-wide free memory. On the non-ROCm path it requires final free memory to be no greater than initial free memory. The own integer control uses 10 GiB initial free memory, 2 GiB own growth, and a co-tenant that releases 3 GiB. Final free memory is 11 GiB; the ordering predicate fails. Quiet and co-tenant-growth controls pass that predicate. This is integer accounting only. It did not allocate memory, sample a device, execute a worker or reproduce startup. Reporter native observations remain reporter evidence. The direct owner already covers this mechanism, so no competing patch is justified.

## Coverage and limits

The narrow LoRA unload issue query returned all eight rows; its open PR query returned all eleven rows. The broader replacement and memory area queries returned all 95 and 94 rows with `incomplete_results=false`. Query completeness is limited to those keywords. It does not prove global absence of other owners. A preliminary profiler/worker search returned only 30/74 rows. It was not used to select or clear a defect.

`source_data.py` is this agent's own standard-library data checker. It ran once and passed at native `c06b19`. It checks the named blobs, public source path, comments and exact PR file rows, then evaluates three inert memory-accounting rows. It does not execute subject methods or author checks. Fifteen source files are not fifteen runtime scenarios.

The saved native return objects are an explicitly labelled composition. API response bodies are retained under `raw/`. No source tree or environment was copied. Named primary source captures are evidence only. No target import, thread, process fixture, pytest, native body, Docker, Modal, model, dependency install, device or paid action ran. No active controls, ledgers, holds, shared source or peers' packets changed. TraceDecay guidance from the preceding task still applies: current named source is authoritative; the stale index is not evidence of caller absence. The retained Context7 quota limit was not retried for this source-review task.


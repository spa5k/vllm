# vLLM and NVIDIA Dynamo: consolidated research report

**Period covered: 6–18 October 2026, India time.**

This report joins the three linked chats, their saved experiments and the final
vLLM contribution report from this chat. The requested period was about two
weeks. The earliest linked chat starts on 6 October in India time. There is no
claim of complete coverage for 4–5 October or of work that was never recorded.

This is a record of completed work. It does not restart research. Both finite
research schedules were read as **PAUSED** on 18 October. No goal, test, build,
model run, paid job, public post or source-code change was started to make this
report. Two agents read old records for this consolidation.

## 1. Main results

The strongest new model performance result is the experimental vLLM grammar
output head: **8.2–8.9% less complete offline request time** on three tested
narrow-grammar Qwen3-4B workloads. It is off by default and has strict support
limits. The result is not a general serving speedup. Other useful work includes
startup-memory safety, bounded checkpoint retention, TCP admission ownership,
KV rejection cleanup, native ARM quantization correctness and planner metadata
consistency. Their evidence levels differ.

The 10–15 October experiments also produced native table/slot fusion gains,
4 MiB less FP8 fallback scratch in a tested shape, compact MoE warmup routes,
PCP counting and MLA allocation/correctness results. The 17–18 October search
added ARM quantization, cache-dtype, Responses budget and pooling findings;
three vLLM lifecycle drafts; and Dynamo metadata, planner, session, broker and
SDK observations. Sections 4–9 record these results, not only the public PRs.
The [HTML edition](report.html#findings) displays the dated research sections
before the public contribution ledger. The sections are open by default.

The delivered public outcome is **four merged upstream PRs** in the reviewed
set: one in vLLM and three in Dynamo. Another **eight PRs remain open**. Three
reviewed PRs are closed without a merge. These states were checked directly
through GitHub on 18 October at about 23:02–23:03 India time. The exact heads,
check results and timestamps are saved in [public-pr-state.json](public-pr-state.json).

Several large component improvements did not become useful model improvements.
The clearest example is n-gram graph replay: strong isolated proposer gains,
but no gain on the later Qwen3-4B full-generation test. That PR remains held.
Negative results and closed leads are part of the outcome, not missing work.

## 2. Sources and evidence rules

| Chat | Role in this report |
| --- | --- |
| [Investigate vLLM startup speed](codex://threads/01a10de3-8988-7c21-bc84-1de88f53a7aa) | Startup, loading, CPU work, public vLLM PRs and the later core/kernel validation. Starts 6 October India time. |
| [dynamo](codex://threads/01a11fa5-feee-7600-8c33-4583643552d3) | Dynamo frontend/runtime/router work, public PRs, and later cross-project GPU work. Starts 10 October India time. |
| [Research Dynamo contributions](codex://threads/01a149d4-7366-7500-8720-f9ea53d2a6f6) | The 17–18 October native Dynamo findings and deeper implementation phase. |
| Current vLLM contribution chat | The 17–18 October vLLM search, native checks, draft branches and final stop record. |

Large chat turns exceeded the history tool's limits at first. Smaller reads and
saved reports supplied the results below. TraceDecay returned partial session
coverage for one search and refused another bounded search. Neither result was
treated as proof that other work did not exist. [thread-coverage.json](thread-coverage.json)
records the selected message IDs, timestamps, coverage and fallback limits.

This report uses four separate kinds of evidence:

- **Normal project tests:** the selected installed project suite ran with its
  normal imports and fixtures, within the stated environment.
- **Native component tests:** real CPU/GPU/native library code ran, sometimes
  with selected source overlays or a narrow build. This is not a full product.
- **Full-model checks:** a real or synthetic model ran. A synthetic model does
  not establish trained-model quality. Offline generation is not HTTP serving.
- **Source or mocked checks:** useful contract evidence. These do not establish
  a device result, real transport delivery or production performance.

Test totals from overlapping suites, repeated campaigns and successive patch
versions are not added. Component percentages are not model percentages.
Requested allocation bytes are not RSS. Reservations and cost estimates are
not invoices or remaining credit balances. NVIDIA Dynamo and the PyTorch
TorchDynamo compiler are different systems.

### Recorded sequence

| India date | Main work |
| --- | --- |
| 6–8 October | Startup-plan safety, bounded PT loading, detokenization and logging CPU work. Two-H100 startup, compiler and BF16/FP8 profiling. |
| 9–10 October | Dynamo frontend/runtime/router submissions. Native CPU correctness, performance tradeoffs and duplicate checks. vLLM core candidates and native follow-up. |
| 12–13 October | Refresh public branches against main. Review-driven changes. Dynamo dispatch and sparse-eligibility PRs merge. Legacy KVBM submissions close. |
| 14 October | Native TCP admission and expiry fixes. Approximate-LRU follow-up. Core GPU checks. Complete codec ingress confirms allocation savings but weak latency value. |
| 15 October | Final fusion/FP8 validation. Grammar and MLA model checks. Larger-model n-gram rejection. Separate TRT-LLM and SGLang studies. Dynamo prefill PR merges. |
| 17–18 October | New vLLM and Dynamo contribution searches. Native observations, deeper lifecycle and metadata patches, profiler implementation and blocked gates. Final stop records. |
| 18 October, this report | Read old evidence. Check public PR states. Join the records. No research resumed. |

## 3. Public contribution ledger

### vLLM

| PR | Current state | Head | Merge or close time (UTC) |
| --- | --- | --- | --- |
| [#60143: [Bugfix] Invalidate startup plans on GPU budget changes](https://github.com/vllm-project/vllm/pull/60143) | **Open** | `e36c80ffdcb1` | — |
| [#60228: [Bugfix] Invalidate stale multimodal startup plans](https://github.com/vllm-project/vllm/pull/60228) | **Open** | `a640b8b82b30` | — |
| [#60227: [Bugfix] Bound threaded PT shard retention](https://github.com/vllm-project/vllm/pull/60227) | **Open** | `896523bc1391` | — |
| [#60688: [Perf] Reduce RMSNorm metadata work](https://github.com/vllm-project/vllm/pull/60688) | **Open** | `fb6d17d9f465` | — |
| [#60498: [Perf] Reduce multiprocess decode logging CPU by 28%](https://github.com/vllm-project/vllm/pull/60498) | **Open** | `2e92119f6732` | — |
| [#60497: [Perf] Reduce fallback decode CPU by 69% at 32K](https://github.com/vllm-project/vllm/pull/60497) | **Merged** | `50f09de18684` | 2026-10-08 21:42:57 |

### NVIDIA Dynamo

| PR | Current state | Head | Merge or close time (UTC) |
| --- | --- | --- | --- |
| [#15973: perf(frontend): avoid copying the prompt batch for each child](https://github.com/ai-dynamo/dynamo/pull/15973) | **Open** | `aae6302bb3a6` | — |
| [#16344: fix(runtime): keep TCP admission until ACK](https://github.com/ai-dynamo/dynamo/pull/16344) | **Open draft** | `601df227b6de` | — |
| [#16346: perf(runtime): skip early TCP tombstone scans](https://github.com/ai-dynamo/dynamo/pull/16346) | **Open draft** | `50c86892cbe6` | — |
| [#15974: perf(runtime): avoid discovery copies in prepared dispatch](https://github.com/ai-dynamo/dynamo/pull/15974) | **Merged** | `348b86fa5ef5` | 2026-10-13 04:08:13 |
| [#15992: perf(router): avoid full scans for sparse worker eligibility](https://github.com/ai-dynamo/dynamo/pull/15992) | **Merged** | `f1a996ca244e` | 2026-10-13 17:58:46 |
| [#15993: perf(router): remove completed prefills without queue scans](https://github.com/ai-dynamo/dynamo/pull/15993) | **Merged** | `62bcfbbc240f` | 2026-10-15 03:22:20 |
| [#15994: perf(kvbm): avoid a set build for one new block](https://github.com/ai-dynamo/dynamo/pull/15994) | **Closed** | `d625d8dbd040` | 2026-10-13 02:48:28 |
| [#15995: perf(kvbm): avoid full alias scans on block removal](https://github.com/ai-dynamo/dynamo/pull/15995) | **Closed** | `1bd47f8049c4` | 2026-10-13 02:48:24 |
| [#15976: perf(runtime): reduce copies in ingress envelope decoding](https://github.com/ai-dynamo/dynamo/pull/15976) | **Closed draft** | `95880506952b` | 2026-10-09 11:01:01 |

The five open vLLM PRs each report a failed `pre-run-check` and require review.
This report does not diagnose that check as a source regression. Earlier saved
records identify trust/approval restrictions. The current status is not an
all-CI-passed result. The three open Dynamo PRs have no failed reported check
in the captured rollup. A green rollup does not replace a full serving test.

### What the public vLLM work fixes

| Work | Problem addressed | Interpretation |
| --- | --- | --- |
| Startup GPU budget, #60143 | A saved startup plan can remain valid after the effective GPU memory budget changes. | Safety and invalidation correctness; no general startup speed claim. |
| Multimodal startup profile, #60228 | A plan can retain stale multimodal profiling inputs. | Related safety work, with a distinct invalidation contract. |
| Threaded PT loader, #60227 | Completed shard results can retain full checkpoint state while consumption lags. | Bound retained loading work; preserve tensor loading and failure behavior. |
| RMSNorm metadata, #60688 | Fake/meta execution performs avoidable metadata work. | CPU/compiler-path optimization, not an RMSNorm CUDA arithmetic speed claim. |
| Decode metrics, #60498 | Zero-valued multiprocess counter updates add avoidable CPU work. | The title's 28% result refers to measured logging CPU work. It is not 28% faster generation. |
| Fallback detokenization, #60497 | Copying the full token-string history on each fallback decode step adds CPU work. | Merged. The title's 69% at 32K is the tested fallback decode boundary. Both versions decode the required window. |

The older PR work, tests, revisions and review limits are expanded in
[the early vLLM history](vllm-early-history/REPORT.md). The current ledger above
supersedes old statements that all six vLLM PRs were still open.

The safety results are useful without a speed claim. The GPU-budget regression
changed a stale 16.15 GiB KV allowance to a fresh 6.23 GiB allowance after the
budget fell. The multimodal profile avoided a 2.83 GiB excess relative to fresh
profiling in its tested configuration. The bounded PT loader reduced tracked
live-tensor peaks by 52–59%; RSS/PSS did not show a clear reduction. These
numbers come from the historical tests linked in the early-history appendix.

A separate docs PR, [#55944](https://github.com/vllm-project/vllm/pull/55944),
corrected statements about numerical differences. It was closed at Kamran's
request. The saved wording commit is `924fadc8717bcfa48979ae28b4fab10f86e92f05`.
This historical documentation record is separate from the 15 code PRs checked
in the current ledger.

### What the public Dynamo work fixes

The frontend batch change removes repeated whole-batch copies while creating
child requests. The final review change consumes the batch and moves each
prompt buffer into its child. Its 17 October record has 42 targeted tests and
26 buffer checks. A 64 × 4 KiB construction probe requests 99.3% fewer bytes.
That is request construction, not model speed.

Prepared dispatch avoids discovery-copy work. Sparse eligibility avoids full
worker scans when only a small eligible set is needed. Prefill completion uses
direct removal instead of scanning a queue for non-FIFO completions. These
three PRs are merged. Their historical normal Linux/Rust test results remain
in [the Dynamo history](dynamo-history/REPORT.md).

Sparse eligibility reduced its tested exhaustive helper collection from
3.132 µs to 60 ns at 512 workers and four eligible workers. This is a helper
boundary. The final prefill change uses a standard BTreeMap and O(log N)
unlink, rather than the earlier custom O(1) list. At 512 queued prefills,
shuffled drain improved by 75.9%, but FIFO drain was 10.4% slower. Small shuffled
cases also regressed. The final implementation and its tradeoffs supersede
the earlier prototype timings.

The two small KVBM PRs are closed without a merge. Native tests did run in the
saved refresh, but that does not make them accepted upstream work. The ingress
decoder PR is also closed. Its stronger later request campaign confirmed an
allocation saving but did not confirm a useful general latency improvement.

## 4. Startup and loading research

### Real startup and FP8 baseline measurements

Qwen3.8-27B on two H100s took 252.18 seconds to become ready in one cold process
and 104.82 seconds in a later process in the same container. Compiler files and
model-file cache state both changed. The 58.4% difference is a cold/warm
observation, not a patch result. Steady decode matrix work accounted for about
83–84% of summed GPU kernel time in the tested 8,192-token case. This did not
prove a memory-bandwidth bottleneck.

FP8 was not uniformly faster. Single-request output rates improved by about
30.5–33.2% in the first allocation. The eight-request, 2,048-token case lost
12.7%, 14.3% and 12.5% across three allocations. Exact-workload traces linked
the loss to large mixed-prefill row counts taking the SM90 swap-AB route when
the row count was not divisible by four. Steady decode could be faster while
the complete request was slower. The small math checks had equal aggregate
scores but different outputs; they do not establish equal model quality.
Existing PR [#60464](https://github.com/vllm-project/vllm/pull/60464) already
addresses the measured dispatch rule. This audit reproduced the stock failure.
It did not rebuild or validate that PR's fix.

Source: [two-GPU profile][VPROFILE].

### Compiler work: useful attribution and rejected shortcuts

A later cold trace found 130 compile-adaptor attempts per rank, but only 40
reached native inner compilation. Ninety already took the reuse path. It did
not prove 130 repeated full compilations. A 21–22 second region inside the
PyTorch compiler frontend remained unattributed. It was a useful next target,
not a completed optimization. Inclusive call durations and concurrent rank
times must not be added.

Shared AOT artifact serialization was implemented and tested on two model
families. Exact object memoization plus a content pool reduced native serialize
calls from 29 to three and 27 to three. Artifact collection saved 49.54–56.06 ms.
Fresh AOT cache loads matched all 64 generated tokens and returned logprobs.
The collector still hashes all entries. Its whole complexity did not become
constant per distinct object. The patch stays local at `6360d59e`; it is held
because a roughly 50 ms phase saving did not establish a useful startup gain.

Host-local checkpoint prefetch was rejected for submission. A two-host cache
simulation improved page coverage from 50% to 100%, but did not show a speed
gain. The loading ranks for an auxiliary model can differ from host membership.
A new loader collective could wait for ranks that never enter that load.
Existing pre-sharded loading and lazy views also disproved some simple copy
assumptions.

The later compiler frontend trace attributed about 9.2 seconds to functional
graph capture/cleanup and 5.6 seconds to mutation/view metadata. It still did
not establish a safe removal. The earlier unattributed interval is a historical
measurement, not the final limit of the investigation.

Sources: [compiler audit][VCOMP], [later frontend attribution][VFRONT],
[startup decision][VSERIAL].

### Graph-memory accounting correction

The warm graph estimate of 708 MiB and final capture delta of 74 MiB initially
looked like a large avoidable gap. Explicit boundaries found 624 MiB retained
after the temporary probe. Most of the apparent gap was not free memory that
could safely become KV cache. Existing upstream work covered the confirmed
accounting defects. No new broad graph-probe removal patch was justified.

Source: [generic startup audit][VGEN].

## 5. vLLM core and GPU drafts from 10–15 October

These are independent candidates. Earlier native evidence does not transfer
automatically to a later port or different source base.

| Candidate | Strongest result retained | Limit or decision |
| --- | --- | --- |
| MLA live-cache restoration | Base lost a strided cache write; the patch restores real selected cache storage. A later native model check confirmed the target write. | Keep cache restoration distinct from the save-gather performance prototype. Broader transfer/attention checks remain. |
| PCP dispatch counting | Replaces per-rank request scans with O(P+N) counting. 208 normal CPU cases; two H100 ranks matched 272 generated tokens and 816 logprobs. | Synthetic eager model. Large CPU stress gains are not model-throughput gains. Small controls include overhead. PR 60538 changes short-prefill ownership and invalidates the saved count on that policy. The private correction has source checks only. |
| Compact DeepGEMM warmup routes | Retained route allocation: 77.623 → 0.683 MiB. All 320 route plans match. Real synthetic MoE startup/serving checks matched tokens, weights and RNG. | The small warm helper was about 5.2% slower. No total startup-peak or startup-speed claim. |
| DeepGEMM route metadata | 67 native H100 cases; large-route model path reached R131072. Three PSUM calls use one block each instead of 32. | Earlier component time: 50.120 → 28.614 µs. Synthetic model; useful serving gain unmeasured. |
| PP integer row gathering | CPU coverage and four real CUDA row/event cases. | Two-rank speculative model gate remains open. |
| Async KV reservations | Selected scheduler tests and supported fallback contracts. | Real offload/DMA, failure, resume and serving validation remain. |
| EPLB inverse maps | Source/CPU/native component work. | Candidate distributed rebalance and useful model latency remain. |
| Input preparation fusion | Native int64 token-state coverage. | Earlier 18–28.6% timing belongs to an int32 prototype. UVA/model/lifetime gates remain. |
| XQA draft graph | Earlier native graph/output evidence; current port has 34 AR worker and five capability CPU cases. | The current port lacks device/model validation. Old-head results are not a current-port pass. |
| Sampler staged writes | CPU source timing and selected state tests. | Native pinned-buffer lifetime and full model gates remain. |
| Masked MoE clear removal / EP activation | Targeted evidence and old native probes. | Held for mixed gains, ABI/port and distributed/model limits. |

Source: [14 October core record][VCORE14] and
[early vLLM history](vllm-early-history/REPORT.md).

### Table/slot fusion: useful metadata improvement

The final tested October 15 draft combines two metadata launches into one.
Seven L4 shapes used **3.5–20.0% less GPU metadata time**, saving 1.14–4.59 µs
per call. Earlier H100 shapes used 17.7–28.2% less time. Full table contents
and the full allocated slot tail were checked. Fourteen committed CUDA cells,
synthetic eager/FULL model pairs and a separate async-output smoke passed.

The FULL diagnostic copied metadata to CPU and serialized steps. The separate
async smoke did not prove active device readers at slot reuse. Normal UniProc
FIFO ownership has source and protocol-model support. Startup and distributed
late readers retain separate contracts. There is no full serving speed claim.

Tested draft: `feat/gather-slot-fusion`, `a40a6eb6a02bd7995452df7ac4f41cb787c7180c`.
The 17–18 October refreshed fusion draft is a **different source successor**.
It restores current dirty-row and draft-consumer behavior. That successor has
source/mocked evidence only. It does not inherit the October 15 GPU pass.

### Scalar FP8 scratch: memory improvement

The eager scalar fallback keeps one BF16 weight scratch buffer instead of two.
All 12 paired allocation observations saved 4,194,304 bytes for a 1,024 × 2,048
weight. Fifty-four CUDA records and synthetic plain/online Llama pairs passed.
Timing was mixed, including a slower cell. The saving is per complete apply;
it cannot be added across layers or treated as total model peak reduction.

Final test-only head: `1804ee56d9395f80659209ac3d93ad73020796d8`.
Production bytes match native-tested `216fcf143b84e526c8722e67cbb7b8bb31187a7a`.
Automatic L4/H100 routes usually bypass this fallback. The SM100 route has
source reachability evidence, not final native Blackwell validation.

Source for both: [final five-hour validation][VFUSION].

## 6. Full-model work from the cross-project chat

### Grammar-selected output head

The experimental head projects the union of grammar-allowed vocabulary rows,
then retains the normal mask, processors and sampler. It has no persistent
selected-weight cache. Wide or unsupported batches use the dense path. The
final patch profiles its maximum workspace before KV sizing and uses dense
fallback with explicit manual KV budgets.

On Qwen3-4B, one L4, BF16, MRV2, TP1 and the recorded graph settings, three
tested narrow workloads used **8.2–8.9% less complete offline request time**.
The unconstrained control had no clear change. Eighty-two final native tests
and 16 full-model comparisons passed. The frozen 32-question JSON check had
32 valid objects and 10 correct answers on both paths. This is not a full
GSM8K result or universal numerical identity.

An early BF16 projection changed two token sequences. The final FP32 selected
projection fixed the observed failure. Startup memory was also repaired and
retested. Those corrections are part of the final draft, not optional future
work. TP, quantized heads, LoRA, speculation and broad serving are outside its
support. This is the strongest measured model-speed draft in the records.

### MLA request-table reuse

The Triton MLA draft stops copying a request block-table row for each draft
query. Query rows index the original request table. It removes an O(BQW)
temporary and copy; it does not remove attention arithmetic.

Full DeepSeek-V2-Lite-Chat used all 27 attention layers and accepted 3,650 draft
tokens. Five full-model token/logprob comparisons matched. Metadata, native
attention and changed-page graph checks passed. Full-model timing was noisy
and mixed. **No stable full-model speedup is established.** It remains an
allocation-reduction draft.

Source for both: [final grammar and MLA review][VGRAMMAR]. Earlier overnight
results are superseded where the later review repaired precision, memory or
test coverage.

### N-gram replay: a useful negative result

Managed replay reduced launch-bound proposer time by 68.9–71.0%. Native tests,
queued checks, sleep/wake and graph checks passed. OPT-125m improved by only
0.8–1.4%. The later Qwen3-4B check ran four workloads with 11 pairs each and
matched 69,003 timed output tokens per arm. Full generation medians were
0.01–0.02% slower. The draft is held. A large isolated host/launch gain did not
justify a broad model-speed claim.

Source: [GPU follow-up and later correction][VNGRAM].

### Other vLLM GPU results

| Candidate | Saved result | Remaining limit |
| --- | --- | --- |
| Direct context-free MLA output | Earlier BF16 source used 2.05–2.36% less complete one-output-token model time on four DeepSeek workloads. Eight FA3 cases and seven model comparisons matched. | Final FP8 dtype guard has CPU evidence only. The final guarded source needs a native rerun. |
| Packed XQA ragged masks | About 256 → 48 µs for mask plus native attention in the scoped H100 case; 16 native consumer cases. | Resident-offset component boundary. Model attempt stopped at offline lookup. |
| Zero-expert routing | Complete L4 router call used about 20.46–21.21% less time; 432 native and 1,944 CPU cases matched. | Zero-expert model feature only. No full model or graph result. |
| Mamba2 causal CB tile skip | 36 producer and 108 consumer interpreter cases; 144 CUDA targets compile. | No native timing. All CTAs still launch; some small chunks skip no tiles. |
| Torch MXFP8 capability guard | Forced SM90 path fails its native recipe with CUBLAS_STATUS_NOT_SUPPORTED. Ten capability and 40 modeled selection cases pass after an SM100 guard. | Narrow forced-backend compatibility fix. Installed selection/native supported-device tests remain. |

Source: [15 October cross-project report][VCROSS].

## 7. New vLLM contribution search, 17–18 October

### Initial findings

| Candidate | Actual evidence | Remaining work |
| --- | --- | --- |
| ARM GPT-OSS W4A8 gate/up layout | Original native result has 35/1,024 values outside tolerance. Alternating gate/up selection passes. Official ARM suite: 169 passes. Synthetic two-expert loader/native check passes. | Trained GPT-OSS and reporter checkpoint format. Synthetic loading is not that reporter's compression recipe. |
| Responses cumulative output budget | Original real ASGI/Harmony JSON/SSE pair has six budget failures and two controls. Candidate passes eight HTTP cases and 18 normal cases. | Engine, tokenizer and tools are scripted. Real model/tool evaluation and adjacent PR coordination remain. |
| Offline embedding dtype in prefix-cache identity | Equal bytes with FP16/BF16 meaning cause a wrong 32-token hit. Fix gives zero cross-dtype hit and preserves same-dtype reuse. Nine normal cases pass. | Public worker/model path and live cache compatibility. A denied import follow-up is an environment failure. |
| Direct segmented mean pooling | 84 correctness cases. L4 cold-L2 component: 2.88–6.93x faster; warm BF16: 4.18–33.51x. Three trained MiniLM pooling checks agree. | Actual worker dispatch, model throughput and PR 60035 coordination. These are not model speedups. |
| Refreshed MRV2 table/slot fusion | Corrected current dirty-row clearing and draft-consumer seed; source review and 459 mocked cases. | Native device/model/performance and PR 60767 coordination. Separate from the older native-tested draft. |

Sources, exact patch hashes and commands:
[initial contribution record][VSCOUT] and [final vLLM record][VFINAL].

### The later substantive lifecycle drafts

**KV rejection cleanup.** A lazy engine iterator can reject after the earlier
request-construction wrapper has ended. Remote prefill then misses its
rejection notice. The four-production-file, three-test-file patch joins those
lifetimes and sends the notice at most once before any engine output.

The candidate passed 43 normal mocked-engine/RPC cases. Its host audit failed
after cleanup because a saved helper compared eight Responses names with all
43 collected names. Independent saved-data review confirmed the 43 passes.
The original-code follow-up failed exactly three missing-notice assertions;
its host and strict result checker passed the expected-failure contract.
The baseline suite did not pass. Its separate independent actual-result audit
was not completed before the user stop. A live connector/producer lease test
remains. Permanent leakage is not proved. PR 59343 touches the shared helper.

Source: `feat/stream-kv-admission-cleanup`, `c72c801883a1eb9355b9ea8863464a6b74c59482`.

**Utility futures after engine death.** Six original controlled requests stayed
pending. Six candidate requests raised EngineDeadError and cleared the registry.
The normal suite later passed all 23 cases with real futures, tasks and bounded
caller threads. Engine transport was mocked. Host, guest and strict checker
passed. Independent review passed 1,154 data/source checks and three negatives.
Two original delivery tool objects were not saved; the completion receipt,
host records and strict-checker object were retained. Keep that evidence limit.

Source: `feat/utility-terminal-cleanup`, `6b80689e4263f918946729083bdd54781733e1ad`.

**Background Responses terminal state.** A stored non-streaming response could
stay queued after an ordinary producer exception. The draft marks an active
response failed while preserving terminal states and cancellation. Twenty-two
controlled rows and 12 normal cases passed. Engine/render/tool inputs are
mocked. Full public HTTP, real engine and model evaluation remain open.

Source: `feat/background-response-terminal`, `ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`.

All three branches were signed and pushed to Kamran's fork. They are separate
drafts, not one tested stack. The final detailed report is at `c154d7216b` on
`feat/vllm-contribution-research-20261018`. No upstream publication occurred
in this contribution-search phase. Source and evidence links are in
[the final vLLM record][VFINAL].

## 8. NVIDIA Dynamo: runtime, routing and native findings

### Earlier core work and tradeoffs

| Candidate | Saved result | Decision or missing gate |
| --- | --- | --- |
| Output-weight tracking | 1,055 native router tests, two ignored. At 4,096 hinted outputs, complete component CPU time fell 38.7%; requested heap peak fell from 241,776 to 143,472 bytes. | Adds 16 header bytes. Reweighting and hinted-growth complexity remain. No serving result. |
| Scheduler queue statistics | Welford values preserve current statistics. FCFS Q4096 component time fell 41.5%; priority case fell 11.8%. | Normal native existing-file follow-up had 287 passes and one port-race failure, then one passing retry. It was not one clean full-suite pass. Global conftest was bypassed. |
| Long-prefix lookup | Native router and exact parity checks. 4,096 blocks/32 workers: 2.704 → 1.233 µs. | O(L) remains. Reconvergent inputs were 20–30% slower. Mixed production value is unknown. |
| Deadline index | Sparse expiry and staggered drain became much cheaper in the tested native component. | Rejected as a general contribution. Roughly three times the queue storage; bulk cancellation 57–70% slower; simultaneous expiry also slower. |
| Pinned image embedding cache | 31 native connector and four configuration tests. Eight 8 MiB saves: 14.468 → 5.482 ms, including allocation/save work. | Classic multimodal vLLM cache only. Real image miss/hit serving, supported versions and allocator-wide pinned memory remain open. |
| Skip unused image sizing | 200 source-parity cases. An unused 32K-token hint fell from about 215–220 to 1.49–1.60 µs. | SDK/media doubles. Native TRT integration and actual vision requests remain unrun. |

These are separate local candidates. None is a new full-model performance
result. Source identities and final tradeoffs are in
[the Dynamo history](dynamo-history/REPORT.md) and [the worthiness review][DCORE].

### TCP admission until ACK

The old permit belonged to the waiting caller. Cancellation could release it
while the request still occupied transport storage. The draft moves an owned
permit with the request through its ACK/discard lifetime. Caller activity
stays separate for idle cleanup. A one-slot native socket regression fails on
base and passes with the fix. Forty client tests passed. The combined network
check with the tombstone change passed 304 tests with three known base tests
excluded. The overlapping suite totals must not be added.

This is draft PR 16344. It adds no new task, lock or unsafe code. The existing
EOF-before-handoff race remains outside its scope.

### TCP tombstone expiry scans

An earliest-expiry deadline avoids scanning the removal table before any entry
can expire. The native association method used 25.6% less time with 32 records
and 75.0% less with 256. Due scans remain capacity-dependent. Small controls
have little benefit or a small regression. This is draft PR 16346, not a model
speed claim. Intermediate results from a shared wrong-worktree binary were
rejected. Final source switches forced the right rebuild.

Source for both: [TCP fixes][DTCP].

### Approximate-LRU physical copy index

Duplicate output hashes can have many physical copies. A position index removes
the repeated vector search and repairs the index after swap_remove. The native
router suite passed 1,081 tests with three existing ignored cases. All 65,536
saved state/event snapshots matched. At 4,096 duplicate copies, eviction
pressure used 90.1% less time; the full measured sequence used 61.0% less.

The tradeoff is eight extra bytes per copy on the tested host. A small case
was 6.3% slower; large distinct-hash cases were 1.4–1.9% slower. Real duplicate
frequency is unknown. The feature is opt-in approximate LRU with events off.
The local one-file draft is not a proved serving improvement.

Source: [LRU follow-up][DLRU].

### Native HTTP metadata inconsistency, then a normal tested fix

Two ready namespaces advertised the same model/alias with effective context
limits 2,048 and 4,096. The real native frontend returned 4,096 from list and
2,048 from retrieve in stable dual-namespace samples. Single-namespace controls
agreed. No inference request was needed to establish the inconsistency.

The four-file candidate shares the existing projection between OpenAI list,
retrieve and Anthropic callers. It preserves the current list policy instead
of inventing a new min/max winner. Later normal Rust gate 9530 reproduced the
baseline assertion failure and passed five candidate tests: one HTTP regression,
two resolver tests and two readiness tests. Independent review checked the result.

Candidate: `50722afdfedc8b0e7027fce18b781437ef3ffa27`. This is the strongest
new 17–18 October Dynamo implementation result. The original native runtime
wheel did not itself contain the fix; the later Rust gate is distinct evidence.

### Profiler artifact provenance: deeper implementation, tests blocked

Candidate `8b991fad3a738d672656267a22ff407877839ff9` changes five production
files and three existing test files. It carries only interpolation artifacts
produced by the current invocation into final assembly. It preserves aggregate
fallback, user files and the existing partial-artifact shape.

Independent source review found no new actionable defect. Normal Python
imports, collection, original failure and candidate product tests did not run.
A qualified matching runtime/AIS/test dependency closure was unavailable.
The implementation goal stayed incomplete. Repeated failed setup routes were
closed rather than replaced with fake package initializers or copied helpers.

Source for both: [Dynamo implementation plan][DPLAN] and
[Dynamo history](dynamo-history/REPORT.md).

### Other native findings and their exact limits

| Finding | Observed result | Status |
| --- | --- | --- |
| Planner DP sample labels | Native estimator: 21/24 DP8 baseline rows disagree with aggregate simulated batch count; candidate 24/24 agrees; DP1 control matches. Native SDK models retain data and return finite predictions. | Qualified component with AST/package-shell limits. Prior approximation policy and normal installed project gate remain. Prediction changes do not prove better accuracy or autoscaling. |
| Session append/removal | Each version passed 32 selected native session tests and eight backend tests. Selected leaf-removal medians improved 35.5% and 27.6%; mixed/internal cases regressed 5.9% and 2.6%. Native Stored-event replay retained parity. | Prior review already covers parts of the mechanism. Timing wrapper and native event consumer differ. Active tier stack and actual eligible frequency matter. No serving gain. |
| NATS endpoint identity collision | Valid same-DRT namespace/component pairs encode to the same subject. Noncolliding control: 9/9 correct. Joint collision: six wrong-handler replies among eight requests. Real broker exchanges match. | Native correctness observation. Exact alias concern exists in prior review. No wire-format patch; compatibility/migration needs the runtime owner. Not a security or production-frequency claim. |
| SDK top-level null | Normal SDK unary call gets an annotated null frame but no unannotated item; exact no-response RuntimeError. Six non-null typed controls pass. | Public null policy is unresolved. No shared schema patch is justified from this observation alone. |
| Audio AAC | Real SoundFile constructor on macOS accepts WAV/FLAC but rejects AAC before writing bytes. | Dependency admission only. No Dynamo formatter, waveform, model, HTTP or Linux path ran. Backend-specific policy is needed. |
| GMS V1 | Real L4 Qwen3-0.6B generation matches 32 output token IDs. Both workers expose the same blocks/capacity/descriptor bytes and graph launches. | Qualification, not memory savings or a fair speed comparison. No distributed serving or integrity result. |
| Routed video duration | Real source omits seconds while forwarding the parser request. Draft and four cases prepared. | Normal Omni imports and actual tests remain unrun. Parser frame counts are not final encoded duration. |
| Non-UUID mocker request ID | Source can generate independent fallback UUIDs across P/D calls. | No supported baseline runtime observation or candidate result. Asset acquisition failed before tokenizer bytes. |

Sources: [permanent Dynamo evidence record][DNEW] and
[Dynamo history](dynamo-history/REPORT.md). Source-only planner startup-name,
replay-budget and active-PR reviews remain in the linked history. They are not
counted as independent validated fixes.

## 9. Adjacent TensorRT-LLM and SGLang work

These experiments occurred in the chat named `dynamo`. They are not Dynamo
product fixes. Their repository labels must remain attached to each claim.

| Project and lead | Evidence | Decision or missing gate |
| --- | --- | --- |
| TensorRT-LLM Marlin routing-sort reuse | Two sorts become one; 480 exact CPU handoff cases. | Native FP4 output, graph routing and complete-layer timing remain. |
| TensorRT-LLM DeepGEMM scratch ownership | Concurrent chunks alias three writable buffers. Separate slots pass 32 allocator and 12 scheduler-arm checks. | Native two-stream corruption is not proved. Graph ownership and actual peak memory remain. |
| TensorRT-LLM SM120 expert IDs | 108 original counterexamples in 252 CPU cases; global-ID normalization passes. | Supported multi-GPU dispatch/GEMM/model test remains. |
| TensorRT-LLM forced dynamic FP8 SwiGLU | Eight policy failures among 48 CPU cases; 40 controls. | Native model gate and wider fusion-policy audit remain. |
| TensorRT-LLM dynamic NVFP4 zero scale | Infinite scale in 12 CPU examples. | Blackwell quantizer/GEMM propagation remains untested. |
| TensorRT-LLM GDN/Mamba copy removal | Exact CPU stride/alignment handoffs. | Native state update, reduction order, graph and model checks remain. |
| TensorRT-LLM active-expert conversion | 1,344 CPU cases, 504 avoid extra conversion. | Tiny cases can lose. Native full-call value remains unmeasured. |
| SGLang SWA predicate | 1,230 CPU plus 1,230 CUDA helper cases; eight native consumers. Tested helper time falls 12–28%. | Three initial host readbacks remain. No full SGLang serving result. |
| SGLang block-16 FP4 pool | Full allocated-pool conversion has high calculated traffic. Inline reader/compact prototypes have codec, interpreter and compiler checks. | Shared-prefix compact cases regress up to 3.25x MPS/3.62x CPU. Inline reader has more spills. No general fix or native speed win. |
| SGLang local decode buffers | 144 metadata cases and 12 adapted tests. Example storage 128 → 8 MiB. | Native capture/output remains. |
| SGLang AITER scales and fresh K/V ordering | CPU counterexamples for Q descale and in-place producer ordering. | ROCm, physical layout, stream, graph and model tests remain. These are distinct defects. |
| SGLang AITER left window | 24 original boundary differences; 60 corrected CPU cases. | Native ROCm window test and owner coordination remain. |
| SGLang compiled one-token MoE | Conservative guard has eligibility and CPU compiled-output evidence. | Optimized fallback is a CPU double. Native compile/EP/layout/model gate remains. |
| SGLang Lean setup/lookup, KDA backup and FA3 Q view | CPU/interpreter/offline-compile or pointer evidence. | Native complete-call crossover, recovery or attention output remains. |

Twenty-two private patches were checked separately against their pinned source.
That is not one combined stack. All six vLLM patches in that campaign passed
pinned changed-file Ruff checks. It was not a full repository type/build pass.
Source: [cross-project report][VCROSS] and its linked primary-source appendix.

## 10. Rejected and owned work

Useful negative results prevented duplicate or unsafe contributions:

- Compiler worker settings and early cache-key APIs already had upstream owners.
- Host-local prefetch had no safe small participant contract.
- Split-table mapping made its complete caller 82–89% slower.
- Generic penalty scan/histogram rewrites regressed important native shapes.
- N-gram replay's component gain did not become a larger-model gain.
- Closed ingress decoding retains a repeatable allocation benefit, but its
  fresh selected latency signal did not repeat consistently. Keep it closed.
- EPLB recovery, LoRA unload/activation and worker memory-accounting leads had
  active matching PRs. No competing patch was made.
- EPP priority handling had useful native queue regression evidence, but the
  fix was already owned in a fork. Semantic owner review corrected an earlier
  keyword-search miss.
- NIXL delayed-producer transfer did not complete in the available network
  environment. It is a source-supported question, not a reproduced transfer bug.
- GMS generation parity is not evidence of GMS integrity or memory saving.
- Unstarted-stream disconnect reachability, prompt width, CMake architecture
  fallback, tiny-logit top-k and several tokenizer/media paths retain stated
  support, owner or native-test limits.

Exact PR IDs and individual rejection reasons are in the source reports and
both history appendices. This list is not a global claim that those systems
have no other bugs. A previous closed or idle-capped PR is not permission to
copy its fix without attribution and coordination.

## 11. Costs, resources and storage

There is no defensible single final bill for all two weeks. Campaigns used
different caps, requested-rate estimates, billing guards and CPU services.
Some figures omit setup, some contain conservative reservations, and some
are overlapping snapshots. They must not be added as actual spend.

| Campaign | Saved accounting | Interpretation |
| --- | --- | --- |
| 8 October compiler trace | About USD0.64 for the successful experiment interval | Partial requested-resource estimate; excludes named setup/load/build costs. |
| 8 October serialization check | About USD0.39 timed function CPU/RAM/GPU estimate | Excludes named startup/build/scaledown and CPU-only work. |
| 14 October core GPU follow-up | USD0.3850; managed replay round USD0.2132; larger-model round USD0.3324 | Separate requested-rate scopes. Not invoices. |
| 15 October grammar/MLA overnight | USD0.49758 | Separate from the later final review round. |
| 15 October grammar/MLA final review | USD0.43854 | Whole owned-app interval estimate; 13 apps stopped. |
| 15 October cross-project five hours | USD0.48506 Modal estimate | Separate E2B costs were not measured. 18 Modal apps and seven saved sandbox stops. |
| 15 October vLLM fusion/FP8 five hours | Guarded estimate USD2.68 under USD3 cap; completed-hour billing report USD0.43041286 for 26/27 owned IDs | Billing lag and retained build/network guards prevent using the partial report as a final bill. 27 owned apps stopped. |
| 17–18 October vLLM contribution search | Guarded ledger value USD2.9192748 under USD10 cap | No new paid work in the later deep-fix phase. Not a live balance. |
| 17–18 October Dynamo search | USD8 retained pessimistic reservations plus USD2 margin under its separate USD10 cap | All 12 reservations retained; invoice total unknown. No further allocation fitted. |

GPU-minute allowances in the earlier core campaigns are also scope-specific.
For example, the 14 October pass settled at 17.402 device-minutes under its
20-minute allowance. Minutes are not dollars or kernel time.

The latest final vLLM stop measured about **67.5 GB free SSD space**. It recorded
exact cleanup for the final local containers. Prior model/cache volumes were
preserved. Owned redundant scratch/cache cleanup was recorded separately.
No fresh global cloud inventory was run for this consolidation. Historical
stopped-resource receipts remain historical; other chats' resources were not
changed. Both vLLM and Dynamo finite automations were read as paused.

Sources: campaign reports, [final vLLM stop][VFINAL], and
[Dynamo budget/history](dynamo-history/REPORT.md).

## 12. Handoff order

This is a suggested review order if Kamran later chooses to resume. It is not
an active goal, schedule or authorization for more compute.

1. Resolve human review and CI access on the open public PRs. Preserve the
   current closed/merged decisions.
2. Review the final grammar head as the strongest measured model-performance
   draft, within its narrow supported modes and memory limits.
3. Review Dynamo metadata `50722af` and vLLM KV cleanup `c72c801` as correctness
   work. The latter still needs real connector/lease validation and shared-helper
   coordination.
4. Assess PCP counting, compact warmup and the native-tested fusion/FP8 drafts
   at their exact tested commits. A newer source port needs new validation.
5. Review ARM W4A8, Responses cumulative budget, embedding-cache dtype and
   utility/background terminal drafts with their model/engine gaps visible.
6. Keep the Dynamo profiler provenance fix blocked until a qualified normal
   environment is available. More mocked tests do not close that gate.
7. Keep speculative or hardware-bound TRT/SGLang/MRV2 successors on hold until
   the smallest real native gate can run under a new explicit compute budget.

Every upstream submission still needs a human to understand the cause, review
every changed line, run the relevant tests, refresh duplicate/owner checks and
disclose AI assistance. No new source stack was assembled or validated here.

## 13. Records and reproducibility

- [Early vLLM history](vllm-early-history/REPORT.md): earlier PR and core work,
  with exact source references and limits.
- [Dynamo history](dynamo-history/REPORT.md): earlier frontend/router/TCP work
  and the 17–18 October findings, implementations and blocked gates.
- [Current public PR snapshot](public-pr-state.json): current state and exact
  heads, not a historical assumption.
- [Thread coverage](thread-coverage.json): selected conversation evidence and
  retrieval limits.
- [Source index](source-index.json): report and packet paths with byte hashes.
- [Schedule state](automation-state.json): both finite automations are paused.
- [Report checks](report-validation.json): local citation, JSON, hash and PR-count
  checks. These checks do not rerun historical product experiments.

The original consolidation was saved locally. Kamran then authorized this
report and an HTML edition to be committed and pushed to
`feat/vllm-contribution-research-20261018` on `spa5k/vllm`.
This packet contains report text, selected state snapshots and source indexes.
The private Dynamo archive, raw experiment trees, models and build artifacts
are separate. Both research schedules remain paused.

[VPROFILE]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/two-gpu-profile-20261008/REPORT.md
[VCOMP]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/compiler-heavy-audit-20261008/REPORT.md
[VFRONT]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/compiler-heavy-audit-20261008/frontend/REPORT.md
[VGEN]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/generic-startup-audit-20261008/REPORT.md
[VSERIAL]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/generic-startup-audit-20261008/final-validation/REPORT.md
[VCORE14]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/core-finalize-20261014/REPORT.md
[VFUSION]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/core-budget-validation-5h-20261015/REPORT.md
[VGRAMMAR]: /Users/pacific/Developer/dynamo-audit/20261015/pr-ready-core/REPORT.md
[VNGRAM]: /Users/pacific/Developer/dynamo-audit/20261014/core-gpu-followup/REPORT.md
[VCROSS]: /Users/pacific/Developer/dynamo-audit/20261015/deep-core-five-hour/REPORT.md
[VSCOUT]: /Users/pacific/.codex/worktrees/vllm-research-record/vllm/benchmarks/local_speed_audit/contribution-record-20261018/REPORT.md
[VFINAL]: /Users/pacific/.codex/worktrees/vllm-research-record/vllm/benchmarks/local_speed_audit/contribution-final-20261018/REPORT.md
[DTCP]: /Users/pacific/Developer/dynamo-audit/20261014/core-fixes/REPORT.md
[DCORE]: /Users/pacific/Developer/dynamo-audit/20261010/pr-worthiness/REPORT.txt
[DLRU]: /Users/pacific/Developer/dynamo-audit/20261014/next-core/REPORT.md
[DNEW]: /Users/pacific/.codex/research/dynamo-2026-10-17/DETAILED-RESEARCH-REPORT.md
[DPLAN]: /Users/pacific/.codex/research/dynamo-2026-10-17/IMPLEMENTATION-PLAN.md

# Unpublished findings: impact and PR preparation

Prepared on 19 October 2026, India time, from research through 18 October.
This is a manual review queue. Research remains
stopped. Both research schedules remain paused. No new product test, model run,
paid job or upstream submission was made for this update.

**Start with Dynamo context metadata, the grammar output head and MLA cache
restoration.** For a larger change across serving modules, review KV rejection
cleanup next. Its live connector test is still missing.

**Correction: do not open our utility-terminal-cleanup draft as a new PR.**
The fresh search found open [vLLM #56416][utility-owner] and
[#58279][rpc-owner]. They cover pending utility futures when the receiver stops.
The second PR includes the first author's work with consent. This supersedes
the earlier ownership assessment. Our tests remain useful research evidence.
They do not establish a new contribution.

## How to read the ranks

Impact ranks compare the potential effect within each supported path. They
consider wrong output, failed cleanup, deployment correctness, measured model
time and memory. They do not estimate how often users meet the problem.
For example, KV cleanup has a high potential effect, but permanent leakage
and actual producer lease release were not proved.

Preparation ranks compare the evidence already saved and the work still
needed for a PR. Rank 1 is the closest candidate for human preparation.
**No entry is certified for immediate submission.** All need human line review,
a current target base, fresh duplicate checks and the relevant tests on that
base. A large test count cannot replace a missing live execution path.

| Preparation rank | Impact rank | Finding | Present state | Main remaining condition |
| --- | --- | --- | --- | --- |
| 1 | 9 | Dynamo context metadata | Normal baseline failure and candidate pass | Current-base check; Linux/default-feature scope |
| 2 | 2 | vLLM grammar-selected output head | Strongest measured model-speed draft | Restore exact patch; scope and current-base review |
| 3 | 4 | vLLM MLA live-cache restoration | Native synthetic model confirms the corrected write | Supported transfer/attention and trained-model check |
| 4 | 1 | vLLM KV rejection cleanup | Seven-file draft; 43 normal mocked-engine cases pass | Live connector and producer lease witness |
| 5 | 5 | ARM GPT-OSS W4A8 gate/up layout | Native failure repaired; 169 ARM tests pass | Trained GPT-OSS with the reporter's format |
| 6 | 13 | FP8 scalar scratch | Native allocation saving and synthetic model checks | Useful production fallback reachability; supported device |
| 7 | 12 | Triton MLA request-table reuse | Native attention and trained-model output checks | Current base; graph/FP8 serving if claimed |
| 8 | 10 | Compact DeepGEMM warmup routes | Large retained-route memory saving | Total startup memory and real configuration value |
| 9 | 11 | DeepGEMM route metadata | Native tests and synthetic MoE path checks | Representative trained-model and serving value |
| 10 | 6 | Embedding dtype in prefix-cache identity | Wrong cross-dtype cache hit reproduced | Public worker/model path and cache compatibility |
| 11 | 8 | Background Responses terminal state | Twelve normal mocked-engine cases pass | Full HTTP create/retrieve with a real engine |
| 12 | 7 | Responses cumulative output budget | Real HTTP handlers pass with scripted generation | Real model/tool turns; adjacent PR coordination |
| 13 | 3 | Dynamo profiler artifact provenance | Eight-file implementation; source review only | Qualified normal environment; authored tests unrun |

The order is an engineering judgement. It is not a measured score. Profiler
provenance ranks high for potential effect and last for preparation because
the normal execution gate is still open.

## Source and ownership checks for this queue

The fresh upstream metadata reads returned these main heads:

- vLLM: `ff01a6b14f329ccd4162fce309913542e2abcd5b`.
- Dynamo: `2141a9690d670440d729e99771afb2fb53e79284`.

These are reference points, not newly tested builds. The candidates retain
their historical bases below. No candidate was rebased or validated on those
fresh main heads in this report update.

[The ownership packet](unpublished-owner-checks.json) contains the exact
commands, search result identities, selected PR metadata, file lists and hashes.
Its `full_raw_record` path and hash identify the retained complete issue/PR
comments, bodies and utility-owner diffs. Those raw bytes are local evidence,
outside this published packet. Broad queries that returned 100 rows are capped.
Narrow title searches are also saved.
Search titles and most body text stay in the full raw record. This keeps
external spelling and long source payloads separate from the authored report.
An empty search does not prove that a fix has no owner. Four initial issue
commands used an invalid flag combination. Their errors remain recorded.
Corrected comment reads and full issue reads are separate successful calls.

This is an ownership screen, not a full review of every PR diff or inline
thread. The previous detailed source reviews remain historical evidence.
Repeat the required issue/comment, linked-open-PR and area-open-PR checks
immediately before a proposal. Resolve any direct overlap first.

[The patch provenance packet](unpublished-patch-provenance.json) records local
branch heads, first parents and retained patch hashes. A first parent is not
always the upstream base. In particular, the grammar and MLA table branches
currently point at their base commit. **Checking out those branch names alone
does not recover either patch. Use the saved patch artifacts.**

## 1. Dynamo context metadata consistency

**Impact 9; preparation 1.** Model list and model retrieve can return different
context sizes for one model or alias. A client can then select an incorrect
request limit. The patch uses the same existing projection in the resolver
and both protocol handlers. It changes four existing files.

Patch branch: `feat/model-context-metadata-consistency`.
Candidate: `50722afdfedc8b0e7027fce18b781437ef3ffa27`.
Upstream base: `5f618a58adca23d527763c688b9cc5a322c7efde`.
The branch is retained in a local Git bundle. It is not a public candidate
branch. [Open the recovery instructions and patch][dmetadata-packet].

Completed validation: native HTTP observations first showed 4096 versus 2048.
The later normal Cargo regression failed on the original source and passed
on the candidate. The controlled regression uses the reverse card order:
retrieve is 4096 and list is 2048. Five selected candidate tests passed:
one HTTP regression, two resolver tests and two existing readiness tests.
The cases include aliases, overrides, missing cards and effective zero.
The run used macOS ARM64, Cargo 1.96.1, a reviewed Swagger override,
`--locked --offline -p dynamo-llm --no-default-features` and two build jobs.
An [independent saved-result review][dmetadata-result] confirms the run.

Before submission: review the chosen list policy and all four files. Compare
the current upstream versions. Run the relevant normal tests on the final
base. Add Linux/default-feature coverage where needed by the submission.
No inference or performance result is claimed. The saved follow-up found all
four base files unchanged at `d846fdaed801007e3e1da8879665fcf7de60ec61`;
that does not validate the fresh main above. Open Dynamo #16470 addresses
discovery reconciliation. Its saved scope is adjacent to this projection.

## 2. Grammar-selected output head

**Impact 2; preparation 2.** Narrow grammars permit few vocabulary tokens.
This experimental, off-by-default feature projects those rows before the
normal mask, processors and sampler. Wide or unsupported batches use the
dense path. The final nine-file patch includes precision and startup-memory
repairs found during validation.

Recorded branch: `feat/grammar-sparse-head-research`.
Base and current branch ref: `8530aed2b78a19eb00e242031c22bb78d615eea2`.
**There is no separate committed patch head in that ref.** Recover the exact
[grammar patch][grammar-patch], SHA256
`673f8a91f2c3fedde66a7cb1e4211413596424bddfcf33cf98e49fcecffaeb99`.
The [source manifest][grammar-source] binds every changed file. The old working
directory is not in the current active worktree list.

Completed validation: 82 final native tests and 16 full-model comparisons.
On Qwen3-4B, L4, BF16, TP1 and MRV2, three narrow workloads used 8.2–8.9% less
complete offline request time across three randomized paired rounds.
The unconstrained control had no clear change. A frozen 32-question JSON
check returned 32 valid objects and 10 correct answers on both paths.
Tokens matched. This is not a full GSM8K evaluation. Startup profiles the
maximum selected workspace. A separate FP16/manual-KV run confirms dense
fallback. Changed-file pre-commit passed. [Tests, model harness and draft][grammar-review].

Before submission: recover the patch in a clean review branch, review the
feature's complexity and confirm maintainer interest in this narrow support
scope. Repeat normal tests and the supported model case on the final base.
The saved runs used matching precompiled native support with changed Python
and Triton files, not a full C++ source build. Llama has wrapper tests only.
Do not claim TP, quantized heads, LoRA, speculative decoding or broad serving
support. Open #60566 uses a different screen and excludes structured outputs.
Open #59740 targets a speculative drafter. Open #45400 changes grammar jump
decoding. These are related work; keep the distinction in a future PR.

## 3. MLA live-cache restoration

**Impact 4; preparation 3.** Loading into a reshaped interleaved cache can
write a temporary copy. The actual cache then keeps stale values. The patch
writes the selected block and row indices in the bound storage. It changes
the existing example connector and its existing unit suite.

Local branch: `feat/mla-cache-write-current`.
Head: `cd4754c1f5754b1f8cc1b8b0480a81200e7c849e`.
Base: `8530aed2b78a19eb00e242031c22bb78d615eea2`.
Worktree: `/Users/pacific/.codex/worktrees/example-mla-cache-write/vllm`.
[Current-base patch and native evidence][mla-cache-report].

Completed validation: four current-package CPU regression cases pass; four
CUDA cases skip on CPU. Earlier native CPU/CUDA cases pass. The later paired
H100 model gate uses real external-cache admission and two interleaved FP16
layer views. Original loading leaves the sentinels in place. Candidate loading
restores selected payloads before attention and preserves unselected rows.
Four greedy tokens and 16 selected scores match full recomputation. The model
is a small dummy DeepseekV2 model. It is not a trained quality evaluation.
Changed-file pre-commit passed.

Before submission: validate the supported save/transfer/load path on the final
base with a representative trained MLA model. Check supported cache layouts
and the existing connector contract. The native gate used current Python
with selected older native support. Do not claim a new full build, generic
offload fix or performance improvement. Keep this separate from MLA table
reuse and the save-gather performance prototype.

## 4. KV rejection cleanup across serving modules

**Impact 1; preparation 4.** A lazy engine iterator can reject after the
earlier construction wrapper ends. The remote prefill side can then miss its
rejection notice. This seven-file patch joins construction and iterator
failure cleanup across Chat, Completion and Responses. It sends the notice
at most once and stops rejection cleanup after the first engine output.

Pushed fork branch: [feat/stream-kv-admission-cleanup][kv-branch].
Head: `c72c801883a1eb9355b9ea8863464a6b74c59482`.
First parent: `371745ebd6c12f314402c6c319de2e7ef82c2981`.
Worktree: `/Users/pacific/.codex/worktrees/vllm-stream-kv-admission/vllm`.
[Final test evidence and source record][vfinal].

Completed validation: 43 normal unit cases pass with mocked engine/RPC inputs:
24 Chat, 11 Completion and eight Responses. The candidate host audit failed
after cleanup because it compared the wrong collected-name sets. Independent
saved-result review confirms the 43 test passes. Three original-code cases
then fail at the expected missing-notice assertion. That baseline experiment's
host and strict checker pass the expected-failure contract. The baseline
pytest suite itself fails. A separate independent review of that last actual
result was not completed before the stop.

Before submission: run the proposed real engine and connector test. Show the
request rejection, notice delivery and actual producer lease release. Check
cancellation and iterator lifecycle on the supported public path. Permanent
leakage is not proved. Open #59343 touches the shared helper; #51505 covers
adjacent multi-prompt work. Open #53298 repairs accepted scheduler state after
KV load rejection, which is a different failure boundary. Recheck these diffs
and coordinate before proposing a shared-helper change.

## 5. ARM GPT-OSS W4A8 gate/up layout

**Impact 5; preparation 5.** The affected activation path selects the wrong
gate/up columns. Alternating columns correct the measured native result.

No dedicated committed fix branch is retained in this packet. Use
[arm-w4a8.patch](../contribution-record-20261018/patches/arm-w4a8.patch).
SHA256: `6df2e88a4956c998c6319cf4cbf3ab2dd80cf177b3902d57ca039fac9e114e79`.
The runtime source pin is `837e87e1c5024843b66383ef1bd60ca5672a9575`.
The saved selected-preimage check extends through
`072c0886d53d933a7e1d3da7e8a3a91670cf181d`. This is applicability evidence,
not a build at that later commit. [Native commands and source record][vscout].

Completed validation: the original native result has 35 of 1,024 values outside
tolerance. The candidate passes. The official ARM suite passes 169 cases.
A synthetic two-expert loader/native check also passes.

Before submission: reproduce the failure and repair on trained GPT-OSS using
the reporter's actual compression/checkpoint format. Check the loader packing
contract. Issue #59457 and adjacent #61593 are retained in the fresh ownership
packet. The synthetic format does not establish the reporter's recipe.
Create a clean review branch from the patch only after selecting the target.

## 6. Scalar FP8 scratch reuse

**Impact 13; preparation 6.** The eager scalar fallback can retain one BF16
weight scratch buffer instead of two. The benefit is bounded memory reduction
in that fallback. It is not a generic FP8 or model-speed improvement.

Local branch: `feat/fp8-scalar-scratch`.
Final test-only head: `1804ee56d9395f80659209ac3d93ad73020796d8`.
Native-tested production head: `216fcf143b84e526c8722e67cbb7b8bb31187a7a`.
Production base: `716c5225aefa7aae0628d88a6d58adddbca7c22c`.
Worktree: `/Users/pacific/.codex/worktrees/fp8-scalar-scratch/vllm`.
[Patch record, allocations and model checks][fusion-report].

Completed validation: 54 CUDA records and synthetic plain/online Llama pairs
pass. All 12 paired allocation observations save 4,194,304 bytes for the
1,024 × 2,048 weight. Final production bytes match the native-tested head.
Timing is mixed and includes a slower cell.

Before submission: identify a useful supported production configuration that
actually selects this fallback. Automatic L4/H100 routes usually bypass it.
The SM100 route has source reachability evidence only; native Blackwell
validation is missing. Recheck the final base and alias/lifetime assumptions.
Do not add per-apply savings across layers or call them total model peak.

## 7. Triton MLA request-table reuse

**Impact 12; preparation 7.** Query rows can index the original request table
instead of copying a row for every draft query. This removes an O(BQW)
temporary and copy. Attention arithmetic remains unchanged.

Recorded branch: `feat/mla-implicit-query-metadata`.
Base and current branch ref: `8530aed2b78a19eb00e242031c22bb78d615eea2`.
There is no separate committed patch head in that ref. Use the saved
[MLA patch][mla-table-patch], SHA256
`0e16d1e52a6645cb545215ce978e364ef9f9ec5fb612dd355b94dd10b0bae42f`.
The [source manifest][grammar-source] binds the final four-file patch.

Completed validation: 16 metadata tests; 18 targeted BF16/FP8 cases on L4.
A100 passes nine BF16 cases and skips nine unsupported FP8 cases.
Changed-page/length fixed-query graph replay passes. Five full-model
DeepSeek-V2-Lite-Chat token/logprob comparisons match across all 27 attention
layers; 3,650 draft tokens are accepted. Full-model timings are mixed.
**No stable model speedup is established.** [Tests and model harness][grammar-review].

Before submission: recover the patch in a clean branch and confirm that the
allocation saving warrants the change. Repeat on the final base. Full-model
graphs, FP8 serving and ROCm remain unvalidated. Open #57094 owns the inherited
empty-padding NaN issue. Related #37353 is in another backend. The fresh broad
MLA searches are capped; they do not clear all possible owners.

## 8. Compact DeepGEMM warmup routes

**Impact 10; preparation 8.** Keep compact route information and expand only
the current warmup case. The GEMM work stays the same.

Local branch: `feat/deepgemm-compact-warmup-routes`.
Head: `50e79d62764346e384e6461ade61aa86bb7cce8c`.
Base: `3f466c852cfd3882820af8dd7963ac775174bce4`.
Worktree: `/Users/pacific/.codex/worktrees/core-warmup-count-20261014/vllm`.
[Exact patch, package tests and engine checks][core-report].

Completed validation: 13 normal package CPU cases, 320 native route plans and
eight native GEMM outputs. A real synthetic FP8 MoE engine matches 48 output
tokens, weights and CUDA RNG states. H100 retained route allocation falls
from 77.623 to 0.683 MiB. A small warm helper is about 5.2% slower.

Before submission: measure total startup peak and the value for a relevant
trained-model configuration. Keep the helper regression visible. Refresh
warmup ownership and current source. The saved allocation is not a measured
reduction in total engine peak or startup time.

## 9. DeepGEMM route metadata

**Impact 11; preparation 9.** Count large route sets with less repeated work
and use one block for each tested PSUM launch. The patch changes two production
files and two existing test files.

Local branch: `feat/deepgemm-route-metadata-final`.
Head: `f547bd2e57f3ed811a5cd13debe4713d2b210e5f`.
Base: `3f466c852cfd3882820af8dd7963ac775174bce4`.
No active worktree for this ref is in the current inventory. The branch and
[metadata-current.patch with test records][core-report] remain retained.

Completed validation: 67 current-source H100 cases and both synthetic FP8 MoE
engine arms. Weights, tokens and finite logprobs match. The large-route path
reaches R131072. Three PSUM calls each use one block instead of 32. The earlier
large count component takes 28.614 rather than 50.120 microseconds.

Before submission: prove useful value in a representative full trained-model
path. Check small controls, quantization, final-base source and ownership.
Open #48734 changes count-kernel block sizing and recompilation behavior;
its interaction needs a changed-line comparison before a proposal. Do not
quote the component reduction as serving throughput.

## 10. Embedding dtype in prefix-cache identity

**Impact 6; preparation 10.** Equal embedding bytes can represent different
values in FP16 and BF16. A key based only on bytes can then reuse the wrong
prefix. The draft adds dtype to that identity.

No dedicated committed fix branch is retained in this packet. Use
[prompt-embedding-dtype.patch](../contribution-record-20261018/patches/prompt-embedding-dtype.patch).
SHA256: `f7359d31d5cb59986725de1dc0f3a5c996df64f67e3055cc85d1ca0ae910551e`.
Runtime and later selected-preimage pins are the same as entry 5.
[Exact manager reproduction, tests and commands][vscout].

Completed validation: a real cache-manager probe changes from a wrong 32-token
cross-dtype hit to zero hit. Same-dtype reuse remains. Nine normal candidate
cases pass. A later denied import attempt is an environment failure.

Before submission: exercise the public offline worker/model entry point with
live prefix reuse. Check supported embedding conversion and cache-identity
compatibility. Refresh adjacent #56656 and #53769. Their saved scopes differ,
but the new broad search is capped. No trained-model cache-output result is
claimed by the manager test.

## 11. Background Responses terminal state

**Impact 8; preparation 11.** A stored non-streaming background response can
remain queued after its producer fails. The draft records failure for active
responses and preserves existing terminal states and cancellation.

Pushed fork branch:
[feat/background-response-terminal](https://github.com/spa5k/vllm/tree/feat/background-response-terminal).
Head: `ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`.
First parent: `e80b6c642f21fd5b24439825592f5b9ced36add8`.
Worktree: `/Users/pacific/.codex/worktrees/background-response-terminal/vllm`.
[Normal test evidence and prior failed setup][vfinal].

Completed validation: 22 controlled rows and 12 normal cases pass. The normal
cases cover three late errors, eight terminal-state controls and cancellation.
Engine, renderer and tool inputs are mocked. Host, guest and strict checker
pass. The initial asset-metadata failure ran zero test cases and stays saved.

Before submission: create and retrieve through the public HTTP API with a real
queue and engine. Confirm the failed status and unchanged successful/cancelled
responses. Run the relevant model/API evaluation. Coordinate any overlap with
the open Responses lifecycle work before combining patches.

## 12. Responses cumulative output budget

**Impact 7; preparation 12.** The allowance can reset between built-in tool
turns. This draft tracks one request-wide output budget through those turns.

No dedicated committed fix branch is retained in this packet. Use
[responses-output-budget.patch](../contribution-record-20261018/patches/responses-output-budget.patch).
SHA256: `d4bdc319f2b89281c4a2b77acf85aab5b613fe6fdf9cf5735529100252f77027`.
Runtime and later selected-preimage pins are the same as entry 5.
[HTTP reproducer, normal tests and exact commands][vscout].

Completed validation: six original budget failures and two controls through
real ASGI/Harmony JSON/SSE handlers. The candidate passes all eight HTTP cases
and 18 normal cases. Engine generation, tokenizer and tools are scripted.

Before submission: run real model/tool sequences, streaming and non-streaming
output/usage evaluation on the final base. Resolve the current interactions
with open #47112, #54064 and #58018. Those change tool-call counts, finalization
or item lifecycle. Do not submit this as a fully validated public serving fix
on scripted generation alone.

## 13. Dynamo profiler artifact provenance: blocked

**Impact 3; preparation 13.** A skipped or partial profile must not let final
deployment assembly consume stale fixed-path results. The implementation
carries results from the current run through interpolation and final assembly.
It changes five production files and three existing test files.

Bundle branch: `feat/profile-artifact-provenance`.
Candidate: `8b991fad3a738d672656267a22ff407877839ff9`.
Base: `5f618a58adca23d527763c688b9cc5a322c7efde`.
[Local bundle, patch and recovery instructions][profiler-packet].
This is not a public candidate branch.

Completed validation: independent source review and static checks only.
The nine authored cases have not run. Normal imports, collection, baseline
failure, candidate success and lint have not passed. The retained Python
environment lacks the required dependency closure; some selected suites can
skip at import. The metadata Cargo result does not close this Python gate.

Before submission: use a qualified normal environment. Preserve package
initializers, conftest and plugin discovery. Collect and run the intended cases
with zero skips. Show genuine aggregate selection, original failure and
candidate success. Test skipped/partial profiling and deployment assembly.
Compare current #13770 and #13020 before accepting a new contribution. The
older selected-base equality check is not a current-main build. Keep blocked
until the normal gate and owner comparison pass.

## Retained work outside the new-PR queue

| Finding and patch location | Evidence retained | Reason to hold or exclude |
| --- | --- | --- |
| Utility terminal cleanup: `feat/utility-terminal-cleanup`, `6b80689e4263f918946729083bdd54781733e1ad` | Six original requests pending; six candidate errors; 23 normal mocked-transport cases pass | **Exclude as duplicate.** Open #56416 and #58279 cover this defect. Their reported real-ZMQ/model results are author claims, not our runs. |
| PCP count: `feat/pcp-linear-dispatch-count`, `23d4867fe4c5775b535a0fc2aadbe5cdcdad86d3` | 208 CPU cases; two-H100 synthetic model matches 272 tokens and 816 scores | Open #60538 changes short-prefill ownership. The saved vector count is invalid under that policy. The private correction has source/CPU evidence only. |
| Table/slot fusion: `feat/gather-slot-fusion`, `a40a6eb6a02bd7995452df7ac4f41cb787c7180c` | Native component savings, 14 CUDA cells and synthetic model checks on the old head | Current source successor has only source/mocked evidence. It does not inherit the old native result. Coordinate #60767. |
| Direct segmented mean pooling: initial scout patch/prototype record | 84 correctness cases; L4 component gains; three trained MiniLM pooling checks | Actual worker dispatch and model throughput missing. Coordinate #60035. |
| Direct context-free MLA output: cross-project patch record | Earlier BF16 model time improves 2.05–2.36% | Final FP8 dtype guard has CPU evidence only. Rerun the final source natively before ranking it as prepared. |
| Dynamo planner, NATS collision and session-removal studies | Native/component failures and partial candidate results are retained | Design-policy and owner gates remain. Session work overlaps #16501/#16610. No competing patch is cleared. |
| Dynamo physical-copy LRU: `feat/lru-copy-position`, uncommitted source draft | Native/parity checks; large pressure-case benefit, small/mixed regressions | Workload frequency and representative application value unknown. No committed candidate head. |
| N-gram replay, split-table caller, serializer and deadline index | Useful negative results and failed assumptions | No useful larger-model gain, complete-call regression, weak total benefit or storage/regression cost. Do not submit from component numbers. |

Existing public PRs, including closed proposals, are listed in the main report.
They are outside this unpublished queue. This update does not reopen them.

## Manual handoff

1. Select one candidate and its exact artifact. Review every changed line.
2. Verify the branch or patch hash against the provenance packet. For grammar
   and MLA tables, recover the patch; their branch refs alone hold no fix.
3. Choose the final upstream base in a separate clean checkout. Preserve the
   existing working trees and other chats' changes. Do not combine independent
   drafts and then claim their individual tests cover the stack.
4. Repeat issue comments, linked-open-PR and area-open-PR checks. Read any
   overlapping current diff and review discussion. Stop if the fix is owned.
5. Run normal relevant tests and the missing live/model gate stated above.
   Keep original/candidate commands, source hashes, output and failures.
6. Run the project PR checklist. Explain scope, tradeoffs, duplicate distinction,
   actual tests and model evaluation. Disclose AI assistance.
7. Create a PR only after human review and those conditions are satisfied.

The linked evidence contains the original test selections and harness commands.
Commands from frozen containers require their recorded source and environment;
they are not generic local setup instructions. No new compute budget is active.

Checklist coverage in this update: evidence scope, cause, compatibility limits,
complexity/benefit, ownership and missing test gates were assessed. **Skip:
full current-source changed-line approval and TraceDecay semantic expansion.**
This update prioritizes saved records and documentation. It does not perform a
new product-code safety review or establish unindexed consumers as safe.

[utility-owner]: https://github.com/vllm-project/vllm/pull/56416
[rpc-owner]: https://github.com/vllm-project/vllm/pull/58279
[dmetadata-packet]: /Users/pacific/.codex/research/dynamo-2026-10-17/experiments/frontend-context-candidate-record-9490/README.md
[dmetadata-result]: /Users/pacific/.codex/research/dynamo-2026-10-17/notes/frontend-context-result-review-9539.md
[profiler-packet]: /Users/pacific/.codex/research/dynamo-2026-10-17/experiments/profiler-artifact-candidate-record-9550/README.md
[grammar-patch]: /Users/pacific/Developer/dynamo-audit/20261015/pr-ready-core/evidence/grammar.patch
[mla-table-patch]: /Users/pacific/Developer/dynamo-audit/20261015/pr-ready-core/evidence/mla.patch
[grammar-source]: /Users/pacific/Developer/dynamo-audit/20261015/pr-ready-core/evidence/final-source-provenance.json
[grammar-review]: /Users/pacific/Developer/dynamo-audit/20261015/pr-ready-core/REPORT.md
[mla-cache-report]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/core-radical-20261015/REPORT.md
[kv-branch]: https://github.com/spa5k/vllm/tree/feat/stream-kv-admission-cleanup
[vfinal]: ../contribution-final-20261018/REPORT.md
[vscout]: ../contribution-record-20261018/REPORT.md
[fusion-report]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/core-budget-validation-5h-20261015/REPORT.md
[core-report]: /Users/pacific/Developer/vllm/benchmarks/local_speed_audit/core-finalize-20261014/REPORT.md

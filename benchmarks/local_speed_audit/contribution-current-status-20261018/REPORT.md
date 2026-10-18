# vLLM research: current findings and deep fixes

This record joins the detailed research report and the later fix records.
The work is saved on Kamran's fork. It is not an upstream submission.
The source branches are separate drafts. They are not one tested combined patch.

## Reports to read or use for a recording

1. [Full research report](../contribution-record-20261018/REPORT.md): the five
   initial candidates, root causes, original/candidate results, costs, rejected
   leads, source versions and remaining checks.
2. [KV admission fix](../contribution-deep-fix-record-20261018/REPORT.md): the
   seven-file request and cache cleanup change.
3. [Utility terminal cleanup](../contribution-utility-terminal-record-20261018/REPORT.md):
   pending RPC futures and engine shutdown.
4. [Background Responses fix](../contribution-background-terminal-record-20261018/REPORT.md):
   stored status after background generation errors.

The reports contain the test commands and evidence links. They separate real
native or normal-suite tests from selected-method tests with fake inputs.
They also identify the source versions that each result covers.

## Strongest initial findings

| Finding | Observed result | Remaining validation |
| --- | --- | --- |
| ARM GPT-OSS W4A8 activation layout | Original native case has 35 of 1,024 values outside tolerance. Candidate passes. The official ARM suite passes 169 cases. | Trained GPT-OSS output and the reporter's checkpoint format. |
| Responses output limit across tool turns | Six original budget failures and two controls. Candidate passes all eight real ASGI/Harmony cases. A normal candidate suite passes 18 cases. | Real model/tool evaluation and adjacent PR coordination. |
| Prompt embedding dtype in the prefix-cache key | A wrong 32-token cache hit becomes no hit. The candidate suite passes nine cases. | Public worker/model path and cache compatibility. |
| Segmented mean pooling | 84 correctness cases, native L4 component timings and three trained MiniLM pooling output checks. | Actual vLLM worker dispatch and model throughput. Component speed is not model speed. |
| MRV2 preparation fusion | Source review and 459 mocked cases. | Native device correctness, model output and performance. |

These are distinct candidates. The full report gives their exact scope and
limitations. None is ready for an automatic upstream PR.

## Substantive fixes prepared after the initial report

### KV admission failure and cleanup

The request can fail when its lazy engine iterator starts. Cleanup at the
earlier request construction point does not cover that failure. A disaggregated
request can therefore miss the rejection notice and retain cache-side state.

The draft coordinates four production files and three existing test files.
It covers serving rejection paths and uses the existing cache-side notice
contract. The separate scheduler test is a distinct validation target.

Source commit: `c72c801883a1eb9355b9ea8863464a6b74c59482`.
Branch: `feat/stream-kv-admission-cleanup`.
The commit is pushed to `spa5k/vllm`.

The selected-method comparison passes eight original/candidate rows. It uses
fake engine inputs. It does not prove a live connector, producer lease release,
public HTTP behavior or a running model.

The new source review identifies 43 normal serving test candidates. Chat has
24 rows. Completion has 11. Responses has eight. The selection uses mocked
engines. Chat and Completion need the small real GPT2 tokenizer cache.
The saved cache has six regular files, five internal links and 2,854,606 regular
bytes. It contains no model weights. All 43 tests still need an actual normal
collection and run under the new CPU policy.

The source plan has eight exact overrides: the seven final files and the base
Responses context. This removes an unrelated cached budget patch. It must not
silently combine the background or output-budget candidates.

### Engine death and utility futures

A utility request can remain pending when the engine ends. Terminal cleanup
must settle pending futures and clear their registry. The draft also covers
registration and terminal-state ordering.

Source commit: `6b80689e4263f918946729083bdd54781733e1ad`.
Branch: `feat/utility-terminal-cleanup`.
The commit is pushed to `spa5k/vllm`.

The controlled comparison has 12 passing rows. Six original rows stay pending.
The six candidate rows raise `EngineDeadError` and leave an empty registry.
Real futures, bounded tasks and caller threads are used. All owned tasks and
threads finish. Engine, ZMQ, monitor, model and public HTTP behavior are not
covered by that comparison. The 23 selected normal rows remain unrun.

### Background response terminal status

A stored non-streaming background response starts as queued. A later ordinary
generation exception can end the task while GET still returns queued. The
draft changes an active stored response to failed. It preserves an existing
completed, cancelled, incomplete or failed state.

Source commit: `ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`.
Branch: `feat/background-response-terminal`.
The commit is pushed to `spa5k/vllm`.

The selected-method comparison passes 22 ordered rows. It uses a fake producer
with real bounded asyncio tasks and locks. It covers the worker, retrieval and
public cancel methods. It is not a full create, real queue admission, ASGI,
engine or model test.

The normal-suite selection has 12 rows: three generation errors, eight terminal
state rows and one cancel row. The eight terminal rows are four states crossed
with a raised exception or a returned `ErrorResponse`.

The first local CPU attempt stopped before origin discovery or pytest. One
runner record still described the earlier 92,927-byte test file. The approved
mount had the correct 87,013-byte test file. The asset size check rejected the
mismatch. This was a runner metadata failure. It was not a test failure or a
production failure. No unit-test row ran in that attempt.

The container exited with code 70. The host rejected it and exited with code 1.
The container had no OOM and no live PID at exit. Exact removal and three empty
absence inventories passed. An independent failure-only audit checked all
saved run and invocation files. No success receipt was made.

The metadata correction passed a new independent source review and a fresh
full input check. The second local attempt collected the exact 12 rows and
passed all 12. JUnit has zero failures, errors or skips. The three normal
project conftests and pytest-asyncio loaded. The host, guest and strict saved
result checker exited with code zero. The guest took 103.215 seconds. The
full host lifecycle took 107.889 seconds. Exact removal and all three absence
checks passed. The first failed attempt remains unchanged.

This normal run uses the real serving methods with mocked engine, renderer
and tool inputs. It runs the three late generation errors, eight terminal
state cases and public cancel case. The source draft is unchanged from
`ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`.

The runtime is the retained ARM64 CPU environment with Python 3.12.12 and
Torch 2.14.0+cpu. The selected Python source and retained native extension
have exact saved identities. This is not a complete current-main build or
native ABI proof. Real queue admission, public HTTP, connector delivery,
model serving and model output evaluation remain unproved.

The complete result and invocation packets are immutable. An independent
agent passed 1,056 saved-data checks and three negative controls. The reviewer
did not rerun the target. The compact [evidence index](evidence-index.json)
links the exact full packets. It includes the raw test result, decoded JUnit,
phase output, cleanup records and independent reviews.

## Work rejected or held

The research checks issues with comments, issue-linked open PRs and area open
PRs. An open PR that covers the same fix excludes a new duplicate patch.
The source and ownership checks are bounded observations at saved versions.
They are not a permanent guarantee that no new PR exists.

- Beam sibling cleanup is already covered by open PR 60550.
- Distributed utility reply recovery is owned by PRs 57846, 60290 and 60401.
- Parallel child-abort parent retention is owned by PR 51629. Adjacent
  registration rollback is owned by PR 56212.
- The PP send audit found no supported new buffer-reuse counterexample.
- The rank-three reduction example has no supported production caller.
- MNNVL, CMake and small logits leads have existing owners or fixes.
- Prompt width and some normal test routes retain environment validation gaps.

The detailed records retain failed experiments and rejected leads. They are
not discarded or counted as successful tests.

## Goal and schedule

The active goal now prioritizes supported defects that cross core engine,
worker, scheduler, KV/cache or serving boundaries. File count is not a reason
to make a change. Each fix needs a root cause, a supported caller and relevant
tests. The next validation priority is the seven-file KV admission fix.

The heartbeat runs every 20 minutes. It continues meaningful research batches.
It ends on **19 October 2026 at 17:58 Asia/Kolkata / 12:28 UTC**. It must then
write the final ranked report and pause. Kamran will handle upstream posting
and must review every changed line before submission.

## Cost and storage state

The total compute limit remains USD 10. The retained guarded estimate is
**USD 2.9192748**. This is not an invoice or a current account balance.
The two new local CPU attempts have no paid compute cost. No new paid job ran in
this update. The separate paid-launch ownership hold remains active.

The local runner uses the existing cached image and frozen environment. It
does not copy a model, wheel, environment or complete source tree. The SSD
reserve remains 20 GiB after the conservative planned peak. The filesystem
reported 70,875,340,800 free bytes at 16:20 UTC on 18 October. Both local test
containers were removed. No new paid remote resource was created.

## Before an upstream submission

A human must understand the complete change and review every changed line.
Repeat the duplicate checks near submission. Run the relevant normal tests and
required serving/model evaluations. Run the repository PR checklist. State the
test results, missing validation, duplicate-work reason and AI assistance.
No upstream PR, issue, comment or review has been created by this research.

# Final vLLM contribution research report

Research stopped on 18 October 2026 at Kamran's request because his usage was over.
The schedule is paused. All three research agents are stopped. No new goal was
created. No new test, model job or paid job will start.

## Reports for a recording

- [Full initial research report](../contribution-record-20261018/REPORT.md).
- [Deep fix and branch index](../contribution-current-status-20261018/REPORT.md).
- [KV normal-test evidence](../contribution-kv-normal-validation-20261018/REPORT.md).
- [Final evidence index](evidence-index.json) and [stop state](final-state.json).

This final report updates the older test states. Earlier reports and failures
remain unchanged. The branches are separate drafts. They have not been tested
as one combined patch. No upstream PR, issue, comment or review was published.

## Best substantive draft: KV rejection cleanup

A request can fail when its lazy engine iterator first advances. A cleanup
wrapper around the earlier request construction has already ended at that
point. The remote prefill rejection notice is then missed. Cache-side state
can remain until a later expiry. A permanent memory leak is not proved.

The draft adds request-local cleanup with at most one rejection notice. It
joins construction and iterator failure paths. It covers Chat, Completion and
Responses. It stops rejection cleanup after the first engine output. The patch
changes four production files and three existing test files.

Branch: [feat/stream-kv-admission-cleanup](https://github.com/spa5k/vllm/tree/feat/stream-kv-admission-cleanup).
Source commit: `c72c801883a1eb9355b9ea8863464a6b74c59482`.

- The candidate passed 43 normal unit cases: 24 Chat, 11 Completion and eight
  Responses cases. Normal conftests and pytest-asyncio loaded.
- That run's host audit exited with code 1 after exact cleanup. A saved helper
  compared eight Responses names against all 43 collected names. The container
  exited with code 0. Independent review confirmed the 43 passing tests from
  the saved collection, raw output and JUnit. No successful host result was
  invented, and the tests were not rerun to hide this audit defect.
- The final original-code run used three unchanged regression cases and the
  four original production files. All three failed at the expected missing
  notice assertion. Pytest exited with code 1. There were no import errors,
  fixture errors or unrelated test failures. The experiment host and strict
  saved-result checker exited with code 0 because this exact failure was the
  required result. The baseline suite did not pass.
- The baseline guest took 116.201 seconds. Its host lifecycle took 121.792
  seconds. The exact container was removed. Three absence checks were empty.
- The original-code result is sealed. A separate independent actual-result
  review was not completed before Kamran stopped the work.

These are normal unit tests with mocked engine and RPC inputs. They prove the
selected failure and candidate behavior. They do not prove actual producer
lease release through a live NIXL connector, a public server or a model.
Unstarted iterators and cancellation before the first advance remain separate
questions. No supported default-server witness was found for that extra lead.

Open PR 59343 touches the shared helper. Its saved source did not cover the
selected late iterator failure. Human coordination is still required. Open PR
51505 covers adjacent multi-prompt work. Refresh all ownership checks before
any upstream proposal. A useful next test would use the existing real-engine
suite and an exact producer lease witness. That test was designed but not run.

## Engine utility futures

When an engine receiver ends, a pending utility future can stay unresolved.
The draft settles pending futures with EngineDeadError, clears the registry,
and handles registration, send failure and terminal-state ordering.

Branch: [feat/utility-terminal-cleanup](https://github.com/spa5k/vllm/tree/feat/utility-terminal-cleanup).
Source commit: `6b80689e4263f918946729083bdd54781733e1ad`.

The controlled comparison had six original requests remain pending. The six
candidate requests raised EngineDeadError and left an empty registry. The
final normal suite passed all 23 cases with zero failures, errors or skips.
The cases use real futures, tasks and bounded caller threads. The engine
transport is mocked. They cover receiver termination, send errors, task
cancellation, late replies, terminal registration and sibling-error controls.

The guest took 94.195 seconds. The host lifecycle took 99.785 seconds. The
guest, host and strict checker exited with code 0. Exact removal and three
empty absence checks passed. Independent review passed 1,154 saved-data checks
and three negative controls.

The review has one explicit evidence limit. The original completion tool
object and sealing tool object were not saved. The actual completion receipt,
three host tool records, before/after observations and strict-checker object
were retained and verified. Do not claim that every delivery tool object has
an independently saved original copy. This does not prove real ZMQ, Ray,
EngineCore, public API, model, device or performance behavior.

## Background Responses status

A stored non-streaming background response can stay queued after an ordinary
generation exception ends its task. The draft marks an active stored response
as failed. It preserves existing terminal states and cancellation behavior.

Branch: [feat/background-response-terminal](https://github.com/spa5k/vllm/tree/feat/background-response-terminal).
Source commit: `ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`.

The controlled comparison passed 22 rows. The normal suite passed 12 cases:
three errors, eight terminal-state controls and one cancellation case. The
guest, host and strict checker passed. Independent review checked the saved
result. The first metadata-only failed attempt remains recorded with zero
test cases. Real queue admission, HTTP, engine and model evaluation are still
missing. The detailed linked report contains the exact commands and evidence.

## Initial contribution candidates

| Priority | Candidate | Strongest saved evidence | Missing validation |
| --- | --- | --- | --- |
| 1 | ARM GPT-OSS W4A8 activation layout | Original native result has 35/1,024 values outside tolerance. Candidate passes. Official ARM suite: 169 passes. | Trained GPT-OSS output and reporter checkpoint format. |
| 2 | Responses output budget across tool turns | Six original failures plus two controls. Candidate passes eight real ASGI/Harmony cases and 18 normal cases. | Real model/tool evaluation and adjacent PR coordination. |
| 3 | Prompt embedding dtype in prefix-cache key | Wrong 32-token cross-dtype hit becomes no hit. Same-dtype control remains. Nine normal cases pass. | Public worker/model path and cache compatibility. |
| 4 | Segmented mean pooling | 84 correctness cases. L4 component speedup: 2.88–6.93x cold and 4.18–33.51x warm. Three trained MiniLM pooling checks agree. | Actual worker dispatch and model throughput. Component speed is not model speed. |
| 5 | MRV2 preparation fusion | Source review and 459 mocked cases. | Native GPU correctness, model output, performance and PR 60767 coordination. |

The initial full report has the source identities, patch artifacts, exact
commands, output tolerances, cost records and individual limits. These five
candidates are distinct from the three later lifecycle drafts. This ranking
is a review order, not a statement that an upstream submission is ready.

## Deeper leads rejected or held

Each accepted lead required issue comments, linked open PRs and area searches.
The saved checks are bounded observations. They do not prove future absence
of duplicate work.

- EPLB collective/drain recovery overlaps open PR 57905 for issue 57883.
- LoRA unload and failed activation overlap open PRs 54939 and 61618.
- Worker memory accounting overlaps open PR 55828. PR 45534 is an alternative.
- Beam sibling cleanup overlaps PR 60550. Distributed utility/RPC recovery
  overlaps PRs 57846, 60290, 60401 and 60940.
- Parallel child-abort retention overlaps PR 51629. Registration rollback is
  adjacent to PR 56212.
- PP send retention had no supported new reuse counterexample. A rank-three
  reduction example had no supported production caller.
- A new quantized-worker screen was interrupted at the user's stop. It has no
  accepted finding, patch or test result.

The latest saved main SHA is
`ff01a6b14f329ccd4162fce309913542e2abcd5b`. The final beam-only upstream
commit did not change the ten selected KV/context/utility source paths.
This is selected source applicability. It is not a full current-main build,
native ABI check or model evaluation.

## Final cost, SSD and resource state

The total compute ceiling remains USD10. The guarded saved estimate is
USD2.9192748. It is not an invoice or live credit balance. No new paid compute
ran in the deeper-fix phase or after the stop. The locked ledger is unchanged.
The paid-launch ownership hold remains active. Its proposed repair was not
adopted or tested. Research infrastructure work is not a vLLM contribution.

The final local free-space measurement and exact ledger hash are in
final-state.json. About 67.5 GB was free at the stop. No environment, model,
wheel or full source-tree copy was added for finalization. All completed local
targets have exact removal and three empty absence checks. No target is left
running from these final experiments.

The last saved Modal inventory had 26 owned apps stopped with zero containers
on 17 October at 23:28:35 UTC. No remote resource was started in this phase.
No fresh remote inventory is claimed. Other chats' resources were not touched.

## Handoff

The final report and compact evidence are committed to the existing report
branch on spa5k/vllm. The three source drafts were already signed and pushed.
Large environments, model assets and full raw runtime trees stay out of Git.
The evidence index points to their sealed local packets.

Kamran must review every changed line, refresh ownership checks, run the
missing engine/model/device tests, and explain the change before submitting
upstream. AI assistance must be disclosed. Research and the finite schedule
remain stopped until Kamran gives a new instruction.

## Record checks

The exact 20 staged files match this record. All JSON files pass strict parsing.
Three copied evidence reports retain their original extra blank line at EOF.
The full whitespace check reports only those three preserved copies. The new
report and all other files pass the whitespace check. No subject test was
run again during finalization.

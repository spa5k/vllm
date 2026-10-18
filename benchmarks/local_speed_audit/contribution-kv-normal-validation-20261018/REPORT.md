# KV admission cleanup: normal unit-test evidence

The seven-file KV cleanup draft now has a saved normal pytest result of
43 passes. The host audit failed after cleanup because its shared helper
filtered only Responses case names. This host failure remains on record.
No repeat run was used to change that result.

Independent review supports the saved unit result. It passed 1,035 source
and data checks and two negative controls. Its decision is
`PASS_FAILURE_DATA_AUDIT`. This confirms the separate unit and host outcomes.
Read the [full audit](evidence/kv43-independent-audit.txt) and
[audit result](evidence/kv43-independent-audit.json).

Read the [current research index](../contribution-current-status-20261018/REPORT.md)
for all initial findings and later fixes. Read the
[detailed KV fix report](../contribution-deep-fix-record-20261018/REPORT.md)
for the root cause, patch design and earlier original/candidate comparison.
Those earlier reports keep their original evidence dates.

## What the fix does

A streaming create call can return before its engine iterator starts.
An initial queue rejection then occurs after the old cleanup wrapper ends.
The producer can miss the existing rejection notice. This can delay release
of remote-prefill cache state. A permanent leak is not proved.

The draft carries one request-local cleanup state through the create call
and the first lazy engine attempt. It attempts the existing notice once
for the two supported queue rejection types. It stops this notice after
the first engine output. Completion is limited to one normal engine input.
The change does not establish admission state from the absence of output.

The draft changes four production files and three existing test files.
The signed source commit is
[`c72c801883a1eb9355b9ea8863464a6b74c59482`](https://github.com/spa5k/vllm/commit/c72c801883a1eb9355b9ea8863464a6b74c59482).
It is pushed on `feat/stream-kv-admission-cleanup` in `spa5k/vllm`.
The production source did not change for this validation run.

## What ran

| Normal suite | Collected | Passed |
| --- | ---: | ---: |
| Chat | 24 | 24 |
| Completion | 11 | 11 |
| Responses | 8 | 8 |
| Total | 43 | 43 |

The raw pytest output reports `43 passed, 39 warnings in 26.73s`.
The XML has 43 cases, zero failures, zero errors and zero skips.
Normal project conftests and pytest-asyncio were active.
The exact collection IDs and XML case identities match the frozen source plan.
The [raw XML](evidence/kv43-junit.xml),
[test output](evidence/kv43-stream_test.stdout.raw) and
[collection output](evidence/kv43-stream_collection.stdout.raw) are retained.
The full argument lists are in the [guest record](evidence/kv43-guest.stdout.raw).
The [phase commands](commands.json) also give the exact argv arrays, exit
codes and measured phase times. They refer to the retained frozen runtime.

The real serving methods ran with mocked engine and notice RPC inputs.
Chat and Completion used the real cached GPT2 tokenizer and renderer.
Responses used mocked renderer, Harmony context, tools and consumer inputs.
This is unit validation. It is not a public HTTP, real connector, running
engine, model output, GPU, native ABI or performance result.

The offline ARM64 container used Python 3.12.12 and Torch 2.14.0+cpu.
Eight exact read-only overrides supplied the seven candidate files and
the original Responses context. The unrelated output-budget and background
drafts were not combined with this source view.
The retained native provider and other Python files form a selected test
environment. This is not a complete build of current upstream main.

## Why the host failed

The guest validated all 43 collection IDs and exited with code zero.
The host then called an inherited collection helper. That helper retained
only the eight Responses names. It compared those eight with all 43 expected
names and raised an assertion. The 24 Chat and 11 Completion names were
discarded by the helper. Pytest name escaping was not the cause.

The host exited with code one. Its failure occurred after exact container
removal and three complete absence checks. The saved guest result is intact.
No success controller receipt or strict-root-checker pass was created.
The [host error](evidence/kv43-host.stderr.raw),
[lifecycle record](evidence/kv43-lifecycle.json) and
[failed completion record](evidence/kv43-failed-completion.json) preserve
these separate outcomes.

Two earlier source failures are also retained. V1 had inconsistent container
labels and never ran. V2 preparation first rejected a large existing input
at its data-reader cap. Preparation then continued with a reviewed larger
reader. That did not change runtime caps or run a target.

## Current source and ownership checks

The fresh upstream reference was
`fe8f2140eeb6103e2ac01fbe2ce40dcc9dba19de`.
All seven original file bodies and the original Responses context matched
that reference. This confirms selected-source applicability.
It does not make the retained test environment a full current-main build.

The review included issue comments, issue-linked open PRs and area searches.
PR #59343 still changes the shared rejection wrapper. Its approach covers
the create-call admission state. Its checked diff has no endpoint lazy
iterator guard. The draft is distinct, but a later upstream submission
needs human coordination and a rebase around that shared helper.
PR #51505 covers the separate multi-prompt Completion restriction.
The draft excludes that multi-input notice scope.

## Next checks and resource state

A separate three-case baseline plan will run one existing regression case
per endpoint against the original four production files. The expected result
is three failures at the missing-notice assertions. This is a prediction
until the baseline runs. The candidate's 43-case run supplies the green side.

Real connector delivery, producer lease release and model/server validation
remain open. Unstarted streams and admission before the first output remain
explicit limits. A separate source audit found a conditional header-send
gap, but did not prove reachability on the default Uvicorn path. No new bug
or patch was accepted from that condition alone.

This run used one CPU, 4 GiB memory, 128 PIDs and 2 GiB temporary space.
It had no network, devices, ports, new volumes or model weights.
The guest took 137.654 seconds. The full owned lifecycle took 148.260 seconds.
The exact container was removed. All three absence inventories were empty.
No resource from another chat was changed.

No new paid compute ran. The guarded saved estimate remains USD2.9192748
of the USD10 total limit. This is a reservation estimate, not an invoice.
The Modal process ownership hold remains active. Its proposed launcher
repair is research infrastructure, not a vLLM contribution finding.

The goal and finite 20-minute schedule remain active until 19 October 2026
at 12:28 UTC / 17:58 Asia/Kolkata. No upstream PR, issue or comment was posted.
AI assistance was used. Kamran must review every changed source line and
complete the remaining checks before an upstream submission.

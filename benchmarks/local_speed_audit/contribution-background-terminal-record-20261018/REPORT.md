# Background Responses terminal-state contribution record

## Status

This record describes a reviewed local contribution draft. The source branch is `feat/background-response-terminal`. The source commit is `ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`, based on `e80b6c642f21fd5b24439825592f5b9ced36add8`.

The fork branch was pushed and verified by `ls-remote`. No upstream pull request was opened. No issue, review, or public comment was posted.

The normal vLLM test rows and a real serving evaluation are still unrun. The draft is not upstream-ready.

## User-visible problem

The problem affects the Responses API when the server store is enabled with `VLLM_ENABLE_RESPONSES_API_STORE=1`. The request uses `background=true`, `stream=false`, and stored output. The server store is disabled by default.

The create call stores a response with status `queued`. The engine generator is lazy, so the background task consumes it after the create call returns. A late admission or generation error can then occur.

The old worker handled a returned `ErrorResponse`, but it did not handle an ordinary exception. Its done callback removed the task entry while the stored response stayed `queued`. A retrieve call could keep returning `queued` with no producer task.

This is a stored state-transition defect. It is not a schema-only defect. It is not proof of a permanent KV or connector leak.

## End-to-end path

`ResponsesRequest` defines the public request fields. The router exposes create, retrieve, and cancel endpoints. The create path validates the store setting, renders the request, and creates the lazy engine generator.

The create path stores one `ResponsesResponse` with status `queued`. It creates the nonstream background task and records it in `background_tasks`. Its done callback removes only the task entry.

`responses_full_generator` consumes the lazy generator. It catches `CancelledError`, but it does not catch ordinary generation exceptions. `AsyncLLM.generate` can raise `QueueOverflowError`, `MaxQueuedTokensError`, or `EngineGenerateError`.

Responses processing can also raise `GenerationError`. The old `_run_background_request` let such exceptions escape. `retrieve_responses` reads the stored object only.

`cancel_responses` writes `cancelled` before it cancels the task. The repair preserves this ordering.

## Repair

The production change is in one method. It catches `Exception` around the full generator, but it does not catch `BaseException`. It does not add a `CancelledError` handler.

The method logs the ordinary exception with the response ID. It joins the exception path with the returned-error path. It then takes the existing response-store lock.

The method changes only `queued` or `in_progress` to `failed`. It preserves `completed`, `cancelled`, `incomplete`, and `failed`. It keeps the same stored object and response ID.

The existing done callback removes the task entry. The patch does not change the protocol schema, router, retention, stream replay, or engine admission. It does not claim connector cleanup.

## Cancellation and terminal races

The response-store lock defines the terminal commit order. If public cancel commits first, the state stays `cancelled`. If failure commits first, the state becomes `failed`.

A retrieve call can see the state before or after the lock commit. The caught worker completes only after the terminal commit. The selected-method comparison checked both cancel forms.

One fake producer returned an error after cancellation. One fake producer propagated `CancelledError`. Both variants recorded one cancellation with empty arguments and returned the same response object from cancel.

The returned-error case did not log cancellation identity. The propagated case did log cancellation identity. The production catch remains limited to ordinary `Exception`.

## Changed files and identities

The source commit changes these two files:

- `vllm/entrypoints/openai/responses/serving.py`
- `tests/entrypoints/openai/responses/test_serving_responses.py`

The commit reports 139 insertions and 9 deletions. Production SHA-256 is `aad988091fb7397c7a81a8e3dbf67e5305b2900c7c1948ca9d7481bba5c98927`. Test SHA-256 is `6463ee688eef79b3d35a0d8813b74e84845d3978dcaae86f681717abb6c5722a`.

Patch SHA-256 is `e226f86530a4e32bf5838134d7e3ac077d51d0277c7495822799fb08c9885538`. The cause crosses request, router, serving, engine, task, and store code. The repair stays in one production method, so the two-file change is not artificial file-count padding.

## Proposed existing-suite tests

The draft adds three test functions with 12 declared pytest rows. Three rows cover late `QueueOverflowError`, `MaxQueuedTokensError`, and `EngineGenerateError` exceptions.

These rows use the create, worker, retrieve, and task callback paths. They use a mocked engine generator. Eight rows cover four stored terminal states with both a raised error and a returned `ErrorResponse`.

One row covers public cancel before the first engine output. The 12 proposed normal rows do not include an `in_progress` witness.

The tests check object identity, one unrelated stored object, and task-map cleanup. They use event barriers instead of sleeps. They await the owned task in cleanup.

All 12 rows are unrun. No normal pytest pass is claimed.

## Controlled selected-method comparison

Root ran one reviewed local comparison. The fixture imported no vLLM module. It compiled three exact selected AST methods and copied the exact create-task cleanup callback AST.

The fixture used fake response records and a fake producer. It used bounded asyncio tasks, events, and a lock. It ran 11 cases per variant and produced 22 ordered rows with 15 strict fields each.

The selected `in_progress` case is synthetic compatibility coverage. The current nonstream create path stores `queued`. This case does not prove a public transition into `in_progress`.

The child exited zero and was reaped. Both streams reached EOF, and stderr was empty. No retry or cleanup signal occurred.

Elapsed time was 0.07971587497740984 seconds. Raw stdout SHA-256 is `122865aa058fffd64aa5f78482e1b00748cd2c5f0e0095d7d82e7293718d704d`.

The baseline let ordinary producer errors escape and left active states active. The candidate logged the exact producer error object and changed active states to failed. Both variants preserved terminal states after raised errors.

The candidate preserved incomplete after a returned error. The baseline changed that incomplete state to failed. Success still changed queued to completed.

Every row preserved the healthy sibling identity. Every row removed the owned task entry, and every owned task was awaited. The independent audit passed 447 assertions and 10 negative controls.

This selected-method comparison does not prove full create, HTTP, admission, native engine, or model behavior. It does not replace normal pytest or a serving evaluation.

## Source and hook validation

The exact patch reproduced both candidate files. All production AST outside the worker stayed exact. All existing test and helper ASTs stayed exact.

The author source checker passed 115 checks and 5 negative controls. The independent source review passed 296 checks and 12 negatives. The comparison source review passed 187 checks and 11 negatives.

The pre-commit run completed with exit code zero. Ruff check, Ruff format, Mypy, and repository hooks passed. The source commit has signature status `G`.

The source worktree was clean after the commit. The fork ref resolves to the full source commit.

## Source currency

A later selected-source check used main `fe8f2140eeb6103e2ac01fbe2ce40dcc9dba19de`. The Responses serving file, Responses test file, and environment settings file were byte-identical.

This proves selected-file currency only. It does not prove whole-repository, dependency, build, or runtime compatibility.

## Ownership and coordination

The saved work checked current comments, issue-linked open pull requests, and narrow area searches. The closest seven reviewed pull-request heads stayed unchanged.

PR #49721 owns background stream termination and replay. PR #48454 owns response retention work. PR #35662 owns cancel presentation.

PRs #38190, #40418, and #47184 own nearby error schema work. They do not add this nonstream exception-to-store transition.

Root also checked these adjacent pull requests:

- [PR #51892](https://github.com/vllm-project/vllm/pull/51892) changes input lookup and stream replay.
- [PR #56963](https://github.com/vllm-project/vllm/pull/56963) adds an optional token session store.
- [PR #42883](https://github.com/vllm-project/vllm/pull/42883) signs responses before persistence.

Each exact-head worker AST still equals the old worker AST. None catches an ordinary producer exception. This is bounded evidence, not a global absence proof.

A human must coordinate with the adjacent stream and error owners before a proposal. No coordination message has been sent.

## Separate negative results

[PR #60550](https://github.com/vllm-project/vllm/pull/60550) already owns the online beam-search lifetime repair. No competing beam-search patch was prepared.

[Issue #51986](https://github.com/vllm-project/vllm/issues/51986) has active collective owner work. [PR #53377](https://github.com/vllm-project/vllm/pull/53377) owns its current capability gate.

The nonzero reduce-scatter discrepancy had no new supported trigger. No competing GPU or collective patch was prepared. These negative results do not support the background fix directly.

## Official behavior evidence

The [official background guide](https://developers.openai.com/api/docs/guides/background) treats `queued` and `in_progress` as polling states. It treats the other response states as terminal.

The pinned official SDK [ResponseStatus](https://github.com/openai/openai-python/blob/553703e2d3db379a83e3ead9e40436b7a66f639e/src/openai/types/responses/response_status.py) includes `failed`. The patch does not add a public error object.

The retained live guide and SDK observations support the lifecycle semantics. They are not a pinned complete OpenAPI document. Context7 returned its monthly quota message. No quota upgrade or purchase occurred.

## Limits and failed preparation

The controlled 22-row comparison had no failed row, and the source hooks had no failed hook. Two preparation commands failed before useful data was read.

One command used an unquoted `?` in zsh. One used the wrong retained source file name. Later bounded reads replaced both attempts, and no target ran in either failed attempt.

Saved full files and hashes replaced truncated console displays. No real HTTP request, queue admission failure, or engine generation failure ran.

No model, device, connector release, or response retention policy was measured. No native engine result exists. The earlier normal-conftest cpuinfo denial stays separate.

No denial was weakened or bypassed. The normal 12 pytest rows remain the main source-test gap.

## Required serving evaluation

This is a serving-affecting change. Existing-suite tests and the PR checklist are necessary, but they are not enough by themselves.

Public endpoint and model smoke validation is pending. The relevant evaluation must cover success, cancel, and ordinary failure with a real engine, or use another human-agreed serving evaluation scope.

The evaluation must verify stored terminal status through the public create and retrieve path. It must record the exact model, engine profile, command, and result. No such result is claimed here.

## Human changed-line review

The human submitter must review every changed line. The human must confirm that broad `Exception` is correct for background storage and that the terminal-state contract is correct.

The human must confirm the missing-store assertion for the current store lifetime. The human must confirm cancellation and lock ordering. The human must review all 12 proposed test rows.

The human must run the normal existing-suite tests and inspect fixture failures. The human must run the agreed serving evaluation. The human must repeat duplicate-work checks and coordinate with adjacent owners before publication.

The human must run the vLLM PR checklist before a draft PR. The PR description must list every test and evaluation command and result. It must explain the ownership difference and state that AI assisted the work.

## Next action

Run the exact existing Responses test selection in a reviewed normal environment. Require all 12 new rows to pass, and run nearby unchanged Responses controls.

Do not use the selected-method comparison as a substitute. If collection fails, record the exact fixture or dependency failure. Do not weaken import, process, or network controls to force a pass.

Then run the agreed public serving evaluation for success, cancel, and failure. Record the endpoint, model, engine, and stored response states.

After all checks pass, repeat ownership checks and run the vLLM PR checklist. The human can then decide whether to propose the change.

## Delivery and budget

The fork remote is `https://github.com/spa5k/vllm.git`. The pushed branch is `feat/background-response-terminal`. The pushed commit is `ce0e01324cd451ed985fa8b39ce071e5b8ac3f07`.

The source branch is not an upstream pull request. New paid calls for this contribution are zero. The shared guarded estimate is USD 2.9192748.

The estimate is not an invoice or account balance. The deadline remains `2026-10-19T12:28:00Z`.

Latest observed SSD free space was 73,555,218,432 bytes. This record makes no physical disk-reclamation claim.

The retained ledger is 55,271 bytes. Its SHA-256 is `4b9b4eec4c3c63c5a059d79cebe0d743634f2d48b4b45f7b46d8e6dfa11c8de4`.

The packaging step must copy evidence only. It must not run tests, imports, targets, or network commands.

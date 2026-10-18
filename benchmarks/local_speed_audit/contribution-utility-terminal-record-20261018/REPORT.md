# Engine control requests after receiver shutdown

This is an addendum to Kamran's vLLM contribution research record. It describes
an engine control fault and the repair draft. A controlled comparison now
reproduces pending original callers and terminal candidate results. The draft
still needs normal pytest, real engine checks and human review.

## Problem and user effect

A frontend can send an EngineCore utility request and then lose its reply
receiver. The request caller waits on a future in `utility_results`. The old
receiver puts its terminal error in the separate generation output queue. It
does not fail the utility futures. With no later utility reply, a sync caller
can remain in `future.result()`. An async caller can remain pending until an
external timeout or cancellation intervenes.

The source path reaches public controls. These include `LLM.sleep`, `/sleep`,
`/wake_up`, `/is_sleeping`, and `/release_kv_cache_memory`. The async client also
sends controls to multiple engines and keeps a fixed notification future for
elastic expert parallelism (EEP). This fault does not require a generation
request to exist. Completion of the send does not prove engine execution.

The source proof is exact upstream main
`371745ebd6c12f314402c6c319de2e7ef82c2981`. The original client file has SHA-256
`17167b8151c9f3389fa1d76ce1d11bf67d136b6ed837ed77945817aa4e5cd77d`.
The isolated draft is now based on exact current main
`e80b6c642f21fd5b24439825592f5b9ced36add8`. The current source and test blobs
are byte-identical to the proof base. Its one newer commit changes two unrelated
DeepSeek AMD paths. The ownership refresh retains the complete comparison.

## Cause across the client lifecycle

1. A sync or async utility call registers its private future.
2. Transport send completes. The caller waits for its own utility reply.
3. The receiver exits after engine death, an ordinary receiver error, or shutdown.
4. The receiver reports the error through `outputs_queue`, or resource cleanup
   cancels the receiver. Neither old path settles the registered utility map.
5. The utility caller has no remaining producer for its future.

There are related lifecycle boundaries. A failed send can leave its row behind.
A cancelled caller can receive a late normal reply. A receiver task can be
cancelled before its first coroutine step. A manager shutdown can raise before
later resource cleanup. The EEP fixed future can fail while another await fails
first. A repair must handle these boundaries without changing healthy results
or masking the original send and cancellation errors.

## Repair design

The production change stays in `vllm/v1/engine/core_client.py`. It covers several
client classes and their shared background resources. File count is not the
selection rule. The earlier KV cleanup draft spans seven files and is recorded
in the separate deep-fix addendum.

Background resources own a terminal event and a utility cleanup callback.
Registration checks the terminal event while holding the registry lock. A
terminal transition sets the event before it drains the registry. Future
completion takes place after the lock is released. Thus a sync completion
callback can safely remove its own row.

The sync receiver fails all remaining control futures on exit. Explicit
shutdown and resource cleanup do the same before fallible manager cleanup.
The original manager, coordinator and socket cleanup order remains intact.

The async receiver has a task-done callback. It works even if cancellation
occurs before the coroutine starts. External resource cleanup dispatches future
completion to the existing owning loop. Utility calls reject a terminal or
finished receiver before they register another row. Ordinary request-output
handling keeps its original error queue behavior.

Callers remove only the row that still holds their own future. The reply path
accepts a missing row for a cancelled or completed call. A failed send retains
its own exception. Async early exits retrieve an already-failed private future
to keep exception ownership clear. EEP uses the same registration and cleanup
rules. Its done callback captures the registry and lock rather than the client.
Both EEP commit handlers retrieve a failed fixed future or cancel a pending one
before they re-raise the original sibling error.

## Evidence already complete

The source proof follows the administrative entrypoints, engine wrappers,
sync/async callers, receiver bodies, resource finalizer and engine monitor.
Its packet contains eleven exact upstream source blobs and bounded ownership
searches. It has 72 reachability checks and 84 author data assertions. Those
are source checks, not runtime scenarios.

An independent proof review accepted the source counterexample. A separate
candidate reviewer reconstructed all 18 patch hunks from the exact original
bytes. The result equals the complete candidate bytes. That review checked
23 named AST predicates and five inert source mutations. These are static
controls, not concurrency tests.

Root read the complete final patch and closed both the author and independent
review packets. Root applied the production patch only in the isolated branch
`feat/utility-terminal-cleanup`. Ruff 0.14.0 check and format check passed at the
real production path without an ignored rule. The candidate source hash is
`85f47eaa802dcf4df4a05ae3bcb0fcdcce6dd7bcd7208d49cec10b1175d93b75`.

## Regression design and execution state

The tests extend `tests/v1/engine/test_wake_up_contract.py`. That existing suite
already tests administrative calls with a CPU marker and controlled client
state. The draft keeps its four existing cases. It uses real call and receiver
methods with fake transport. A sync test uses one bounded real caller thread.
Async tests use real futures and tasks on their owning loop.

The proposed cases cover terminal receivers, normal cleanup, a failing manager,
send errors, cancellation, late replies, healthy siblings, pre-start receiver
cancellation, multi-engine gather and the EEP notification future. A controlled
registration boundary is a helper control. It is not a measured thread race.

Root found a draft test gap during review. Cleanup rows originally drove the
receiver before they checked caller settlement. The receiver could hide a
missing cleanup-entry callback. The final draft checks those assertions before
the receiver runs. This was a test design finding, not an observed product failure.

The final draft declares 23 ordinary test rows. Four are the existing wake-up
rows. Nineteen are new. Four new rows exercise both real EEP commit bodies with
an ordinary sibling error or cancellation while their notification future is
already failed. That setup uses a real `asyncio.Future` subclass. It counts
public exception/cancel calls while retaining the real future state. These
four ordinary rows have not run. The real manager constructor and Ray transport
do not run in that test design.

All applicable source hooks passed on the final two-file draft. These include
Ruff check and format, mypy for Python 3.11, test tethering and the repository's
other applicable checks. Initial hook attempts exposed formatting and three
missing test annotations. Those were fixed. Root verified AST equivalence to
the reviewed test proposals apart from those annotations and import order.

Normal pytest is still held by the known ancestor conftest `cpuinfo` import
denial. The CPU marker does not override that gate. The 23 rows are declared
test cases, not 23 measured passes. This is the current research runner
boundary. It is not a vLLM security rule or a product bug. No new normal pytest
attempt was made for this draft.

## Controlled comparison result

One local stdlib comparison selected the exact original and candidate method
bodies by AST. It used real concurrent futures, asyncio futures and tasks, and
one bounded caller thread at a time. Transport and external startup state were
explicit stand-ins. The real selected Sync constructor and Async setup method
installed their own cleanup callbacks.

| Controlled path | Original future | Candidate future |
| --- | --- | --- |
| Sync receiver engine-death marker | Pending; row retained | EngineDeadError; row removed |
| Sync normal resource cleanup | Pending; row retained | EngineDeadError; row removed |
| Async receiver engine-death marker | Pending; row retained | EngineDeadError; row removed |
| Async ordinary receiver error | Pending; row retained | EngineDeadError; row removed |
| Async receiver cancelled before its first step | Pending; row retained | EngineDeadError; row removed |
| Async normal resource cleanup | Pending; row retained | EngineDeadError; row removed |

The corrected comparison passed all twelve rows. Both original and candidate
preserved the ordinary receiver error in the generation output queue. Both
pre-start cancellation rows had zero receive calls. All owned caller threads
joined. All owned async tasks finished. Root recomputed all 28 selected source
definition bindings: twelve original and sixteen candidate definitions.

The child returned zero. Both raw streams reached EOF. Stderr was empty.
The parent measured 0.4700675418 seconds and reaped the exact child. This is
the parent clock measurement, not an engine or request latency benchmark.
The complete 5,175-byte stdout has SHA-256
`581f502d472678db2c424b570847c817d32808143bdef2cb541dba52ed9df119`.
The closed actual result manifest is
`ae9cae8e1119e487c02534b39490b95e35b069a627280de35b464c1185b83edd`.

The independent actual audit accepted the saved rows, source bindings and
cleanup receipt. Its manifest is
`0a56e8359772b7f376e49e1232945cd95a9a7e038080baf75c589917ded1a369`.
Root's original native execution object is retained separately in this record.
That object was not inside the four-file actual packet that the reviewer
audited. No reviewer reran the target.

The first fixture version is retained as failed evidence. It read the
pre-start cancellation state before the queued task-done callback ran. Five
candidate paths completed at that observation point. The sixth looked pending.
The correction added a separate observer callback after production setup and
waited for that callback before it read future state. Production bytes did not
change between the two runs. Python documents that done callbacks are queued
with `call_soon`, and that these callbacks run in registration order.
[Future documentation](https://docs.python.org/3.12/library/asyncio-future.html#asyncio.Future.add_done_callback),
[event loop documentation](https://docs.python.org/3.12/library/asyncio-eventloop.html#asyncio.loop.call_soon).

The first child also finished and was reaped. Its nonzero result was a fixture
observation failure, not a successful 12-row comparison. Both versions and
their exact raw streams remain in the evidence. No retry used unchanged input.

## Duplicate and ownership scope

The original proof retained issue comments, issue-linked open PR searches and
area-keyword open PR searches. Adjacent readiness and health PRs
[60505](https://github.com/vllm-project/vllm/pull/60505),
[59179](https://github.com/vllm-project/vllm/pull/59179) and
[46811](https://github.com/vllm-project/vllm/pull/46811) do not settle the generic
utility registry in the saved diffs. DeepEP sleep buffer work
[59939](https://github.com/vllm-project/vllm/pull/59939) has a different scope.
Issue [40244](https://github.com/vllm-project/vllm/issues/40244) concerns
allocation order. The final ownership refresh found its eleven comments and
the four adjacent PR heads unchanged. Area matches
[51974](https://github.com/vllm-project/vllm/pull/51974) and
[55274](https://github.com/vllm-project/vllm/pull/55274) add utility consumers,
not registry terminal cleanup. No direct same-fix PR was found in these bounded
searches. This does not prove global absence of competing work.

## Limits and next validation

The draft does not add a send timeout. A call can still wait in transport send
before it awaits the future. Async settlement needs its existing owning loop
to run. The draft does not add loop restart or cross-loop client support.

Source extraction with fake transport cannot prove a real ZMQ failure, engine
process death, monitor thread loop dispatch, HTTP request completion, distributed
EEP, model output or performance. Relevant ordinary tests and later real engine
checks remain necessary. Human review of every changed line remains necessary
before an upstream proposal. No upstream PR, issue, comment or review was sent.

## Budget and delivery

This fix has used no new paid compute. The shared ledger retains a conservative
USD 2.9192748 estimate including the network guard. That is not an invoice or
an account balance. The USD 10 total limit and the Modal runtime hold remain.
The research continues until 19 October 2026 at 17:58 Asia/Kolkata.

The earlier full report is on branch
`feat/vllm-contribution-research-20261018`, commit
`0913b8102a48bd5784d50999d4a6a59dbdda2a8c` on Kamran's fork. The earlier KV
cleanup draft is on `feat/stream-kv-admission-cleanup`, commit
`c72c801883a1eb9355b9ea8863464a6b74c59482`. Both remote refs were verified.
The utility source draft is committed and pushed to Kamran's fork:

- Branch: `feat/utility-terminal-cleanup`.
- Commit: `6b80689e4263f918946729083bdd54781733e1ad`.
- Base: `e80b6c642f21fd5b24439825592f5b9ced36add8`.
- Remote: `https://github.com/spa5k/vllm.git`.
- Fresh remote ref matched the local commit. The isolated worktree is clean.
- The commit has the human sign-off, Codex co-author trailer and a good SSH signature.

The [source commit](https://github.com/spa5k/vllm/commit/6b80689e4263f918946729083bdd54781733e1ad)
changes two files, with 667 insertions and 28 deletions. It does not include
research scripts in vLLM's test tree. This is a fork draft. No upstream PR was
created. `DELIVERY.json` records the compact report and source branch context.

# vLLM deep-fix progress — 18 October 2026

This record extends the [first research report](../contribution-record-20261018/REPORT.md).
The first report was pushed in commit `929b667c0e71a1a60458593ac76bbf88c516297a`.
It contains the ranked ARM quantization, Responses budget, prompt-cache identity,
pooling, and other findings, with test results and limits.

The next phase has one substantive candidate. It changes four production
modules and three existing test modules. It addresses a request-lifecycle gap
across the API and engine boundary. File count did not drive the choice.

**State: draft patch. Source review and an extracted-method before/after check
passed. Normal pytest validation is pending. No upstream PR was opened.**

## The new finding

A streaming request can pass the serving preflight and fail engine admission
when its result iterator is first consumed. If the request has remote-prefill
KV metadata, the serving cleanup wrapper has already returned. The queue error
is then formatted inside the stream. The wrapper does not send the existing
remote-prefill rejection notice.

The checked source supports delayed release of the producer's retained KV
blocks until connector cleanup. The retained default lease evidence is
30 seconds. No live producer block retention or permanent leak was measured.
This is separate from the earlier capacity-reservation proposal in issue #58192.

The supported sequence is:

1. The producer completes prefill and supplies remote KV metadata.
2. The decode API passes its early queue check.
3. The API returns a lazy streaming iterator.
4. Another request fills the last queue slot.
5. The first iterator advance raises `QueueOverflowError` or
   `MaxQueuedTokensError` before normal engine registration.
6. The stream emits its existing error output. The old wrapper is no longer
   active, so it sends no rejection notice.

The existing notice RPC can submit an `abort_immediately` cleanup marker.
The NIXL scheduler source handles that marker through its empty-receive path.
The existing test
`tests/v1/kv_connector/unit/test_nixl_connector.py::test_abort_immediately_remote_prefill_enqueues_empty_recv`
is relevant to that path. It has not been run for this candidate.

## Exact source and patch

The candidate is based on upstream
`371745ebd6c12f314402c6c319de2e7ef82c2981`.
The selected source and test preimages are byte-equal to the earlier
`072c0886d53d933a7e1d3da7e8a3a91670cf181d` snapshot. The intervening commit
changes documentation. This is a selected-file statement, not a native-build
or whole-runtime equivalence claim.

The [draft patch](patches/stream-kv-admission-cleanup-draft.patch) has SHA-256
`4053b1c3fc716728211a07e2131e6b29d7ac1dc3056a52ba1d5147cb7c6dc7d4`.
It changes 7 files, with 392 insertions and 29 deletions.

| File | Purpose |
| --- | --- |
| `vllm/entrypoints/generate/base/serving.py` | Share a request-local cleanup guard between the create call and initial engine iteration. |
| `vllm/entrypoints/openai/chat_completion/serving.py` | Guard initial admission for the Chat generator, including atomic parallel sampling. |
| `vllm/entrypoints/openai/completion/serving.py` | Guard the single-input Completion generator. |
| `vllm/entrypoints/openai/responses/serving.py` | Guard only the first engine turn of a Responses request. |
| Three existing serving test files | Cover early and late rejection, once-only notice, RPC failure, admitted output, mixed Completion branches, and later tool turns. |

The guard attempts the notice once. It sets that state before awaiting the
RPC. An RPC failure keeps the original request error. A real `RequestOutput`
marks engine output as observed and prevents a later outer cleanup notice
from releasing that request's remote prefix again.

The patch excludes beam search and the new single-input guard does not cover
multi-prompt Completion requests. One prompt can be admitted while another is
rejected. Releasing their shared transfer metadata from the rejected branch
would require a separate ownership contract. Later Responses turns and
unstarted stream cancellation also need separate analysis.

An accepted request can fail before its first output. Absence of output does
not prove absence of admission. The candidate does not claim to solve that
broader existing cleanup problem.

## Validation completed

Ruff 0.14.0 matches the repository's pinned Ruff version. Its check and format
check passed for all seven final files. All applicable pre-commit hooks also
passed, including mypy, test tethering, SPDX, lazy-import and forbidden-import
checks. Git whitespace checks passed. The seven source hashes stayed unchanged.
Two independent source reviews checked the production change and the final
seven-file candidate. The latter reconstructed all seven files from the patch
and checked the scope, once-only state, ordering, and preserved formatter paths.

One local paired check executed selected source methods with explicit standard
library test doubles. It used the real selected `AsyncLLM` method bodies, the
serving bodies, exception classes, and candidate guard body. It removed function
annotations and decorators through a recorded AST transform. It imported no
vLLM package and used no ASGI server, device, model, or real connector.

| Case | Old code notices | Candidate notices |
| --- | ---: | ---: |
| Early preflight rejection | 1 | 1 |
| Render error | 1 | 1 |
| Late non-streaming rejection | 1 | 1 |
| Late streaming rejection | 0 | 1 |

All eight variant/case rows passed. There were 26 recorded source bindings.
There were no ordinary engine submissions. Error frames and request state
were equal across the two variants. The late streaming frames stayed an error
event followed by `[DONE]`.

The single owned child exited 0 and was reaped. Both output streams reached
EOF. Its complete stdout is retained in
[stream-kv-source-pair.json](evidence/stream-kv-source-pair.json), with the
[execution receipt](evidence/stream-kv-source-pair-receipt.json).
This check proves only those extracted-method contracts. It does not prove
normal pytest success or actual remote block release.

## Validation still required

The test source declares 39 candidate parameter rows. These rows have not been
collected or run. A separate plan selects those rows plus four nearby existing
controls, for 43 serving rows. It keeps normal conftests and real pytest-asyncio.

The serving-only source view uses the seven exact candidate files and restores
the unmodified Responses context file so that the earlier budget patch cannot
affect results. A small existing GPT-2 tokenizer cache view is now closed.
No environment install or download was made.

**Normal imported tests are blocked by the retained execution policy.** Normal
root conftest loading imports `LLM`, which imports `UsageContext`. That module
imports `cpuinfo`. The required runtime observer denies this import. A saved
earlier renderer attempt already proves that collection stops at this boundary.
The earlier successful Responses tests had no such observer. They cannot prove
compatibility under the newer policy. The initial source-feasible test plan is
superseded by [the blocked correction](evidence/normal-test-blocker.txt).

No executable test gate or repeat was prepared after this conflict was found.
The observer, normal conftests, real dependency code, process restrictions and
socket restrictions were preserved. A separately reviewed execution environment
or policy is needed for ordinary pytest. This is an environment-policy block;
it does not establish a serving regression.

The NIXL scheduler test is a separate validation item. Its module imports Ray,
which is absent from the checked cached runtime. Its real model configuration
also needs an accepted OPT configuration and model-info cache view. These
requirements do not establish a failure in the serving patch.

A native connector check, actual producer block-release observation, and human
review of every changed line are still required before upstream submission.
No model accuracy or throughput result is claimed.

## Ownership and overlap

The latest bounded ownership refresh checked current issue comments,
issue-linked open PRs, narrow open-PR searches, and relevant file patches.
Its initial and final upstream reads both returned `371745eb…`.

Open draft [#59343](https://github.com/vllm-project/vllm/pull/59343), head
`a6236f0`, changes the exact base cleanup method. It tracks engine admission
through a context variable. Its focused tests consume `AsyncLLM.generate()`
while the outer wrapper is active. Its checked patch does not guard the lazy
Chat, Completion, or Responses iterators after their create calls return.
The candidate addresses that residual path. This is a material difference,
with an exact same-method overlap that requires human coordination and rebase
review if the draft changes or merges.

Issue [#50425](https://github.com/vllm-project/vllm/issues/50425) owns the earlier
cleanup report. Its last saved comment says the known create-time cancellation
case appears fixed by merged #41269. Open #50565 and #57529 cover other Mooncake
connector paths. Open #42442 covers post-registration engine validation-error
cleanup. Issue #58192 and its closed #58477/#58478 proposals concern pre-render
capacity reservation. The checked patches do not implement this lazy rejection
notice. The search was bounded and cannot prove global duplicate absence.

No issue, PR, comment, review, or message to a person was published. Kamran
will handle upstream coordination after review.

## Other deep leads checked

| Lead | Decision |
| --- | --- |
| Encoder cache after external weight update | Source contract gap, with active related ownership. Held for coordination and a supported runtime case. |
| LoRA path identity in encoder cache | Rejected as direct overlap with open #44950. |
| AutoRound/Marlin input dtype | Rejected as direct overlap with open #49039. |
| Inkling on SM12x | Existing #51560 and #55078 own the selected failure/fallback work. |
| MRV2 row lifecycle and speculative preemption | The checked supported ordering did not produce a counterexample. No patch accepted. |
| Inkling auxiliary stream and tail indexing | The checked source ordering and pinned FlashAttention indexing did not produce a counterexample. No device claim made. |

The raw source checks, failed hypotheses, duplicate searches, draft patches,
and source identities remain in the scout directory. Their entry points and
hashes are listed in [evidence-index.json](evidence-index.json).

## Work and resource state

The substantive patch is applied in the isolated local branch
`feat/stream-kv-admission-cleanup`. Draft commit
[`c72c801883a1eb9355b9ea8863464a6b74c59482`](https://github.com/spa5k/vllm/commit/c72c801883a1eb9355b9ea8863464a6b74c59482)
is pushed to Kamran's fork. Its normal tests remain pending. This report branch
records the draft and evidence; it does not apply the production patch.

The active goal and heartbeat now select substantial fixes with proved causes
across module boundaries. Three agents cover source/ownership review, result
review, and normal test preparation. The finite follow-up runs every 20 minutes
until **19 October 2026, 17:58 Asia/Kolkata**. It will then finish the report
and pause. No continuing run after that deadline is authorized here.

The total new research compute cap remains **USD 10**. The shared ledger's
conservative retained charge is **USD 2.9192748**, not an invoice or account
balance. No paid compute ran in this deep-fix batch. The existing Modal runtime
ownership hold remains active. No credit purchase or plan upgrade was made.
The latest local check had about 76 GB free. The 20 GiB post-peak reserve
remains in force. Other chats' source and resources were preserved.

AI assistance: Codex coordinated the research, source checks, draft patch and
tests. Kamran has not yet completed changed-line review or the missing runtime
validation. This record is not a claim of human-approved upstream readiness.

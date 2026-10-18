# Worker lifetime follow-up

Decision: **NO_NEW_UNOWNED_CONTRIBUTION**. Do not propose a patch or a device run from this packet.

Current primary main is `ff01a6b14f329ccd4162fce309913542e2abcd5b`, committed at `2026-10-18T16:49:42Z`. The new commit is the beam-search generation-config EOS fix, #62072. This packet did not reopen beam work.

## The selected boundary

I read [issue #57883](https://github.com/vllm-project/vllm/issues/57883), its complete one-comment result, its issue-linked open PR search, and a short open `EPLB async` PR search. The report describes a live server with a stalled async expert transfer cycle. It comes from a vendor image based on an older commit. It is reporter evidence, not a current-main reproduction.

Open [PR #57905](https://github.com/vllm-project/vllm/pull/57905) explicitly fixes #57883. Its saved head is `551d2680741d8a07746d11ce0cecfd8a6069638f`. I read all three changed-file patches. They change the readiness collective predicate, the drain predicate, and the event waits in the exact three files at this boundary. This is direct competing work. It is enough to reject another fix. This audit does not approve that PR's implementation or tests.

The exact current source preserves this path:

- `EPLBController.step` calls `EplbState.step` for enabled, registered models.
- The async worker finishes its stream work, publishes `pending_result`, then waits for `consumed_event`.
- The main step gates the readiness collective on `rebalanced`. The consumption path clears `pending_result` before it records the event.
- The current event wait has no explicit timeout. The open PR modifies this same wait and the collective path.

These are source facts. They do not prove that current supported ranks can reach a permanent stall. A negative printed interval count also occurs while a valid async cycle remains in flight. The small inert counter control shows that a later consumption can still reset it. The control has no threads, collectives, devices or production method execution. It does not reproduce the reported stall.

I read the exact current `test_eplb_events.py` as data. Its tests cover record-before-wait, repeated event use, and device buffer ordering. They require real event/device behavior. I did not run them. A useful new CPU proof would need a supported production transition that produces the disputed rank state. This packet does not provide one, and ownership already blocks a competing proposal.

## Excluded work

Saved reports rejected the shutdown-drain report #61561 because #61562 and #61598 own it. They also record #61859 as a duplicate. I did not repeat their live issue searches. The prior collective-RPC fixes #57846/#60290/#60401/#60940, online beam cleanup, and PP unsupported-buffer concern remain excluded. The saved PP audit did not establish a supported recovery write after its fatal exception edge.

The three new broad issue searches returned 30 rows each. Their total counts were 107, 331 and 55. They are capped intake evidence. They do not establish absence of another report or owner. The issue-linked search for #57883 returned its complete one row. The area query returned all 71 rows with `incomplete_results=false`; its keyword scope is still limited.

## Ten-path current-source transfer

Root requested an exact comparison from `fe8f2140eeb6103e2ac01fbe2ce40dcc9dba19de` to `ff01a6b14f329ccd4162fce309913542e2abcd5b`. The primary compare has one commit. Its sole parent is the exact base. It has five changed beam-search paths. A separate direct commit response has the same five names/blob IDs and matching complete diff-stat sums. Page 1 contains 1/1 commits; page 2 contains none. Neither response offers a next page. The five-file result is below the compare API's 300-file ceiling.

None of these ten paths changed on that exact transition:

1. `tests/entrypoints/openai/chat_completion/test_serving_chat.py`
2. `tests/entrypoints/openai/completion/test_completion_error.py`
3. `tests/entrypoints/openai/responses/test_serving_responses.py`
4. `vllm/entrypoints/generate/base/serving.py`
5. `vllm/entrypoints/openai/chat_completion/serving.py`
6. `vllm/entrypoints/openai/completion/serving.py`
7. `vllm/entrypoints/openai/responses/serving.py`
8. `vllm/entrypoints/openai/responses/context.py`
9. `vllm/v1/engine/core_client.py`
10. `tests/v1/engine/test_wake_up_contract.py`

This is a selected upstream Git transition result. It does not compare patched candidate bytes with upstream. It does not establish whole-tree, native ABI or current-runtime equivalence. It does not transfer a previous test observation beyond its stated selected-source scope. Exact receipt hashes and pagination data are in `selected-source-transfer.json`. The file-limit and pagination interpretation follows the [official GitHub commit API documentation](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#compare-two-commits). Its saved read result is in `raw/compare-api-primary-doc-tool.json`.

## Evidence and limits

`source-identities.json` records five exact current Git blobs, lengths and SHA256 values. Their API content was decoded, checked against Git blob SHA1, and parsed as Python AST. No imported module or subject body ran. `source-data-audit.json` records the narrow source checks and the inert counter control. `check_source_data.py` is this agent's own data checker. It ran once and passed. It is not an author or target verifier.

The saved native objects are composed from original nested `exec_command` return objects. They are labelled as that composition. Redirected API files are primary response bodies. No missing native object is represented as an original capture. No target package, method, test, subprocess fixture, device, Docker, Modal, model or paid operation ran. No patch, source edit, environment copy, install or publication was made. All earlier execution holds remain in force.

TraceDecay exploration/tracing guidance was read. The old index is not evidence of current caller absence. Named primary source is authoritative here. Context7 quota was already exhausted in retained PP evidence. I made no new library-contract claim that needs another quota call.


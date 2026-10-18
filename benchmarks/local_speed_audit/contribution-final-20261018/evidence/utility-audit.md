# Utility23 saved-result audit

## Decision

`PASS_SAVED_DATA_AUDIT_WITH_UNSAVED_TOOL_OBJECT_LIMIT`

The sealed run and invocation data support one successful Utility23 normal CPU
attempt. The run manifest is 15,993 bytes with SHA-256
`58c99b63cc31a30483db405418c2c713c7e436e5e699bf80a5bae31661057e58`.
The invocation manifest is 3,792 bytes with SHA-256
`39796d3e8d7767ce0983e6d4a0df999980b274f5f66e0fe4a27c3039a0b03a61`.
All 98 payload files, both manifests, and all declared directories match their
saved size, hash, and mode records.

This review read saved data only. It did not execute the subject, a helper, the
author checker, pytest, a process, a container, or a resource command.

## Unit result

The guest result has exactly three complete phases: origin, collection, and
test. Each phase has the pinned argv and typed exit code zero. The six decoded
phase streams match the six separately saved raw derivatives. The phase times
fit inside the 420-second guest bound.

Collection contains exactly 23 unique node IDs from
`tests/v1/engine/test_wake_up_contract.py`. The IDs match the sealed source
selection. The loaded plugin rows contain the root conftest, the engine
conftest, and pytest-asyncio. The selected distributed conftest is imported as
source but is not registered as a test conftest.

JUnit is 3,518 bytes with SHA-256
`6e1f5d60ffc3240acf8ae98149e67aa74fae085c1fd311a5a23d6d2c8cc9e44b`.
It contains exactly 23 direct and unique testcases. All 23 passed. It has zero
failures, zero errors, and zero skips. Its identities match the 23 collected
nodes. The saved guest verdict has `suite_success=true`, `status=passed`, and
the exact log and JUnit identities.

These tests cover wake-up consensus and utility future lifetime behavior. The
rows include sync and async receiver termination, send errors, pre-start task
cancellation, late replies, terminal registration, gather and EEP notification
settlement, and the four scale-up or scale-down sibling-error controls.

## Source, origin, and provider data

The result binds adapter
`88a55a6ba0bb76cafd2769d06df0b0beb5d04b9847028936775fdce81fd7f1a2`,
family `aed8ac81697fd422b3b7b56d83a22342c1dd88dfcb4f852292e28641e5ae91ed`,
and peer review
`8fb0aeb4e8a37ef54de95fb8d6c2c50a406b6ac9ad703526aac07a7a73435a27`.
The preflight closure has two packet closures, five tree closures, 49 fixed
files, and four providers. It records enough free space after the conservative
peak.

The guest source derivation matches the two exact overrides. The canonical
derived source manifest is 1,434,652 bytes with SHA-256
`7a437570832309f37446eb88fcd8d7cb3f5b111fa2b72b899738a6efad0c4110`.
The candidate, dependency overlay, and seven-wheel overlay receipts have the
expected entry, byte, directory, and mode-relation counts. The freeze receipt
has 56,990 entries and 2,262,611,530 regular bytes.

The origin receipt matches Python 3.12.12, 19 modules, seven added metadata
records, and two added native module records. The Harmony receipt matches all
seven files and both embedded byte ranges. The saved network observation has no
external route claim. The environment remained offline.

## Host lifecycle and cleanup

The call ledger has the exact version, context, image, inventory, create,
prestart, start, 13 poll, log, cleanup, and three absence operations. Each saved
raw stream matches its receipt. The create, start, and removal records use the
same exact CID
`603eb1254ad4557571e5585ece0cf1317af78aff91d9c208610811432ff84a70`.

The full Config, HostConfig, environment, eight read-only mounts, labels, and
resource policy match the command plan. The saved post-start
`OomKillDisable=false` to `null` presentation is the only admitted
configuration transition. The terminal state is exited with code zero, PID
zero, no OOM, no error, and no cleanup error.

The lifecycle lasted 99.78526670788415 seconds. The guest lasted
94.195394418 seconds. All command durations fit the pair clock. Entry and target
freshness bind the exact closure and stay inside their limits. The original
1,500-second batch, 1,380-second normal deadline, and 480-second target window
all hold. The exact CID was removed. The ID, global, and name absence
inventories are empty.

## Root receipts and strict checker

The saved host stdout equals the pair lifecycle record. Host stderr is empty.
The three original host tool records show one started session and a final
completed, reaped exit zero. The saved before and after observations enclose
the pair and root-completion times.

The root completion receipt has SHA-256
`baef6d693675cf9429d5358f58f61ff0bd872705303e7279f099e42710486c33`.
It states completed, reaped, and exit zero. Its member descriptors match the
saved host records and streams. The strict checker receipt has exit zero. Its
exact output matches the saved strict-checker output. The strict result binds
the same source, family, closure, completion receipt, guest verdict, CID,
ledger, freshness, and limited claims.

The original completion tool object identified as `3b73fa` was printed in tool
history but was not saved before sealing. The sealing tool object identified as
`fe72e2` was also not saved. This review does not infer either original object.
It verifies the saved completion receipt, the retained host tool objects, the
before and after objects, and the retained strict-checker object. Therefore it
does not claim that every original delivery tool object has an independently
retained byte copy.

## Limits

The selected tests use mocked engine transport. They use real futures, tasks,
and bounded caller threads inside ordinary pytest. They do not prove a public
API, real ZMQ or Ray transport, real EngineCore, model execution, device
behavior, current native ABI, trained output, or performance.

The normal CPU policy admits cached metadata helpers and local asyncio under
container limits. It does not provide a complete process or native syscall
trace. Root completion remains trusted same-host testimony rather than an
independent operating system lifetime proof.

The independent audit recorded 1,154 source and saved-data checks plus three
negative controls. Those counts are reviewer evidence, not new target tests.


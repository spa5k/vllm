# Deep-fix phase

## Objective

Find, implement and validate substantial supported vLLM defects whose cause
crosses production module boundaries. Prefer a complete request, cache or
worker lifecycle with clear user impact. Do not increase a diff merely to
increase its file count.

This phase starts on 18 October 2026. It keeps the existing deadline:
19 October 2026 at 12:28 UTC, or 17:58 Asia/Kolkata.

## Parallel work

| Lane | Scope | Expected decision |
| --- | --- | --- |
| Core | Scheduler, KV/cache/offload, connector and worker state ownership | Select one supported cross-module failure or reject it with evidence |
| Serving | API, engine lifecycle, request/response state and tool execution | Select one supported protocol/lifecycle failure or reject it with evidence |
| GPU/MRV2 | Device preparation and runner/kernel integration after report audit | Select a substantive unowned invariant; do not reopen coordination-held tiny cases |
| Root | Evidence, independent review, worktrees, Git record, resource and cost gates | Select the strongest viable change and drive it through relevant validation |

The agents reuse prior evidence. Finished negative or owned leads are not
repeated without new evidence.

## Acceptance and implementation

1. Pin exact current upstream source.
2. Read the supported contract and trace the failure across modules.
3. Read issue comments, issue-linked open PRs and area-keyword open PRs.
4. Reject the same fix if an active PR owns it.
5. State the root cause, impact, minimal repair and test design.
6. Prepare the smallest coherent production change in an isolated feat/ worktree
   or a scout patch. Do not modify another chat's source.
7. Use the cheapest real existing-suite test that catches the defect.
8. Check both original failure and candidate behavior where feasible.
9. Run a relevant model or serving evaluation when the change affects output
   or model execution. Source models do not satisfy this condition.
10. Obtain independent changed-line review. Save limits and missing validation.

A failed environment test is not a bug proof. A source model is not a native
device result. Component speed is not model throughput.

## Schedule

The existing heartbeat now runs every 20 minutes in this chat. Each wake
continues useful work from PLAN.json, STATUS.json and the saved phase record.
It does not repeat an unchanged status check.

The deadline stays 19 October at 12:28 UTC. At that time, record the ranked
findings, patches, tests, missing validation, rejected work, Git state and
final exact owned-resource/cost state. Then pause the finite automation.
The active goal covers this report record and the deeper implementation phase.

## Compute and SSD

The total ceiling stays USD10 across all phases. The ledger is shared and
locked. Only Root may launch paid work. Every paid launch uses
control/run_bounded.py and an exact reviewed input/resource manifest.
Preserve the existing paid ownership hold, CPU-first conditions, runtime
denials, cleanup checks and deadline gates.

Use prepared cached images and bounded short jobs when later authorized.
Do not buy credits or upgrade plans. Keep at least 20 GiB free after planned peak
SSD use. Exclude environments, wheels, checkpoints and raw runtime trees from
Git. Preserve all evidence and other chats' resources.

## Publication

The user authorized a commit and push of this compact record to the fork.
This does not authorize upstream PRs, issues, comments, reviews or messages.
Kamran handles submission and must review every changed line.

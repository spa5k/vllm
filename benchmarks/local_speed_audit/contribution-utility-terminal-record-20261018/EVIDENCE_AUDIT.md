# Evidence audit

The source draft and this record use separate branches. No upstream PR, issue,
comment or review was created. Kamran must review every changed line and run
the relevant ordinary tests before any upstream proposal.

- The actual V1 comparison failed with child exit70. It observed a cancelled
  receiver before its queued completion callbacks. All raw bytes are retained.
- V2 adds an explicit observer callback and a bounded Event wait. Production
  source is unchanged. The exact new input received a separate Root review.
  V2 passed twelve controlled rows. Both children finished and were reaped.
- The first source hook attempt changed formatting and found three missing
  test annotations. A later pass formatted one new annotation and the added
  EEP test. All applicable final hooks passed. Root verified the final test
  AST composition and production bytes.
- Root entered a wrong expected hash in one EEP copy precheck (`f5fe2f`). That
  check failed before any write. The next command used the exact descriptor
  from the already-closed manifest. No target code ran in either command.
- Independent reviewer parser errors are retained in the review packets.
  They are reviewer harness errors, not vLLM failures.
- Twenty-three ordinary rows are declared. No ordinary pytest row ran for
  this utility draft. The existing research runner rejects the ancestor
  conftest's cpuinfo import. That is a research boundary, not a vLLM bug.
- The selected-body comparison uses fake transport. It does not import vLLM,
  run EngineCore, test real ZMQ, prove monitor-thread loop dispatch, execute
  the EEP commit handlers, serve HTTP, or evaluate a model.
- The shared Modal ledger is unchanged. No paid job ran for this fix. The
  conservative retained estimate is USD2.9192748 including the network guard.
  This is not an invoice or a balance. Historical stopped-resource records
  are not presented as a fresh remote inventory.
- Complete research packets remain in the scout directory. The compact
  committed record contains the source patch, raw local comparison streams,
  receipts, review excerpts and their exact hashes. The evidence index names
  the full packets and their manifest hashes.

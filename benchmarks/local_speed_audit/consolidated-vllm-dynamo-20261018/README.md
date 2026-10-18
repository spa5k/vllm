# Final vLLM and Dynamo research report

Period: **6–18 October 2026, India time**.

- Open [report.html](report.html) in a browser for the dated research results.
  Seven visible sections cover 17–18 October, 10–15 October and the startup
  study. Period and project filters help select the work to read.
- The HTML also has plain explanations, a separate public PR ledger, a glossary
  and all three embedded technical reports.
- Read [REPORT.md](REPORT.md) for the consolidated Markdown report.
- Read [the unpublished review queue](UNPUBLISHED_REVIEW_QUEUE.md) for separate
  impact and preparation ranks, exact branches or patch files, completed tests
  and missing validation. It is also visible near the start of the HTML.
- Read [vLLM history](vllm-early-history/REPORT.md) and
  [Dynamo history](dynamo-history/REPORT.md) for the detailed appendices.

The reviewed code PR set contains four merged, eight open and three closed
unmerged PRs at the saved 18 October snapshot. A separate documentation PR is
outside that count. Test limits and rejected results are part of the record.
Both research schedules remain paused.

The fresh ownership check excludes utility terminal cleanup from new PR work.
Open upstream PRs #56416 and #58279 already cover that defect. The earlier
research and its test results remain part of the historical record.

The HTML file works offline. It embeds all report text, CSS and JavaScript.
GitHub displays HTML source. Download the file, or open this checkout's copy
in a browser, to view the report. Adjacent JSON links require the report folder.
Local experiment links require the original evidence directories. The private
Dynamo archive, raw experiment trees, model files and build outputs are not
part of this packet.

The source reports and selected snapshots are retained with hashes. This HTML
edition adds no research result and starts no paid work. AI assistance was used.

To rebuild the HTML with the existing environment and installed markdown-it-py:

```bash
uv run --no-project /Users/pacific/Developer/vllm/.venv/bin/python render_report.py
```

Run this command from this report folder. The HTML snapshot date and summary
claims belong to the saved source period, not the time a reader opens it.

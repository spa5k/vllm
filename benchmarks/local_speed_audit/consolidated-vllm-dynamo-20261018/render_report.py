# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Render the saved research records as one offline HTML document."""

import hashlib
import html
import json
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
PUBLISHED = "https://github.com/spa5k/vllm/blob/"
PUBLISHED += "feat/vllm-contribution-research-20261018/"


def render_markdown(path: Path, prefix: str) -> str:
    """Render tables and preserve the scope of external local evidence links."""
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = parser.parse(path.read_text())
    heading_count = 0
    for token in tokens:
        if token.type == "heading_open":
            heading_count += 1
            token.attrSet("id", f"{prefix}-heading-{heading_count}")
            token.tag = f"h{min(int(token.tag[1:]) + 1, 6)}"
        elif token.type == "heading_close":
            token.tag = f"h{min(int(token.tag[1:]) + 1, 6)}"
        for child in token.children or []:
            if child.type != "link_open":
                continue
            target = child.attrGet("href") or ""
            source_path, separator, suffix = target.rpartition(":")
            line = suffix if separator and suffix.isdecimal() else None
            original = target
            if line and target.startswith("/"):
                target = source_path
            if "consolidated-vllm-dynamo-20261018/" in target:
                target = target.split("consolidated-vllm-dynamo-20261018/", 1)[1]
            if target == "vllm-early-history/REPORT.md":
                target = "#appendix-vllm"
            elif target == "dynamo-history/REPORT.md":
                target = "#appendix-dynamo"
            elif target.startswith("/"):
                if "vllm-research-record/vllm/" in target:
                    target = (
                        PUBLISHED + target.split("vllm-research-record/vllm/", 1)[1]
                    )
                    if line:
                        target += "#L" + line
                else:
                    child.attrSet("title", "Local source record: " + original)
                    target = "file://" + target
                    child.attrSet("class", "local-evidence")
            child.attrSet("href", target)
    return parser.renderer.render(tokens, parser.options, {})


def main() -> None:
    snapshot = json.loads((ROOT / "public-pr-state.json").read_text())
    rows = []
    for pr in snapshot["prs"]:
        project = "vLLM" if pr["repo"] == "vllm-project/vllm" else "Dynamo"
        state = pr["state"].lower()
        label = state.title() + (" · draft" if pr["isDraft"] else "")
        title = html.escape(pr["title"])
        url = html.escape(pr["url"], quote=True)
        rows.append(
            f'<tr data-project="{project}" data-state="{state}">'
            f"<td>{project}</td>"
            f'<td><a href="{url}">#{pr["number"]} · {title}</a></td>'
            f'<td><span class="badge {state}">{label}</span></td>'
            f"<td><code>{pr['headRefOid'][:12]}</code></td></tr>"
        )
    replacements = {
        "@@PR_ROWS@@": "\n".join(rows),
        "@@MAIN_REPORT@@": render_markdown(ROOT / "REPORT.md", "main"),
        "@@VLLM_HISTORY@@": render_markdown(
            ROOT / "vllm-early-history/REPORT.md", "vllm"
        ),
        "@@DYNAMO_HISTORY@@": render_markdown(
            ROOT / "dynamo-history/REPORT.md", "dynamo"
        ),
        "@@REPORT_HASH@@": hashlib.sha256(
            (ROOT / "REPORT.md").read_bytes()
        ).hexdigest(),
    }
    output = (ROOT / "report_template.html").read_text()
    for marker, value in replacements.items():
        assert output.count(marker) == 1, marker
        output = output.replace(marker, value)
    assert "@@" not in output
    (ROOT / "report.html").write_text(output)
    print(f"Rendered report.html ({len(output.encode()):,} bytes)")


if __name__ == "__main__":
    main()

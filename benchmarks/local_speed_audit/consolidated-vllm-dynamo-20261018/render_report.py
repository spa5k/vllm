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


def render_markdown(path: Path, prefix: str, content: str | None = None) -> str:
    """Render tables and preserve the scope of external local evidence links."""
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = parser.parse(path.read_text() if content is None else content)
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


def research_catalog() -> str:
    """Keep the dated research visible without duplicating its source text."""
    path = ROOT / "REPORT.md"
    text = path.read_text()
    references = "\n".join(
        line for line in text.splitlines() if line.startswith("[") and "]: " in line
    )

    def section(number: int) -> str:
        start = text.index(f"\n## {number}. ") + 1
        end = text.find("\n## ", start + 1)
        return text[start : end if end != -1 else len(text)].partition("\n")[2]

    dynamo = section(8)
    recent_heading = "### Native HTTP metadata inconsistency, then a normal tested fix"
    old_core = dynamo.split("### TCP admission until ACK", 1)[0]
    lru = "### Approximate-LRU physical copy index"
    old_core += lru + dynamo.split(lru, 1)[1].split(recent_heading, 1)[0]
    recent_dynamo = recent_heading + dynamo.split(recent_heading, 1)[1]
    panels = [
        (
            "recent-vllm",
            "recent",
            "vllm",
            "17–18 October · vLLM",
            "Quantization, cache identity, pooling and failure handling",
            "Native ARM and GPU observations, API regressions and later lifecycle "
            "drafts. Each row retains its tested boundary and missing check.",
            section(7),
        ),
        (
            "recent-dynamo",
            "recent",
            "dynamo",
            "17–18 October · Dynamo",
            "Metadata, profiler artifacts, planner labels and native routing",
            "The metadata fix passed its normal Rust gate. The profiler remains "
            "source-reviewed. Other native observations retain policy "
            "and owner limits.",
            recent_dynamo,
        ),
        (
            "gpu-core",
            "lastweek",
            "vllm",
            "10–15 October · vLLM",
            "GPU preparation, memory and core-engine drafts",
            "Fusion, FP8 scratch reuse, compact warmup routes, PCP counting and "
            "cache writes. Component savings stay separate from model performance.",
            section(5),
        ),
        (
            "model-results",
            "lastweek",
            "vllm",
            "14–15 October · vLLM",
            "Full-model results, including the experiments that did not help",
            "Grammar projection improved selected offline requests. MLA table reuse "
            "removed allocation. N-gram replay did not improve the larger model.",
            section(6),
        ),
        (
            "dynamo-core",
            "lastweek",
            "dynamo",
            "10–14 October · Dynamo",
            "Router state, queue statistics, prefix lookup and physical-copy LRU",
            "Native CPU gains came with storage costs and workload regressions. "
            "These separate candidates have no established serving-speed gain.",
            old_core,
        ),
        (
            "other-engines",
            "lastweek",
            "other",
            "14–15 October · Other engines",
            "TensorRT-LLM and SGLang findings from the same research chats",
            "These retain their actual project labels. Many are CPU, interpreter "
            "or compile checks with native-device validation still missing.",
            section(9),
        ),
        (
            "startup",
            "early",
            "vllm",
            "8 October · vLLM",
            "Startup, compiler attribution, checkpoint loading and cold/warm effects",
            "The baseline study corrected several promising assumptions. Cold/warm "
            "differences and partial compiler timings are not patch speedups.",
            section(4),
        ),
    ]
    result = []
    for key, period, project, date, title, lead, content in panels:
        body = render_markdown(path, "research-" + key, content + "\n\n" + references)
        result.append(
            f'<article class="research-panel" id="result-{key}" '
            f'data-period="{period}" data-project="{project}">'
            f'<div class="research-panel-head"><div class="tag">{date}</div>'
            f"<h3>{title}</h3><p>{lead}</p></div>"
            f'<div class="prose">{body}</div></article>'
        )
    return "\n".join(result)


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
        "@@RESEARCH_CATALOG@@": research_catalog(),
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

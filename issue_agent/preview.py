from collections.abc import Iterable


def render_classification_preview(records: Iterable[dict]) -> str:
    lines = [
        "# Issue Agent Classification Preview",
        "",
        "Mode: preview",
        "Safety: no GitHub issues were changed.",
        "",
        "| Issue | Title | Category | Status |",
        "|-------|-------|----------|--------|",
    ]
    for record in records:
        number = record.get("issue_number", record.get("number", "unknown"))
        title = str(record.get("title", "")).replace("|", "\\|")
        category = record.get("category", "unknown_unsafe")
        status = record.get("status", "preview_only")
        lines.append(f"| #{number} | {title} | {category} | {status} |")
    lines.append("")
    return "\n".join(lines)

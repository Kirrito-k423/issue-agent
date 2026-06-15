---
name: github-issue-summary
description: Publish bounded GitHub issue automation summaries to a tracking issue. Use when Codex needs to read close, classify, and reply process files, create or update an official automation tracking issue, replace a managed report block, and summarize auto-close reasons plus aggregate classification and reply counts for repositories such as verl-project/verl.
---

# GitHub Issue Summary

Use this skill to turn process state from the issue-operation skills into a concise official tracking issue report.

## Configuration

Accept configuration from the user prompt, environment notes, or a local config file if one exists. Defaults:

```yaml
repo: verl-project/verl
actor: Kirrito-k423
state_root: .issue-agent/state/verl-project__verl
write_policy: preview
summary_tracking_issue_title: "[Automation] Issue processing report"
managed_block_start: "<!-- issue-agent-summary:start -->"
managed_block_end: "<!-- issue-agent-summary:end -->"
```

Use `write_policy: preview` unless the user explicitly says `apply=true` or `write_policy=apply`.

## Inputs

Read these files when present:

- `state_root/close/records.json`
- `state_root/classify/records.json`
- `state_root/reply/records.json`

Missing files count as empty data. Do not read reply body files unless needed to verify a path exists; the summary should not include reply text.

## Output State

Create or update these files under `state_root/summary/`:

- `latest-report.md`: overwritten each run with the managed report block content.
- `pending-update.json`: overwritten each run with target issue metadata, counts, and preview body.

The report must be bounded. Replace the managed block instead of appending a new historical report.

## Report Content

Generate a Markdown block with:

```markdown
<!-- issue-agent-summary:start -->
## Automated Issue Processing Report

Updated: <ISO-8601 timestamp>
Actor: <actor>
Repository: <repo>

### Auto-close Details
| Issue | Status | Suitable | Reason | Evidence |
| --- | --- | --- | --- | --- |
| #20 | previewed | yes | resolved-by-maintainer-answer | issue/comment links |

### Aggregate Counts
| Workflow | Previewed | Applied/Posted/Closed | Skipped | Failed |
| --- | ---: | ---: | ---: | ---: |
| Classification | 0 | 0 | 0 | 0 |
| Replies | 0 | 0 | 0 | 0 |

### Classification Labels
| Label | Count |
| --- | ---: |

### Reply Activity
| Metric | Count |
| --- | ---: |
| Reply-worthy issues | 0 |
| Replies posted | 0 |
<!-- issue-agent-summary:end -->
```

List detailed auto-close reasons. For classification and reply workflows, report counts only unless the user explicitly asks for issue-level detail.

## Tracking Issue Workflow

1. Confirm `gh auth status`.
2. Load process records and compute counts.
3. Search for an open or closed issue with the configured title using `gh issue list --search`.
4. If no tracking issue exists:
   - in preview mode, record that a tracking issue would be created;
   - in apply mode, create it with `gh issue create --title <title> --body-file <latest-report.md>`.
5. If a tracking issue exists, fetch its current body.
6. Replace content between `managed_block_start` and `managed_block_end`. If no block exists, append the managed block after the existing body with one blank line.
7. Write `latest-report.md` and `pending-update.json`.
8. If and only if `apply=true`, edit the issue body with `gh issue edit <number> --body-file <file>`.

## Subagent Use

Subagents may audit process files or recompute counts, but the parent agent owns the final report and GitHub issue mutation. Request this output shape:

```json
{
  "close_counts": {},
  "classify_counts": {},
  "reply_counts": {},
  "auto_close_rows": [],
  "notes": []
}
```

Do not let subagents edit the tracking issue or write canonical summary files.

## Safety Rules

- Never edit the tracking issue in preview mode.
- Preserve any user-written content outside the managed block.
- Do not publish reply body contents.
- Do not include private local filesystem paths; use repo issue URLs or relative process paths when needed.
- If tracking issue creation succeeds but body editing fails, record the issue URL and mark the update failed in `pending-update.json`.

## Verification

Before finishing, report the tracking issue number or creation plan, aggregate counts, updated local files, and whether preview or apply mode was used. In preview mode, explicitly state that no GitHub issue body was changed.

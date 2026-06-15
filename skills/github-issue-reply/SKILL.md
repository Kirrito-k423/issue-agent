---
name: github-issue-reply
description: Draft and optionally post academic bilingual GitHub issue replies with bounded reply metadata. Use when Codex needs to inspect oldest unrecorded issues, decide whether a reply is appropriate, store each English-then-Chinese reply body in a separate file, optionally comment only after explicit apply=true, and maintain a reusable reply table for repositories such as verl-project/verl.
---

# GitHub Issue Reply

Use this skill to decide whether issues deserve an automated maintainer-style reply, draft replies in a consistent format, and keep reply metadata separate from reply body files.

## Configuration

Accept configuration from the user prompt, environment notes, or a local config file if one exists. Defaults:

```yaml
repo: verl-project/verl
actor: Kirrito-k423
state_root: .issue-agent/state/verl-project__verl
write_policy: preview
batch_size: 10
reply_signature_en: "Processed by Codex + 5.3-Codex."
reply_signature_zh: "由 Codex + 5.3-Codex 处理。"
```

Use `write_policy: preview` unless the user explicitly says `apply=true` or `write_policy=apply`.

## State Files

Create or update these files under `state_root/reply/`:

- `records.json`: canonical object keyed by issue number as a string.
- `replies/issue-<number>.md`: one reply body per reply-worthy issue.
- `pending-batch.json`: overwritten each run with decisions and relative reply paths.
- `latest-preview.md`: overwritten each run with summaries and reply file links.

Each `records.json` entry must contain:

```json
{
  "issue_number": 20,
  "url": "https://github.com/OWNER/REPO/issues/20",
  "title": "Issue title",
  "reply_worthy": true,
  "suitability_reason": "A concise answer can unblock the reporter with public evidence.",
  "already_replied": false,
  "reply_file": "reply/replies/issue-20.md",
  "posted_comment_url": null,
  "status": "drafted|posted|skipped|failed",
  "actor": "Kirrito-k423",
  "assessed_at": "ISO-8601 timestamp"
}
```

Do not store full reply text in `records.json`; store only the relative path and posted comment URL.

## Workflow

1. Confirm `gh auth status`.
2. Load `records.json`; skip issue numbers already present.
3. Fetch open issues sorted oldest first. Select the next `batch_size` unrecorded issues.
4. Fetch full issue body, labels, and comments for each selected issue.
5. Determine `already_replied` by checking whether the configured actor or prior automation signature already appears in comments.
6. Mark an issue reply-worthy when a public, evidence-based response can help:
   - ask for missing reproduction details using the repo's issue context;
   - point to a relevant doc, existing issue, PR, config, or known label area;
   - summarize current status and suggest a concrete next diagnostic step;
   - provide a cautious maintainer-style clarification without making unsupported promises.
7. Mark not reply-worthy when the issue needs deep code investigation, private maintainer judgment, speculative roadmap promises, or has already received a sufficient recent answer.
8. For reply-worthy issues, create `replies/issue-<number>.md` with:
   - English section first;
   - Chinese section second;
   - academic, precise, respectful tone;
   - no unsupported claims;
   - final two lines exactly:
     `Processed by Codex + 5.3-Codex.`
     `由 Codex + 5.3-Codex 处理。`
9. Write `pending-batch.json`, `latest-preview.md`, and `records.json`.
10. If and only if `apply=true`, post each reply file using `gh issue comment <number> --body-file <path>`, capture the comment URL when available, and update `status: posted`.

## Reply Style

Use this structure unless the issue requires a shorter answer:

```markdown
Thank you for reporting this. ...

Recommended next steps:
1. ...
2. ...

感谢你的反馈。...

建议的下一步：
1. ...
2. ...

Processed by Codex + 5.3-Codex.
由 Codex + 5.3-Codex 处理。
```

Keep replies specific to the issue. Avoid marketing language, apologies for delays, guarantees, and claims that maintainers will implement something.

## Subagent Use

Subagents may analyze issue context and draft reply candidates, but the parent agent owns final wording, GitHub comments, and state writes. Give subagents raw issue JSON and request this output shape:

```json
{
  "issue_number": 20,
  "reply_worthy": true,
  "suitability_reason": "Why a reply is appropriate",
  "already_replied": false,
  "draft_reply_markdown": "English first, Chinese second, signed",
  "confidence": "low|medium|high"
}
```

Do not let subagents post comments or write canonical state files.

## Safety Rules

- Never post in preview mode.
- Never reply when the answer requires running unverified experiments and no evidence is available.
- Never expose private tokens, local paths, or internal notes.
- If a reply file exists and the issue is reprocessed by explicit request, overwrite that issue's file rather than creating duplicates.
- If posting fails, preserve the draft file and mark the record `status: failed`.

## Verification

Before finishing, report the assessed issue numbers, which reply files were created, whether any comments were posted, and the updated state paths. In preview mode, explicitly state that no GitHub comments were posted.

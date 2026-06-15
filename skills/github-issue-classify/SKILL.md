---
name: github-issue-classify
description: Classify GitHub issues with configurable labels and bounded processed state. Use when Codex needs to process new or unrecorded issues in batches, assign labels such as bug, Ascend, Hardware, question, or enhancement, optionally apply labels only after explicit apply=true, and maintain a reusable processed issue list for repositories such as verl-project/verl.
---

# GitHub Issue Classify

Use this skill to label the next batch of unprocessed issues while keeping one canonical classification record per issue.

## Configuration

Accept configuration from the user prompt, environment notes, or a local config file if one exists. Defaults:

```yaml
repo: verl-project/verl
actor: Kirrito-k423
state_root: .issue-agent/state/verl-project__verl
write_policy: preview
batch_size: 20
label_config_version: verl-default-v1
labels:
  bug: ["error", "exception", "crash", "traceback", "incorrect", "not working", "hang"]
  Ascend: ["ascend", "npu", "torch_npu", "cann", "910b", "910"]
  Hardware: ["gpu", "nvidia", "amd", "cuda", "npu", "device", "hardware"]
  question: ["how", "why", "can I", "is it possible", "?"]
  enhancement: ["feature request", "support", "add", "improve", "enhancement"]
```

Use the repository's exact label spelling. For `verl-project/verl`, known labels include `bug`, `Ascend`, `Hardware`, `question`, and `enhancement`. If a configured label does not exist, do not create it unless the user explicitly asks.

## State Files

Create or update these files under `state_root/classify/`:

- `records.json`: canonical object keyed by issue number as a string.
- `processed-ids.json`: sorted numeric list derived from `records.json`.
- `pending-batch.json`: overwritten each run with proposed or applied labels.
- `latest-preview.md`: overwritten each run with human-readable rationale.

Each `records.json` entry must contain:

```json
{
  "issue_number": 20,
  "url": "https://github.com/OWNER/REPO/issues/20",
  "title": "Issue title",
  "labels_before": ["question"],
  "labels_proposed": ["question"],
  "labels_applied": [],
  "reason": "The issue asks how to use an existing feature.",
  "status": "previewed|applied|skipped|failed",
  "label_config_version": "verl-default-v1",
  "actor": "Kirrito-k423",
  "processed_at": "ISO-8601 timestamp"
}
```

Keep state bounded by replacing the issue's entry and regenerating `processed-ids.json`.

## Workflow

1. Confirm `gh auth status`.
2. Fetch repo labels with `gh label list --json name,description` and keep only labels that exist.
3. Load `records.json`; skip issue numbers already present.
4. Fetch open issues sorted oldest first. Select the next `batch_size` unprocessed issues.
5. Fetch full issue details for each selected issue when the title and existing labels are insufficient.
6. Propose labels using repo labels, body evidence, comments, and existing labels:
   - `bug`: reproducible failure, stack trace, incorrect behavior, regression, crash, hang, or error report.
   - `Ascend`: Ascend NPU, CANN, `torch_npu`, `acl`, 910/910B, or Ascend-specific install/runtime behavior.
   - `Hardware`: hardware backend or device-specific behavior, including CUDA, AMD, NVIDIA, GPU, NPU.
   - `question`: usage question, clarification request, or "is this possible" issue without a concrete change request.
   - `enhancement`: feature request, support request, roadmap idea, or improvement proposal.
7. Preserve useful existing labels. Do not remove labels unless the user explicitly asks.
8. Write `pending-batch.json`, `latest-preview.md`, `records.json`, and `processed-ids.json`.
9. If and only if `apply=true`, add missing labels with `gh issue edit <number> --add-label "label1,label2"` and update `labels_applied` plus `status`.

## Subagent Use

Subagents may classify disjoint issue batches. The parent agent must provide available labels and raw issue data, then merge decisions and perform all GitHub and state writes. Request this output shape:

```json
{
  "issue_number": 20,
  "labels_proposed": ["question"],
  "reason": "Why these labels fit",
  "confidence": "low|medium|high"
}
```

Do not let subagents create labels, mutate issues, or write canonical state files.

## Safety Rules

- Never mutate labels in preview mode.
- Do not invent labels that are absent from the repository.
- Do not classify a closed issue unless the user explicitly asks for closed issue processing.
- If no label clearly fits, use an empty proposal and explain the uncertainty.
- If label application partially fails, preserve the preview record and mark `status: failed`.

## Verification

Before finishing, report the processed issue numbers, labels proposed or applied, state paths updated, and whether preview or apply mode was used. In preview mode, explicitly state that no GitHub labels were changed.

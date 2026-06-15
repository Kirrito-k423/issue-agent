---
phase: 02-code-aware-triage-and-answers
plan: "03"
subsystem: answer-preview
tags: [python, cli, preview-state, answer-drafts, evidence]
requires:
  - phase: 02-02
    provides: Answer policy gates for source evidence, run evidence, and reply-worthiness
provides:
  - Answer preview record builder
  - Preview-only answer CLI command
  - Bounded answer state and per-issue draft files
  - Markdown answer preview with evidence mode and draft paths
affects:
  - 03-stale-cleanup-and-controlled-apply
  - 04-summary-tests-and-operator-docs
tech-stack:
  added: []
  patterns:
    - Answer workflow gathers evidence before policy and draft rendering
    - Draft bodies are stored in per-issue files rather than embedded in records.json
    - CLI commands remain explicit and preview-only
key-files:
  created:
    - issue_agent/answer.py
    - tests/test_answer_preview.py
  modified:
    - issue_agent/models.py
    - issue_agent/preview.py
    - issue_agent/state.py
    - issue_agent/cli.py
    - issue_agent/policy.py
    - README.md
    - tests/test_answer_policy.py
    - tests/test_cli_skeleton.py
    - tests/test_github.py
requirements-completed:
  - CODE-03
  - CODE-04
  - SAFE-02
  - ANS-01
  - ANS-02
  - ANS-03
key-decisions:
  - "Answer preview records include answer_policy and draft_path without replacing Phase 1 preview record fields."
  - "Only reply-worthy records write local draft files under answer/drafts/."
  - "Unsupported answer categories such as bug reports are skipped instead of drafted."
patterns-established:
  - "write_answer_preview mirrors bounded classification state while adding per-issue draft file management."
  - "answer-preview CLI proves source-backed answer drafts without posting GitHub comments."
duration: 7 min
completed: 2026-06-15T17:02:34Z
---

# Phase 2 Plan 03: Answer Preview Workflow Summary

**Preview-only answer drafts with evidence citations, bounded state, and an explicit CLI command**

## Performance

- **Duration:** 7 min
- **Started:** 2026-06-15T16:55:30Z
- **Completed:** 2026-06-15T17:02:34Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added `issue_agent/answer.py` to classify issues, gather evidence, run answer policy, and build preview records.
- Added bounded answer state under `answer/` with `records.json`, `pending-batch.json`, `latest-preview.md`, and local `drafts/issue-<number>.md` files.
- Added `answer-preview` CLI and README usage so maintainers can generate local answer previews without posting comments.

## Task Commits

1. **Task 1: Build answer preview records from evidence and policy** - `63abfa1` (feat)
2. **Task 2: Write bounded answer state and draft files** - `d05e845` (feat)
3. **Task 3: Add preview-only answer CLI command** - `b0955d8` (feat)
4. **Task 3 follow-up: Update fixture intake expectations** - `dfef764` (fix)

## Files Created/Modified

- `issue_agent/answer.py` - Answer preview workflow and deterministic draft renderer.
- `issue_agent/models.py` - Added `answer_policy` and `draft_path` to preview records.
- `issue_agent/preview.py` - Added Markdown answer preview renderer.
- `issue_agent/state.py` - Added `write_answer_preview` with bounded records and draft file handling.
- `issue_agent/cli.py` - Added `answer-preview` command.
- `issue_agent/policy.py` - Skips unsupported answer categories instead of drafting bug reports.
- `README.md` - Added answer-preview quickstart and evidence-draft note.
- `tests/test_answer_preview.py` - Added workflow, state, draft, and CLI tests.
- `tests/test_cli_skeleton.py` and `tests/test_github.py` - Updated fixture expectations for the expanded issue batch.

## Decisions Made

- Kept answer drafts deterministic for Phase 2 so safety and evidence plumbing are verified before live model drafting.
- Stored draft paths in preview records but kept draft bodies in local Markdown files.
- Treated bug reports and other non-answer categories as skipped unless a later phase explicitly supports them.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Skip unsupported answer categories**
- **Found during:** Task 3 CLI verification.
- **Issue:** Bug report fixture issue was initially considered reply-worthy by the default policy path, which created an unintended draft file.
- **Fix:** Added `unsupported_answer_category` handling for non-code/non-usage categories and kept `unknown_unsafe` as human review.
- **Files modified:** `issue_agent/policy.py`, `tests/test_answer_policy.py`.
- **Verification:** `answer-preview` now creates drafts for issue 1 and issue 3 only; issue 4 records `requires_unverified_reproduction`.
- **Committed in:** `b0955d8` (Task 3 commit)

**2. [Rule 3 - Blocking] Update fixture-order tests after fixture expansion**
- **Found during:** Plan-level full test run.
- **Issue:** `tests/test_github.py` still expected only fixture issues `[1, 2]` after Phase 2 intentionally added issues 3 and 4.
- **Fix:** Updated fixture order assertions to `[1, 2, 3, 4]`.
- **Files modified:** `tests/test_github.py`.
- **Verification:** Full Phase 2 test suite passes, 35 tests.
- **Committed in:** `dfef764`

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 blocking).
**Impact on plan:** Both fixes preserve the Phase 2 safety boundary and align tests with planned fixture expansion. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Verification

- `.venv/bin/python -m pytest tests/test_answer_preview.py tests/test_answer_policy.py tests/test_codegraph.py tests/test_cli_skeleton.py tests/test_classifier_policy.py tests/test_state_preview.py tests/test_github.py tests/test_config.py` - PASSED, 35 tests.
- `python -m issue_agent.cli answer-preview --config examples/config.yaml --issues-file examples/issues.fixture.json --repo-root tests/fixtures/source_repo --state-root /tmp/issue-agent-answer-preview` - PASSED.
- CLI artifact assertion - PASSED: `answer/records.json`, `answer/pending-batch.json`, `answer/latest-preview.md`, and local draft files exist.
- Source-backed draft assertion - PASSED: code-logic fixture issue 3 produces `answer/drafts/issue-3.md`.
- No-answer assertion - PASSED: reproduction fixture issue 4 produces no draft and records `requires_unverified_reproduction`.
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" query verify.key-links .planning/phases/02-code-aware-triage-and-answers/02-03-PLAN.md` - PASSED, 3/3 links verified.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent tests README.md` - PASSED, no matches.

## Next Phase Readiness

Phase 2 has a complete answer-preview path. Phase 3 can build stale cleanup and controlled apply mode on top of evidence refs, answer policy decisions, bounded state, and the preview-only CLI convention.

## Self-Check: PASSED

---
*Phase: 02-code-aware-triage-and-answers*
*Completed: 2026-06-15*

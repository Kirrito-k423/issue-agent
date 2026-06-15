---
phase: 03-stale-cleanup-and-controlled-apply
plan: "02"
subsystem: closure-preview
tags: [python, policy, state, cli, github, closure]
requires:
  - phase: 03-stale-cleanup-and-controlled-apply
    plan: "01"
    provides: Linked reference schema, parser, and stale cleanup fixtures
provides:
  - Conservative closure policy gates for stale cleanup recommendations
  - Close preview records with reason, risk, current state, evidence, and draft comment
  - Bounded local close preview state under close/
  - Preview-only close CLI command
affects:
  - 03-stale-cleanup-and-controlled-apply
  - 04-summary-tests-and-operator-docs
tech-stack:
  added: []
  patterns:
    - Closure policy is separate from answer policy and apply policy.
    - Preview mode writes local state only and never calls GitHub mutation commands.
    - Closure suitability requires explicit allowed evidence; age alone is insufficient.
key-files:
  created:
    - issue_agent/closure.py
    - tests/test_closure_policy.py
    - tests/test_close_preview.py
  modified:
    - issue_agent/models.py
    - issue_agent/policy.py
    - issue_agent/preview.py
    - issue_agent/state.py
    - issue_agent/cli.py
    - README.md
key-decisions:
  - "Block closure recommendations for roadmap/help-wanted/open contribution signals unless explicit closure evidence exists."
  - "Keep close-preview records immutable with `github_mutation_applied=False`."
  - "Write close preview state as bounded JSON plus Markdown for maintainer review."
patterns-established:
  - "build_close_preview_records(issues, repo) extracts linked references before policy evaluation."
  - "write_close_preview(state_root, records) replaces canonical records by issue number."
  - "close-preview CLI reports preview mode and local artifact path without public side effects."
requirements-completed:
  - SAFE-04
  - CLOSE-01
  - CLOSE-02
duration: 6 min
completed: 2026-06-15T17:28:31Z
---

# Phase 3 Plan 02: Close Preview Summary

**Evidence-gated stale cleanup recommendations with local-only preview artifacts**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-15T17:23:37Z
- **Completed:** 2026-06-15T17:28:31Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added `ClosureDecision` and conservative closure reason/risk fields for stale cleanup decisions.
- Implemented `evaluate_closure_policy` so roadmap/help-wanted/open contribution signals remain not suitable to close, while allowed reasons require explicit evidence.
- Added close preview record generation, Markdown rendering, and bounded local state under `close/`.
- Added `close-preview` CLI for fixture-backed local inspection with an explicit no-mutation safety message.

## Task Commits

1. **Task 1: Add closure recommendation policy** - `e7c8e8a` (feat)
2. **Task 2: Build close preview records and bounded state** - `9c64fd2` (feat)
3. **Task 3: Add preview-only close CLI command** - `b2080a0` (feat)

## Files Created/Modified

- `issue_agent/models.py` - Added closure reason, risk level, and closure decision models.
- `issue_agent/policy.py` - Added evidence-gated closure policy separate from answer policy.
- `issue_agent/closure.py` - Added close preview record builder.
- `issue_agent/preview.py` - Added close preview Markdown renderer.
- `issue_agent/state.py` - Added bounded close preview state writer.
- `issue_agent/cli.py` - Added `close-preview` Typer command.
- `tests/test_closure_policy.py` - Added conservative closure policy tests.
- `tests/test_close_preview.py` - Added preview state and CLI tests.
- `README.md` - Documented close preview usage and safety boundary.

## Decisions Made

- Closure suitability is never inferred from age alone.
- Unknown linked PR status and roadmap/help-wanted/open contribution signals block closure recommendations.
- Draft close comments are generated only for suitable-to-close records.
- Preview state is intentionally local and contains no applied GitHub mutation flag.

## Deviations from Plan

None.

## Issues Encountered

None.

## User Setup Required

None - preview mode uses fixture input and local state only.

## Verification

- `.venv/bin/python -m pytest tests/test_closure_policy.py tests/test_links.py` - PASSED, 10 tests.
- `.venv/bin/python -m pytest tests/test_close_preview.py tests/test_state_preview.py` - PASSED, 6 tests.
- `.venv/bin/python -m pytest tests/test_close_preview.py tests/test_cli_skeleton.py tests/test_config.py` - PASSED, 9 tests.
- `.venv/bin/python -m issue_agent.cli close-preview --config examples/config.yaml --issues-file examples/issues.fixture.json --repo Kirrito-k423/issue-agent --state-root /tmp/issue-agent-close-preview` - PASSED, wrote local close preview artifacts.
- `.venv/bin/python -m pytest tests/test_closure_policy.py tests/test_close_preview.py tests/test_links.py tests/test_state_preview.py tests/test_cli_skeleton.py tests/test_config.py` - PASSED, 21 tests.
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" query verify.key-links .planning/phases/03-stale-cleanup-and-controlled-apply/03-02-PLAN.md` - PASSED, 3/3 links verified.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent tests README.md` - PASSED, no preview mutation matches.

## Next Phase Readiness

03-03 can now add an explicit apply boundary that consumes existing preview records, requires operator intent, and isolates any GitHub mutation commands to a dedicated adapter tested with fake runners.

## Self-Check: PASSED

---
*Phase: 03-stale-cleanup-and-controlled-apply*
*Completed: 2026-06-15*

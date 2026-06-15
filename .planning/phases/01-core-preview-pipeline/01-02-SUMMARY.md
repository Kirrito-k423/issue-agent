---
phase: 01-core-preview-pipeline
plan: "02"
subsystem: github-intake
tags: [python, pydantic, github, fixtures, labels]
requires:
  - phase: 01-01
    provides: CLI preview skeleton and config loading
provides:
  - Typed issue, comment, and label models
  - Fixture-backed issue and label intake adapter
  - CLI preview wired to typed intake and repository label awareness
affects:
  - 01-03 classifier schema and deterministic policy validation
tech-stack:
  added: []
  patterns:
    - Fixture intake validates JSON through Pydantic before preview state creation
    - GitHub live access is isolated behind a read-only client shell
key-files:
  created:
    - issue_agent/github.py
    - issue_agent/models.py
    - tests/test_github.py
  modified:
    - issue_agent/cli.py
    - tests/test_cli_skeleton.py
key-decisions:
  - "Keep GitHub access behind `issue_agent/github.py` and expose only read-only list methods in Phase 1."
  - "Load configured labels as typed `LabelInfo` values before building preview records."
  - "Reject absent labels in preview data shape without adding label creation behavior."
patterns-established:
  - "Fixture loaders preserve deterministic input order."
  - "CLI preview consumes typed issue and label records instead of raw JSON dictionaries."
requirements-completed:
  - GH-01
  - GH-02
  - SAFE-05
  - STATE-03
duration: 3 min
completed: 2026-06-15T16:28:07Z
---

# Phase 1 Plan 02: GitHub Issue and Label Intake Summary

**Typed fixture issue intake with read-only GitHub adapter boundary and label-aware preview records**

## Performance

- **Duration:** 3 min
- **Started:** 2026-06-15T16:25:05Z
- **Completed:** 2026-06-15T16:28:07Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added Pydantic `IssueComment`, `IssueInput`, and `LabelInfo` models for fixture validation.
- Added `load_fixture_issues`, `load_fixture_labels`, and a read-only `GitHubClient` shell.
- Updated the CLI preview path to consume typed issue and label records and persist `labels_available` / `labels_rejected`.

## Task Commits

1. **Task 1: Define issue and label models** - `180e2ff` (feat)
2. **Task 2: Add fixture and read-only GitHub intake adapter** - `483ba9a` (feat)
3. **Task 3: Wire CLI preview to typed intake and label set** - `e451f00` (feat)

## Files Created/Modified

- `issue_agent/models.py` - Typed issue, comment, and label input models.
- `issue_agent/github.py` - Fixture loaders and read-only GitHub client shell.
- `issue_agent/cli.py` - Preview command wired to typed fixture and label intake.
- `tests/test_github.py` - Fixture validation and deterministic loader tests.
- `tests/test_cli_skeleton.py` - Label awareness assertions in preview records.

## Decisions Made

- Kept live GitHub access unimplemented in Phase 1 except for a read-only client shape.
- Represented missing proposed labels as `labels_rejected` entries with reason `label_not_in_repository`.
- Preserved fixture ordering so repeated previews are deterministic.

## Deviations from Plan

None - plan executed exactly as written.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope change.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Verification

- `.venv/bin/python -m pytest tests/test_cli_skeleton.py tests/test_github.py` - PASSED, 6 tests.
- `.venv/bin/python -m issue_agent.cli preview --config examples/config.yaml --issues-file examples/issues.fixture.json --state-root /tmp/issue-agent-preview` - PASSED, preview records contain typed issue numbers and label fields.
- `rg "gh issue (edit|comment|close)|create_label|delete_label" issue_agent/github.py issue_agent/cli.py` - PASSED, no matches.
- `gsd-tools query verify.key-links .planning/phases/01-core-preview-pipeline/01-02-PLAN.md` - PASSED, 2/2 links verified.

## Next Phase Readiness

Ready for Plan 01-03 to add classifier proposal schemas, deterministic policy, invalid-output handling, and model/policy fields in preview state.

## Self-Check: PASSED

---
*Phase: 01-core-preview-pipeline*
*Completed: 2026-06-15*

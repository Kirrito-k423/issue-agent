---
phase: 01-core-preview-pipeline
plan: "01"
subsystem: cli
tags: [python, typer, pydantic, preview-state, pytest]
requires: []
provides:
  - Python package scaffold with issue-agent CLI entrypoint
  - Non-secret YAML repository profile and empty environment variable example
  - Fixture-backed preview command that writes bounded local state artifacts
affects:
  - 01-02 GitHub issue and label intake
  - 01-03 classifier schema and policy validation
tech-stack:
  added: [typer, pydantic, pyyaml, rich, pytest]
  patterns:
    - Typer command group with explicit preview subcommand
    - Pydantic config models for non-secret repository profiles
    - Bounded JSON and Markdown preview state under a workflow directory
key-files:
  created:
    - pyproject.toml
    - README.md
    - .env.example
    - examples/config.yaml
    - examples/issues.fixture.json
    - issue_agent/__init__.py
    - issue_agent/cli.py
    - issue_agent/config.py
    - issue_agent/preview.py
    - issue_agent/state.py
    - tests/test_cli_skeleton.py
    - tests/test_config.py
  modified: []
key-decisions:
  - "Use a Typer command group so `python -m issue_agent.cli preview ...` remains an explicit subcommand."
  - "Keep tracked config non-secret and document provider/proxy values as empty environment variables."
  - "Represent Phase 1 preview records as plain dictionaries until typed issue and classifier schemas land in later plans."
patterns-established:
  - "Preview state is written under `<state_root>/classify/` with records.json keyed by issue number."
  - "CLI output uses plain Typer echo for machine-readable paths."
requirements-completed:
  - CONF-01
  - CONF-02
  - CONF-03
  - GH-01
  - CLSF-01
  - SAFE-03
  - STATE-01
  - STATE-02
  - STATE-03
duration: 4 min
completed: 2026-06-15T16:25:03Z
---

# Phase 1 Plan 01: CLI, Config, and Preview Skeleton Summary

**Typer preview CLI with non-secret YAML config and bounded fixture preview state artifacts**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-15T16:21:00Z
- **Completed:** 2026-06-15T16:25:03Z
- **Tasks:** 3
- **Files modified:** 12

## Accomplishments

- Created the Python package scaffold, editable install metadata, and explicit `issue-agent` console script.
- Added a non-secret example repository profile, empty `.env.example` provider/proxy keys, and two offline fixture issues.
- Implemented `preview` so it loads config and fixture issues, writes `records.json`, `pending-batch.json`, and `latest-preview.md`, and reports preview-only behavior.

## Task Commits

1. **Task 1: Scaffold package and CLI entrypoint** - `7873a93` (feat)
2. **Task 2: Add non-secret config loading and fixture input** - `204bcd5` (feat)
3. **Task 3: Write bounded preview artifacts from fixture run** - `aa8fd04` (feat)

## Files Created/Modified

- `pyproject.toml` - Package metadata, dependencies, console script, and pytest config.
- `README.md` - Quickstart, proxy guidance, and preview-first safety notes.
- `.env.example` - Empty provider and proxy environment variable names.
- `examples/config.yaml` - Non-secret Phase 1 repository profile.
- `examples/issues.fixture.json` - Offline fixture issue batch.
- `issue_agent/cli.py` - Typer app and `preview` command.
- `issue_agent/config.py` - Pydantic config models and YAML loader.
- `issue_agent/preview.py` - Markdown preview renderer.
- `issue_agent/state.py` - Bounded preview state writer.
- `tests/test_cli_skeleton.py` - End-to-end CLI fixture preview smoke test.
- `tests/test_config.py` - Config loader tests.

## Decisions Made

- Used a Typer callback to keep `preview` as a real subcommand even while the app has only one command.
- Used plain `typer.echo` for output paths so tests and later automation can consume exact file paths without Rich line wrapping.
- Deferred typed issue models to Plan 01-02 and classifier schemas to Plan 01-03, while preserving the final state file names and replacement semantics.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Forced Typer group mode for the preview subcommand**
- **Found during:** Task 3 (Write bounded preview artifacts from fixture run)
- **Issue:** Typer treated the single command app as a root command, so `python -m issue_agent.cli preview ...` failed with an unexpected argument error.
- **Fix:** Added a no-op `@app.callback()` to force command group behavior.
- **Files modified:** `issue_agent/cli.py`
- **Verification:** `.venv/bin/python -m issue_agent.cli preview --config examples/config.yaml --issues-file examples/issues.fixture.json --state-root /tmp/issue-agent-preview`
- **Committed in:** `aa8fd04`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix preserves the planned explicit preview command and does not expand scope.

## Issues Encountered

- System Python lacked `PyYAML` and rejected global pip installs due PEP 668. Created ignored `.venv` and installed `.[dev]` there for verification.

## User Setup Required

None - no external service configuration required.

## Verification

- `.venv/bin/python -m pytest tests/test_cli_skeleton.py tests/test_config.py` - PASSED, 4 tests.
- `.venv/bin/python -m issue_agent.cli preview --config examples/config.yaml --issues-file examples/issues.fixture.json --state-root /tmp/issue-agent-preview` - PASSED, wrote all three preview files.
- `rg "gh issue (edit|comment|close)" issue_agent tests` - PASSED, no matches.
- `rg "gho_|github_pat_|MINIMAX_API_KEY=.+|password|secret" examples .env.example issue_agent tests` - PASSED, no committed secret values.

## Next Phase Readiness

Ready for Plan 01-02 to replace ad hoc fixture dictionaries with typed issue and label intake models.

## Self-Check: PASSED

---
*Phase: 01-core-preview-pipeline*
*Completed: 2026-06-15*

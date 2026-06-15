# Phase 4: Summary, Tests, and Operator Docs - Context

**Gathered:** 2026-06-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 hardens the completed Issue Agent workflows into a trustworthy v1 operator experience. It should add an aggregate local summary report over classification, answer, close, and apply state; broaden deterministic regression coverage for preview/apply separation and bounded state behavior; and document configuration, proxy setup, CodeGraph fallback, preview mode, apply mode, and release verification. This phase does not add dashboards, scheduling, GitHub App auth, multi-repo orchestration, live provider evaluation, or new public mutation surfaces.

</domain>

<decisions>
## Implementation Decisions

### Aggregate Summary Report
- **D-01:** Add a preview-only summary workflow that reads existing local state files and produces an aggregate report without calling GitHub, model providers, CodeGraph, or policy generation code.
- **D-02:** The first summary report should include classification, answer, close, and apply sections when their state files exist. It must gracefully mark missing workflows as absent rather than failing the whole report.
- **D-03:** Summary output should be both machine-readable and maintainer-readable: write bounded `summary/records.json` plus `summary/latest-preview.md`, following the existing state-root convention.
- **D-04:** The CLI command should be explicit, such as `summary-preview`, and should print a preview/no-mutation safety line plus the latest summary path.

### Regression Fixture Suite
- **D-05:** Phase 4 tests should exercise the full offline workflow path using fixtures and temporary state: classify preview, answer preview, close preview, summary preview, and apply result recording through fake runners.
- **D-06:** Regression tests must prove schema validation, policy downgrades, preview/apply separation, bounded record replacement, and missing-state summary behavior. They should not require live GitHub, live MiniMax, CodeGraph installation, or network.
- **D-07:** Keep tests focused on safety invariants and operator-visible artifacts rather than brittle Markdown formatting. JSON structure and key safety text are stronger assertions than full-file snapshots.
- **D-08:** Add a mutation-surface scan that documents `gh issue` mutation commands are isolated to the explicit apply adapter, tests, and documentation.

### Operator Documentation
- **D-09:** Keep README as the short quickstart and add a dedicated operator guide for the full workflow. The guide should cover config, fixture commands, proxy environment variables, CodeGraph behavior, preview/apply boundaries, and remote-server network notes.
- **D-10:** Documentation must make the local China Mac proxy convention explicit (`127.0.0.1:7890`) without copying private config paths, passwords, tokens, or server credentials into tracked files.
- **D-11:** The docs should explain when not to answer issues: no environment reproduction, insufficient source evidence, unresolved linked state, or unsafe closure evidence.
- **D-12:** Apply mode docs must be visibly different from preview docs: preview commands cannot mutate GitHub; `apply-close` can run `gh issue` mutations only after matching preview records exist.

### Secret and State Hygiene
- **D-13:** Tracked examples and docs must not contain provider keys, GitHub tokens, local password paths, or private remote-server credential values.
- **D-14:** Generated `.issue-agent/state/` remains ignored and must not be committed. Phase 4 summary state is written under the operator-selected state root, not into `.planning/`.
- **D-15:** Verification should include a lightweight tracked-file scan for obvious secret placeholders and sensitive local paths relevant to this project.

### Phase 4 Scope Fence
- **D-16:** Do not implement dashboards, HTML reports, scheduled jobs, recurring automations, GitHub App auth, or multi-repo runs.
- **D-17:** Do not add new model-provider routing or live model evaluation; summary is deterministic aggregation of already-written state.
- **D-18:** Do not change the existing preview/apply semantics while adding summary and docs. Existing commands must remain backward compatible.

### the agent's Discretion
- The agent may choose exact model names for summary records and helper functions, provided output stays bounded and schema-valid.
- The agent may decide whether summary aggregation lives in a new `summary.py` module or as small helpers near `state.py` and `preview.py`.
- The agent may split regression tests into one or more files based on readability.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` — Core value, preview-first operation, CodeGraph rule, and deferred v2 boundaries.
- `.planning/REQUIREMENTS.md` — Phase 4 requirement `STATE-04`, Definition of Done, and acceptance criteria for fixture, docs, and no-secret behavior.
- `.planning/ROADMAP.md` — Phase 4 goal, success criteria, and planned work items.
- `.planning/STATE.md` — Current milestone position and Phase 4 readiness.

### Prior Phase Contracts
- `.planning/phases/01-core-preview-pipeline/01-CONTEXT.md` — Config, fixture intake, preview state, secret handling, and no-mutation rules.
- `.planning/phases/02-code-aware-triage-and-answers/02-CONTEXT.md` — CodeGraph-first evidence, no-answer gates, answer-preview state, and fallback recording.
- `.planning/phases/03-stale-cleanup-and-controlled-apply/03-CONTEXT.md` — Linked evidence, closure preview, explicit apply boundary, and fake-runner testing rules.
- `.planning/phases/03-stale-cleanup-and-controlled-apply/03-03-SUMMARY.md` — Latest apply engine behavior and verification results.

### Repository Instructions
- `AGENTS.md` — Chinese-first collaboration, proxy note, remote-server caution, and CodeGraph-before-grep rule when `.codegraph/` exists.
- `.gitignore` — State, environment, and cache files that must remain untracked.
- `README.md` — Existing quickstart and safety model to preserve and extend.

### Current Implementation
- `issue_agent/models.py` — Existing Pydantic models and natural home for summary models if needed.
- `issue_agent/state.py` — Bounded state writers and local record replacement patterns.
- `issue_agent/preview.py` — Markdown preview renderers and safety text conventions.
- `issue_agent/cli.py` — Typer command pattern for explicit preview/apply commands.
- `issue_agent/apply.py` — Explicit apply validation and fake-runner-compatible execution boundary.
- `issue_agent/github.py` — Fixture loaders and isolated GitHub mutation adapter.
- `examples/config.yaml` — Non-secret repository profile example.
- `examples/issues.fixture.json` — Offline fixture batch for end-to-end regression.
- `tests/test_cli_skeleton.py` — CLI smoke test style.
- `tests/test_apply.py` — Fake-runner apply tests and preview preservation behavior.
- `tests/test_state_preview.py` — Bounded record replacement pattern.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `state._read_records` already loads workflow `records.json` as dictionaries and can guide summary loading.
- Existing writers use `records.json`, `pending-batch.json`, and `latest-preview.md` conventions; summary should mirror the bounded JSON plus Markdown pattern.
- `render_*_preview` functions provide a simple list-of-lines Markdown style that summary rendering can match.
- Existing CLI commands load config, derive state roots, and print safety lines; `summary-preview` can follow the same Typer pattern.
- `tests/test_apply.py` already proves fake GitHub mutation runners; Phase 4 can reuse the idea without live `gh`.

### Established Patterns
- Commands that do not mutate GitHub say so plainly in stdout and write local files.
- JSON records are canonical machine-readable state; Markdown previews are maintainer-readable summaries.
- Tests use temp directories, fixture issues, and local source fixtures. They do not require network, credentials, or live provider calls.
- Policy and apply boundaries are deterministic Python code; summary should aggregate their outputs instead of re-deciding them.

### Integration Points
- Summary reads from `<state_root>/classify/records.json`, `<state_root>/answer/records.json`, `<state_root>/close/records.json`, and `<state_root>/apply/records.json`.
- Summary writes to `<state_root>/summary/records.json` and `<state_root>/summary/latest-preview.md`.
- Documentation connects README quickstart to a fuller operator guide under `docs/`.
- Regression verification connects to existing pytest suite and safety scans in Phase 4 summaries.

</code_context>

<specifics>
## Specific Ideas

- `summary-preview` should work even if only some workflows have been run, because operators may inspect partial batches.
- The summary report should include counts that matter to maintainers: total classified, human review/blocked labels, answer drafts ready, close-suitable records, high-risk close records, applied/failed/skipped apply actions, and missing workflow names.
- Keep summary deterministic and offline so it can be used in CI and local verification.
- Add an operator guide that explicitly mentions local proxy exports and remote-server network forwarding as operational notes, but never includes the private config path contents.

</specifics>

<deferred>
## Deferred Ideas

- Web dashboard, hosted HTML report, recurring automation, GitHub App auth, multi-repo scheduling, and provider cost/quality evaluation remain v2.
- Richer natural-language executive summaries can be added later; Phase 4 needs deterministic counts and safety evidence first.

</deferred>

---

*Phase: 4-Summary, Tests, and Operator Docs*
*Context gathered: 2026-06-16*

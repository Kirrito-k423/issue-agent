# Walking Skeleton — Issue Agent

**Phase:** 1
**Generated:** 2026-06-15

## Capability Proven End-to-End

User can run a local CLI command against fixture issue data and receive bounded preview artifacts that show schema-validated classification proposals with no GitHub mutation.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Python 3.11+ package with Typer CLI | Fits a maintainer automation tool, is easy to test offline, and supports structured JSON/state workflows. |
| Data layer | Local JSON state files under `.issue-agent/state/<owner>__<repo>/classify/` | Phase 1 needs bounded preview state, not a database server. JSON is inspectable and matches existing reference workflows. |
| Auth | GitHub CLI auth for live operations; no stored secrets | The user is already authenticated with `gh`; Phase 1 keeps credentials outside tracked files. |
| Model boundary | Pydantic schemas plus provider interface and deterministic fixture provider | Simple models such as MiniMax can be added behind the interface without letting raw model output control side effects. |
| Interaction surface | CLI command and Markdown preview | The product is an operator tool; the first interaction is command-line, not a web UI. |
| Deployment target | Local editable install plus documented full local run command | Phase 1 proves the full stack locally; remote deployment is unnecessary for a CLI MVP. |
| Directory layout | `issue_agent/` package, `tests/` suite, `examples/` fixtures/config | Keeps implementation small and conventional for later phases. |

## Stack Touched in Phase 1

- [ ] Project scaffold — package metadata, dependency declarations, test runner.
- [ ] CLI route — at least one real Typer command.
- [ ] State store — at least one real JSON write and one real JSON read/update path.
- [ ] Operator interaction — CLI command produces human-readable terminal/Markdown preview output.
- [ ] Local run — documented command exercises config loading, fixture intake, classification proposal, policy validation, and preview state writing.

## Out of Scope (Deferred to Later Slices)

- CodeGraph source lookup.
- Answer drafting.
- Stale cleanup and closure recommendations.
- GitHub label/comment/close apply mode.
- GitHub App auth.
- Web dashboard or scheduled multi-repo service.

## Subsequent Slice Plan

Each later phase adds one vertical slice on top of this skeleton without altering its safety decisions:

- Phase 2: Code-aware triage and source-backed answer previews.
- Phase 3: Evidence-based stale cleanup and explicit GitHub apply mode.
- Phase 4: Summary reporting, safety fixtures, and operator documentation.

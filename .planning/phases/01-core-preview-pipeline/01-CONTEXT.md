# Phase 1: Core Preview Pipeline - Context

**Gathered:** 2026-06-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers the first safe vertical slice of Issue Agent: a Python CLI that can load repository configuration, fetch or read fixture-backed GitHub issue data, run a schema-validated classifier proposal, and write bounded preview artifacts without mutating GitHub. This phase intentionally stops before CodeGraph-backed answer drafting, stale closure recommendations, and public apply mode.

</domain>

<decisions>
## Implementation Decisions

### CLI and Project Shape
- **D-01:** Build the Phase 1 implementation as a Python 3.11+ package with a Typer CLI entrypoint. The CLI should expose a preview classification path first; command names should be explicit and action-oriented rather than hidden behind one generic command.
- **D-02:** Keep the initial code layout small and conventional: `issue_agent/` for implementation, `tests/` for fixtures and unit tests, and a tracked example config file that contains no secrets.
- **D-03:** Phase 1 should include a walking skeleton command that exercises config loading, issue intake, classification schema validation, and preview state writing in one run.

### Configuration and Secrets
- **D-04:** Use YAML repository profiles for non-secret settings: repository name, state root, batch size, label policy, write policy, provider name, and provider base URL.
- **D-05:** Read API keys, GitHub authentication, and proxy values from environment variables only. Do not write provider keys, GitHub tokens, local password paths, or remote-server credentials into tracked files or preview state.
- **D-06:** Include proxy-aware documentation and config examples for `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY`, with `127.0.0.1:7890` as the local Mac convention.

### GitHub Intake
- **D-07:** Prefer `gh` subprocess calls for local GitHub operations in Phase 1 because the user is already authenticated with GitHub CLI. Keep the adapter isolated so REST or GraphQL can be added later without touching workflow logic.
- **D-08:** Phase 1 must support fixture-backed intake so tests and local development do not require live GitHub network access.
- **D-09:** Fetch or load the repository label set before classification, and mark any absent proposed labels as non-applyable rather than creating labels.

### Model and Classification Boundary
- **D-10:** Treat the model as a proposal generator only. It returns structured classification proposals; deterministic Python policy decides whether the proposal is valid for preview.
- **D-11:** Define Pydantic schemas for issue input, model proposal, policy result, evidence references, preview records, and batch state before implementing provider-specific calls.
- **D-12:** Phase 1 should include a provider interface plus a deterministic fixture/mock provider for tests. A MiniMax/OpenAI-compatible provider can be wired through the same interface, but tests must not depend on live model calls.
- **D-13:** Invalid model JSON should be repaired at most once. If still invalid, the issue becomes `human_review` with no public action.

### Preview Safety and State
- **D-14:** Preview mode is the only Phase 1 mode. No `gh issue edit`, `gh issue comment`, `gh issue close`, or label creation command may be reachable from Phase 1 commands.
- **D-15:** State files should be bounded and replaceable: one canonical `records.json` keyed by issue number, one overwritten `pending-batch.json`, and one overwritten `latest-preview.md`.
- **D-16:** Preview records must show both the model proposal and deterministic policy result, including confidence, proposed labels, rejected labels, no-action reason, evidence needs, and validation status.
- **D-17:** The state root should default under `.issue-agent/state/<owner>__<repo>/`, but `.issue-agent/state/` remains ignored by git.

### Phase 1 Scope Fence
- **D-18:** Do not implement CodeGraph source lookup in Phase 1 beyond reserving schema fields for future source evidence.
- **D-19:** Do not implement answer drafting, stale closure recommendations, or public apply mode in Phase 1.
- **D-20:** Do not migrate the existing `skills/github-issue-*` workflows into executable code wholesale. Use them as reference examples for safety rules, state naming, and preview format only.

### the agent's Discretion
- The agent may choose exact module names, helper function names, test fixture shape, and Markdown preview layout as long as the decisions above and Phase 1 requirements are satisfied.
- The agent may decide whether the initial live GitHub intake command is fully implemented in Phase 1 or partially fixture-first, but the CLI must make network use explicit and tests must remain offline-safe.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope and Requirements
- `.planning/PROJECT.md` — Core value, constraints, and project-level decisions.
- `.planning/REQUIREMENTS.md` — Phase 1 requirement IDs and acceptance criteria.
- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, and plan outline.
- `.planning/STATE.md` — Current project position and active concerns.

### Research
- `.planning/research/SUMMARY.md` — Recommended stack, phase ordering, and key risks.
- `.planning/research/STACK.md` — Python, GitHub CLI/API, MiniMax, Pydantic, Typer, and Rich stack details.
- `.planning/research/ARCHITECTURE.md` — Proposed CLI/orchestration/adapter/state layering.
- `.planning/research/FEATURES.md` — Feature priorities and MVP definition.
- `.planning/research/PITFALLS.md` — Safety pitfalls and verification checklist.

### Repository Instructions and Reference Workflows
- `AGENTS.md` — Chinese-first collaboration, proxy handling, secrets, CodeGraph, and preview-first project constraints.
- `skills/github-issue-classify/SKILL.md` — Reference for classification state shape and label safety rules.
- `skills/github-issue-reply/SKILL.md` — Reference for preview-before-comment safety and reply-worthiness separation.
- `skills/github-issue-close/SKILL.md` — Reference for conservative closure policy; Phase 1 does not implement closure.
- `skills/github-issue-summary/SKILL.md` — Reference for bounded summary reporting; Phase 1 only reserves compatible state concepts.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/github-issue-classify/SKILL.md`: useful as a reference for `records.json`, `processed-ids.json`, `pending-batch.json`, and `latest-preview.md` naming, but it is not an executable module to preserve unchanged.
- `skills/github-issue-reply/SKILL.md` and `skills/github-issue-close/SKILL.md`: useful safety language for preview/apply separation and conservative no-action behavior.

### Established Patterns
- The repository currently has planning docs and reference skills, but no Python package or application code. Phase 1 should establish the first implementation pattern rather than trying to match a nonexistent codebase.
- `.gitignore` already ignores `.issue-agent/state/`, `.env*`, Python caches, and virtual environments; generated state and secrets must stay out of commits.

### Integration Points
- New implementation files should connect to the existing project through documented CLI commands and tracked example config, not by mutating `.planning/` files directly.
- State output should default to `.issue-agent/state/<owner>__<repo>/` so later workflows can coexist with the historical local state layout without committing it.

</code_context>

<specifics>
## Specific Ideas

- Prefer command names that make safety obvious, such as a preview classification command whose default behavior cannot mutate GitHub.
- Keep live-provider use optional and testable through fixtures; do not require MiniMax credentials to run tests.
- Make any live GitHub command explicit in docs and CLI help because the user may need proxy settings on this machine or remote servers.

</specifics>

<deferred>
## Deferred Ideas

- CodeGraph-backed source lookup and answer drafting belong to Phase 2.
- Stale cleanup, closure recommendations, and explicit GitHub apply mode belong to Phase 3.
- GitHub App auth, dashboarding, multi-repo scheduling, and provider cost comparison remain v2 work.

</deferred>

---

*Phase: 1-Core Preview Pipeline*
*Context gathered: 2026-06-15*

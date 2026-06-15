# Phase 2 Research: Code-Aware Triage and Answers

**Phase:** 2 - Code-Aware Triage and Answers
**Researched:** 2026-06-15
**Status:** Complete

## Research Question

What does the executor need to know to plan Phase 2 well: CodeGraph-first source lookup, fallback evidence recording, refusal gates for unverified experiment issues, and preview-only source-backed answer drafts?

## Inputs Read

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/02-code-aware-triage-and-answers/02-CONTEXT.md`
- `.planning/phases/01-core-preview-pipeline/01-CONTEXT.md`
- `.planning/phases/01-core-preview-pipeline/01-VERIFICATION.md`
- `.planning/phases/01-core-preview-pipeline/01-03-SUMMARY.md`
- `.planning/research/SUMMARY.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/FEATURES.md`
- `.planning/research/PITFALLS.md`
- `.planning/research/STACK.md`
- `AGENTS.md`
- `skills/github-issue-reply/SKILL.md`
- `issue_agent/models.py`
- `issue_agent/classifier.py`
- `issue_agent/policy.py`
- `issue_agent/state.py`
- `issue_agent/preview.py`
- `issue_agent/cli.py`

## Key Findings

### 1. Source lookup should be an adapter, not policy logic

The CodeGraph rule is a repository-reading concern. It should live behind a small adapter that can answer:

- Is `.codegraph/` present in the target repo?
- Which lookup mode was attempted?
- Did CodeGraph succeed, fail, or fall back?
- Which source evidence records were found?

Policy code should consume structured evidence; it should not know how CodeGraph commands are executed.

### 2. Evidence needs a richer typed shape

Phase 1 has `EvidenceRef(kind, value, reason)`. Phase 2 needs source-specific fields while staying backward-compatible:

- `lookup_mode`: `codegraph`, `fallback_search`, `unavailable`, or similar.
- `path`: repository-relative path.
- `symbol`: optional function/class/module symbol.
- `snippet`: compact source excerpt.
- `line_start` and `line_end`: optional citation line range.
- `fallback_reason`: why CodeGraph was not used or why fallback was needed.

This gives previews enough detail to justify drafts and skips.

### 3. Refusal gates should run before drafting

The user's strongest requirement is not to answer experiment or environment issues when the agent cannot reproduce them. That gate must run deterministically before answer drafting:

```text
issue + classifier proposal + run evidence + source evidence
    -> reply-worthiness/no-answer policy
    -> draft only if supported
```

If run evidence is missing for an experiment, hardware, dependency, install, or environment issue, the output should be a preview-safe skip such as `request_info`, `human_review`, or `blocked` with reason `requires_unverified_reproduction`.

### 4. Answer previews can start deterministic

Phase 2 does not need live MiniMax calls to prove answer safety. A deterministic draft renderer can cite source paths and snippets, which validates the evidence plumbing and state format. A later provider can replace the text generator while keeping the same policy gates.

### 5. CLI should stay explicit and offline-testable

The existing `preview` command should remain intact. Add a separate answer-preview command that accepts a target repository root and fixture issues. Tests can create a small fixture source repo with and without `.codegraph/`, then inject command runners to simulate CodeGraph.

## Recommended Plan Shape

### Plan 02-01: CodeGraph Adapter and Source Evidence

Add richer evidence schemas, a CodeGraph-first lookup adapter, fallback source search, and tests for CodeGraph-present and CodeGraph-absent behavior.

### Plan 02-02: No-Answer Gates

Add deterministic reply-worthiness policy that blocks unverified experiment/environment issues and blocks code answers with no source evidence.

### Plan 02-03: Answer Preview Workflow

Add preview-only answer draft generation, bounded answer state, Markdown preview rendering, and a CLI command that proves source-backed drafts and no-answer skips end to end.

## Validation Strategy

Phase 2 verification should prove:

- A fixture repo with `.codegraph/` routes through a stubbed CodeGraph command before fallback search.
- A fixture repo without `.codegraph/` records fallback mode in evidence.
- Reproduction-only issues without run evidence do not produce answer drafts.
- Code logic questions without source evidence do not produce answer drafts.
- Code logic questions with source evidence produce local draft previews with citations.
- No Phase 2 code can post comments, edit labels, close issues, create labels, or delete labels.
- All tests run offline without GitHub, MiniMax, CodeGraph installation, or network.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| CodeGraph is assumed to exist everywhere | Detect `.codegraph/` per target repo and record fallback mode. |
| Fallback search creates false confidence | Store `lookup_mode=fallback_search` and include fallback reason in previews. |
| Model prose bypasses refusal policy | Run deterministic no-answer gates before any draft rendering. |
| Answer records bloat `records.json` | Store draft bodies in per-issue files and keep JSON records compact. |
| Tests depend on real CodeGraph | Use injectable command runner and fixture repos. |

## Phase 2 File Targets

Likely implementation files:

- `issue_agent/codegraph.py`
- `issue_agent/evidence.py`
- `issue_agent/answer.py`
- `issue_agent/models.py`
- `issue_agent/classifier.py`
- `issue_agent/policy.py`
- `issue_agent/state.py`
- `issue_agent/preview.py`
- `issue_agent/cli.py`
- `examples/issues.fixture.json`
- `tests/test_codegraph.py`
- `tests/test_answer_policy.py`
- `tests/test_answer_preview.py`
- `tests/fixtures/source_repo/`

## Open Questions for Planning

None blocking. Exact module boundaries and field names can be chosen during implementation as long as CodeGraph-first evidence, no-answer gates, and preview-only answers are enforced.

## RESEARCH COMPLETE

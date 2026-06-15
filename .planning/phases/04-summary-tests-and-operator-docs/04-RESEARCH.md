---
phase: 04-summary-tests-and-operator-docs
type: research
tags: [summary, tests, docs, safety, state]
created: 2026-06-16
---

# Phase 4 Research: Summary, Tests, and Operator Docs

## Research Question

What needs to be known to plan Phase 4 well, without expanding scope beyond aggregate reporting, deterministic regression coverage, and operator documentation?

## Current System Shape

Issue Agent already has four local workflows:

- `preview` writes classification state under `classify/`.
- `answer-preview` writes answer records, Markdown preview, and local drafts under `answer/`.
- `close-preview` writes closure recommendation state under `close/`.
- `apply-close` validates preview state and records explicit mutation outcomes under `apply/`.

All existing tests are offline. They use fixture issues, temp state roots, a fixture source repository, deterministic providers, and fake GitHub mutation runners.

## Implementation Findings

### Summary Aggregation

- The summary layer should read state files instead of recomputing decisions. Recomputing policy at summary time would violate Phase 4 decision D-01 and could diverge from the reviewed preview artifacts.
- Existing record files are JSON objects keyed by issue number or action id:
  - `classify/records.json` contains `PreviewRecord`.
  - `answer/records.json` contains `PreviewRecord` with answer fields and draft paths.
  - `close/records.json` contains `ClosureDecision`.
  - `apply/records.json` contains `ApplyResult`.
- A new `issue_agent/summary.py` module is the cleanest boundary. It can expose `build_summary_report(state_root)` and helper functions without coupling the aggregation logic to CLI or rendering.
- Summary records should tolerate missing workflow directories. Operators may run only part of the workflow and still want a report.

### State and Rendering

- `issue_agent/state.py` already owns bounded writes. Adding `write_summary_preview(state_root, report)` keeps the file layout consistent.
- `issue_agent/preview.py` already renders Markdown previews through simple list construction. Adding `render_summary_preview(report)` fits the existing pattern.
- Existing preview writers overwrite `latest-preview.md` and replace canonical JSON records. Summary can write a single canonical report under `summary/records.json`; it does not need `pending-batch.json` unless execution later finds a concrete need.

### CLI Shape

- Current commands are explicit:
  - `preview`
  - `answer-preview`
  - `close-preview`
  - `apply-close`
- `summary-preview` is the safest matching name. It communicates local preview behavior and avoids implying upload or publication.
- CLI output should include a no-mutation line such as `Mode: preview; no GitHub issues were changed.` plus the latest summary path.

### Regression Coverage

- Existing test files already cover each workflow independently. Phase 4 should add cross-workflow regression tests rather than duplicating every unit case.
- A useful regression fixture should run the local CLI commands against a temp state root, then call summary aggregation. Apply can be covered through fake-runner functions instead of invoking the real CLI, because the CLI would call live `gh`.
- Safety scans should be explicit and allow-listed. After Phase 3, `gh issue` mutation strings are expected only in `issue_agent/github.py`, `tests/test_apply.py`, and documentation that warns about apply mode.
- Secret scanning should avoid false positives from placeholder environment variable names such as `MINIMAX_API_KEY=` in docs. It should look for actual credential-like values, private local config paths, and generated state files in the tracked file list.

### Documentation

- README should remain a short quickstart with command examples.
- A new `docs/OPERATOR_GUIDE.md` can carry the longer operational material:
  - config and env variables
  - local proxy convention (`127.0.0.1:7890`)
  - remote-server networking note without credentials
  - CodeGraph-first behavior and fallback evidence
  - preview/apply distinction
  - when not to answer or close
  - release verification commands
- Documentation should not mention private paths from the user's local configuration files. `AGENTS.md` already contains a public-safe version of the environment rules and can be cited as a source.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Summary silently recomputes decisions | Plan summary as read-only aggregation from existing state only. |
| Summary fails on partial state | Tests cover missing workflow directories and report `missing_workflows`. |
| Apply command accidentally runs in tests | Use fake-runner apply functions; do not invoke `apply-close` against live `gh`. |
| Safety scan blocks expected docs | Use allow-list for explicit apply adapter/tests/docs and focused secret patterns. |
| Docs expose local secrets | Include proxy examples only; scan for private config paths, tokens, and generated state. |

## Validation Architecture

Phase 4 verification should combine:

1. Targeted unit tests for summary aggregation and rendering.
2. CLI smoke test for `summary-preview`.
3. Cross-workflow regression test using temp state and fixtures.
4. Mutation-surface scan that confirms `gh issue` strings are isolated to explicit apply boundaries.
5. Secret/state hygiene scan over tracked files.
6. Full `pytest` run.

## Recommended Plan Split

1. `04-01`: Aggregate summary report and `summary-preview` command.
2. `04-02`: Regression fixture suite and safety verification.
3. `04-03`: Operator documentation, proxy guidance, and release readiness cleanup.

## RESEARCH COMPLETE

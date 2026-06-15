# Issue Agent

## What This Is

Issue Agent is a lightweight GitHub issue handling assistant for code repositories. It uses simple LLMs such as MiniMax for bounded judgment tasks, combines them with repository-aware code reading through CodeGraph, and produces conservative issue actions: classify, answer, request information, mark as not actionable, or propose closure.

The project is for maintainers who want help processing large issue backlogs without letting automation guess beyond evidence. Existing `skills/github-issue-*` files and `.issue-agent/state/` records are reference material from prior experiments, not a required implementation baseline.

## Core Value

Every public issue action must be grounded in visible repository evidence, and the default action under uncertainty is no public mutation.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Build a configurable issue intake pipeline that fetches GitHub issues, labels, comments, linked PRs, and repository metadata.
- [ ] Configure CodeGraph as the primary code-reading accelerator when a target repository has a `.codegraph/` index.
- [ ] Implement an LLM-based issue classifier with explicit categories for experiment/reproduction requests, code logic questions, usage questions, stale PR or issue cleanup, feature requests, and unsafe/unknown cases.
- [ ] Refuse to answer experiment or environment reproduction issues when the agent cannot run or verify the requested environment.
- [ ] For code logic or repository behavior questions, read relevant source before drafting an answer, using CodeGraph first and shell/search fallback when CodeGraph is unavailable.
- [ ] For stale PR or issue cleanup, require evidence that the item is obsolete, superseded, resolved, duplicate, unsupported, or waiting on missing information before recommending closure.
- [ ] Maintain bounded local state for previews, decisions, evidence, and applied GitHub mutations.
- [ ] Support preview-first operation and require explicit apply mode before posting comments, applying labels, or closing issues.
- [ ] Provide a small-model-friendly prompt and schema layer so models such as MiniMax can make structured decisions without controlling side effects directly.

### Out of Scope

- Fully automated experimental reproduction — remote environments may lack dependencies, hardware, or network, and unverified experiments should not become public answers.
- Trusting LLM judgments without source or issue evidence — simple models are useful for triage, not for unsupported conclusions.
- Creating missing GitHub labels automatically — repository label taxonomy belongs to maintainers.
- Replacing human maintainer judgment for roadmap, policy, security, or controversial product decisions — the agent should surface evidence and recommend, not decide alone.
- Browser-only GitHub automation — prefer `gh` and API workflows that are auditable and scriptable.

## Context

The current repository contains four prior GitHub issue workflow skills:

- `github-issue-classify`: batch label preview/apply with bounded state.
- `github-issue-reply`: draft bilingual maintainer-style replies.
- `github-issue-close`: Chinese conservative closure assessment.
- `github-issue-summary`: publish bounded automation summaries.

Those files demonstrate useful state shapes and safety rules, but the new project should generalize beyond one repository and one manual skill workflow. The target direction is an executable issue-processing system with configuration, model adapters, CodeGraph-aware code reading, schemas, preview artifacts, and controlled GitHub mutations.

Historical state under `.issue-agent/state/verl-project__verl/` shows a real trial against `verl-project/verl`: classification proposed labels for 20 issues, reply assessment skipped 10 issues, and closure assessment was intentionally conservative. This supports the project principle that the agent should prefer "skip" or "needs evidence" over speculative action.

The user's operating environment is a China-based Mac. External network access may require proxy configuration through `127.0.0.1:7890`; remote development servers may lack direct network access and may need local proxy forwarding.

## Constraints

- **Language**: Communicate with the user in Chinese — project operation and status updates should be Chinese-first when user-facing.
- **Network**: Support proxy-aware operation — GitHub and model-provider access may require local proxy configuration.
- **Evidence**: Public comments, labels, and closures require concrete evidence references — issue links, comments, PRs, docs, or source paths.
- **Safety**: Default to preview mode — no GitHub mutation unless explicitly configured or requested.
- **Model capability**: Design for simple LLMs — constrain outputs with schemas, deterministic prechecks, and post-validation.
- **Code reading**: Use CodeGraph before grep/find when `.codegraph/` exists — this is a project-level rule from the repository instructions.
- **State**: Keep process state bounded and replaceable — avoid unbounded history growth in JSON records.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat existing skill workflows as reference only | The current files are useful experiments, but the next version should become a configurable executable system rather than inheriting every workflow detail | — Pending |
| Preview-first GitHub mutations | Maintainer trust depends on seeing proposed labels, replies, and closures before public action | — Pending |
| CodeGraph-first code reading | The user explicitly wants CodeGraph to accelerate repository understanding for code questions | — Pending |
| No answer for unverified experiment reproduction issues | Without an executable environment, public answers would be speculation | — Pending |
| Simple-model schema boundary | Models such as MiniMax should classify and explain, while deterministic code owns fetching, validation, and mutation | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-15 after initialization*

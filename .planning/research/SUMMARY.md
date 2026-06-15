# Project Research Summary

**Project:** Issue Agent
**Domain:** GitHub issue automation with code-aware LLM triage
**Researched:** 2026-06-15
**Confidence:** MEDIUM-HIGH

## Executive Summary

Issue Agent should be built as a conservative CLI-first automation system. The most important architectural choice is to separate model judgment from side effects: MiniMax or another simple LLM may classify and propose an action, but deterministic code must validate schema, enforce policy, write preview state, and require explicit apply mode before GitHub mutation.

The best MVP is not a broad autonomous maintainer. It is a reliable preview pipeline that fetches issue context, understands existing repo labels, detects CodeGraph availability, builds evidence packets, and produces structured decisions. This directly supports the user's rule: do not answer experiment/reproduction issues without an environment; do read code before answering code logic questions; only recommend closing stale items when evidence shows they are resolved, duplicate, superseded, unsupported, or waiting on missing information.

The main risk is maintainer trust. A single unsupported public comment or unsafe closure can damage confidence more than a hundred correct previews help. The roadmap should therefore front-load schemas, previews, state, and no-mutation safety before comment/close apply mode.

## Key Findings

### Recommended Stack

Use Python 3.11+ with a Typer CLI, Pydantic v2 schemas, local JSON/Markdown state, `gh` for GitHub operations, a small GitHub REST fallback layer, a CodeGraph shell adapter, and a MiniMax/OpenAI-compatible model adapter.

**Core technologies:**
- Python: orchestration, CLI, state, and tests.
- `gh`: local authenticated GitHub issue/PR operations.
- Pydantic v2: typed decision schemas and JSON Schema generation.
- MiniMax OpenAI-compatible API: budget/simple model provider.
- CodeGraph CLI: code-reading accelerator when `.codegraph/` exists.

### Expected Features

**Must have (table stakes):**
- Repository profile config.
- GitHub issue intake with labels/comments/linked references.
- Existing-label-aware classifier.
- CodeGraph detection and source evidence capture.
- Preview-first JSON and Markdown artifacts.
- Explicit apply mode for any public mutation.
- Bounded per-issue state.

**Should have (competitive):**
- No-answer gate for unverified experiment/reproduction issues.
- Code logic answer drafts with source citations.
- Evidence-based stale PR/issue closure preview.
- Small-model prompt/schema profiles.

**Defer (v2+):**
- GitHub App auth.
- Web dashboard.
- Multi-repo scheduling.
- Full provider router and cost dashboard.

### Architecture Approach

Build the system in layers: CLI -> orchestration -> adapters -> state. The classifier receives a compact evidence packet and returns a typed decision. Policy code then decides whether that decision can become a previewed label, answer, information request, closure recommendation, or human-review item.

**Major components:**
1. CLI and config loader — user commands and per-repo policy.
2. GitHub adapter — issues, comments, labels, PR references, mutations.
3. CodeGraph adapter — source discovery and code evidence.
4. Evidence builder — compact context with citations.
5. Model adapter — MiniMax/OpenAI-compatible structured calls.
6. Policy validator — safety gates.
7. State and preview writer — bounded audit trail.
8. Apply engine — explicit GitHub mutations.

### Critical Pitfalls

1. **Public mutation from unvalidated model output** — prevent with schema validation, policy gates, preview state, and explicit apply.
2. **Answering reproduction issues without an environment** — route to no-answer/request-info/human-review.
3. **Code logic answers without source evidence** — require CodeGraph or fallback source evidence before drafting.
4. **Closing old but useful issues** — require specific resolved/duplicate/superseded/unsupported/waiting-info evidence.
5. **Noisy replies** — add reply-worthiness gate and skip when evidence is weak.

## Implications for Roadmap

### Phase 1: Core Preview Pipeline
**Rationale:** Safety and trust must come first.
**Delivers:** Config, GitHub intake, label fetch, Pydantic schemas, classifier preview, bounded state.
**Addresses:** Table-stakes workflow and no-mutation default.
**Avoids:** Public mutation from unvalidated model output.

### Phase 2: Code-Aware Answering and No-Answer Gates
**Rationale:** The user's highest-value branch is answering code logic/questions by reading code, while refusing unverified experiments.
**Delivers:** CodeGraph adapter, fallback source search, evidence packets, answer draft preview, no-answer decisions.
**Uses:** CodeGraph CLI, MiniMax model adapter, policy gates.
**Implements:** Source-backed answer flow.

### Phase 3: Stale Cleanup and Apply Mode
**Rationale:** Closure is high-risk and should come after evidence and preview foundations work.
**Delivers:** Linked PR/comment inspection, closure policy, label/comment/close apply mode, summary report.
**Implements:** Evidence-based cleanup and controlled GitHub mutations.

### Phase Ordering Rationale

- Classification and preview state are prerequisites for all later actions.
- Code-aware answering depends on evidence capture and source retrieval.
- Closure/apply mode is intentionally last because it creates public side effects.
- This order directly mitigates the most serious trust and safety pitfalls.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** CodeGraph command behavior in real indexed repositories.
- **Phase 3:** GitHub close reasons, duplicate marking, linked PR resolution patterns, and rate-limit handling.

Phases with standard patterns:
- **Phase 1:** Python CLI, Pydantic validation, JSON/Markdown local state.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | GitHub, MiniMax, Pydantic, Typer, and Rich have official docs for required primitives. |
| Features | MEDIUM-HIGH | Strongly grounded in user goals and prior local skill experiments. |
| Architecture | MEDIUM-HIGH | Standard adapter + schema + policy layering fits the risk profile. |
| Pitfalls | HIGH | Prior local state and public mutation risk make safety requirements clear. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **CodeGraph runtime details:** Validate exact CLI output and failure modes during Phase 2.
- **MiniMax structured-output reliability:** Test actual models with the decision schema before enabling broad use.
- **GitHub linked reference extraction:** Decide whether REST, GraphQL, or issue-body/comment parsing is enough for closure evidence.
- **Remote server proxying:** If execution moves to a remote server, document proxy forwarding for GitHub and model calls.

## Sources

### Primary (HIGH confidence)
- GitHub REST Issues docs: https://docs.github.com/rest/issues
- GitHub REST Issue Comments docs: https://docs.github.com/rest/issues/comments
- GitHub REST Labels docs: https://docs.github.com/en/rest/issues/labels
- GitHub REST Rate Limits docs: https://docs.github.com/rest/rate-limit/rate-limit
- GitHub GraphQL docs: https://docs.github.com/en/graphql
- GitHub CLI issue manual: https://cli.github.com/manual/gh_issue
- MiniMax Chat Completions API: https://platform.minimax.io/docs/api-reference/text-chat-openai
- MiniMax OpenAI-compatible API: https://platform.minimax.io/docs/api-reference/text-openai-api
- MiniMax Tool Use guide: https://platform.minimax.io/docs/guides/text-m3-function-call
- Pydantic JSON Schema docs: https://pydantic.dev/docs/validation/latest/concepts/json_schema/

### Secondary (MEDIUM confidence)
- Typer docs: https://typer.tiangolo.com/
- Rich table docs: https://rich.readthedocs.io/en/latest/tables.html
- Existing local skill docs and state under `skills/` and `.issue-agent/state/`.

---
*Research completed: 2026-06-15*
*Ready for roadmap: yes*

# Architecture Research

**Domain:** GitHub issue automation with code-aware LLM triage
**Researched:** 2026-06-15
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  classify | answer | close-preview | apply | summary         │
├─────────────────────────────────────────────────────────────┤
│                     Orchestration Layer                       │
│  repo profile -> issue intake -> evidence -> model decision   │
│        -> policy validation -> preview/state -> apply         │
├─────────────────────────────────────────────────────────────┤
│                      Integration Layer                        │
│  GitHub adapter | CodeGraph adapter | Model adapter           │
├─────────────────────────────────────────────────────────────┤
│                         State Layer                           │
│  records.json | pending-batch.json | latest-preview.md        │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| CLI | Expose user commands and flags. | Typer app with subcommands. |
| Config loader | Merge defaults, repo profiles, environment proxy/model settings. | YAML + Pydantic settings model. |
| GitHub adapter | Fetch issues, comments, labels, PR references; apply mutations. | `gh` subprocess first, `gh api` or httpx fallback. |
| CodeGraph adapter | Locate source evidence when target repo is indexed. | Shell wrapper around `codegraph explore` and `codegraph node`. |
| Evidence builder | Normalize issue, comments, PR, docs, and source snippets. | Pydantic models with citation references. |
| Model adapter | Call MiniMax/OpenAI-compatible models. | httpx or OpenAI-compatible SDK style client. |
| Decision validator | Validate JSON output and enforce policy gates. | Pydantic schema plus deterministic checks. |
| State store | Maintain bounded per-issue records and latest previews. | JSON files and Markdown previews. |
| Apply engine | Perform GitHub side effects only after preview and explicit apply. | `gh issue edit/comment/close`. |

## Recommended Project Structure

```text
issue_agent/
├── cli.py              # Typer command entrypoint
├── config.py           # Repo profile and environment loading
├── github.py           # gh/REST adapter
├── codegraph.py        # CodeGraph detection and source lookup
├── models.py           # Pydantic data and decision schemas
├── llm.py              # MiniMax/OpenAI-compatible provider calls
├── evidence.py         # Evidence assembly and citation normalization
├── policy.py           # Safety gates and action eligibility
├── state.py            # Bounded JSON/Markdown state writes
├── preview.py          # Human-readable reports
└── workflows/
    ├── classify.py
    ├── answer.py
    ├── close.py
    └── summary.py
tests/
├── test_policy.py
├── test_models.py
├── test_state.py
└── fixtures/
```

### Structure Rationale

- **Adapters are isolated:** GitHub, CodeGraph, and model providers can fail independently and be tested with fixtures.
- **Policy is separate from prompts:** LLMs propose; deterministic code decides whether a public action is eligible.
- **State is centralized:** bounded state rules remain consistent across classify, answer, and closure workflows.

## Architectural Patterns

### Pattern 1: Model-Proposes, Policy-Disposes

**What:** The LLM returns a structured proposal; deterministic code validates it and may downgrade to preview/no-action.
**When to use:** All public-facing decisions.
**Trade-offs:** Slightly slower and more code, but far safer for simple models.

```python
decision = IssueDecision.model_validate_json(raw_model_output)
final = policy.apply(decision, evidence, repo_profile)
```

### Pattern 2: Evidence Packet Before Prompt

**What:** Build a compact evidence packet before the model sees the issue.
**When to use:** Classification, answer drafting, closure checks.
**Trade-offs:** Requires more deterministic fetching, but reduces model hallucination.

### Pattern 3: Preview as the Unit of Trust

**What:** Every run writes a JSON batch and Markdown preview before any mutation.
**When to use:** All workflows.
**Trade-offs:** Adds files, but creates auditability and resumability.

## Data Flow

### Request Flow

```text
User command
    -> Config loader
    -> GitHub adapter fetches issues/comments/labels
    -> CodeGraph adapter fetches source evidence when needed
    -> Evidence builder creates compact packet
    -> Model adapter returns structured proposal
    -> Pydantic validates proposal
    -> Policy gate approves/downgrades/rejects action
    -> State store writes preview records
    -> Apply engine mutates GitHub only with explicit apply
```

### Key Data Flows

1. **Classification:** issue context + labels -> classifier -> label proposals -> preview/apply.
2. **Code answer:** issue question -> CodeGraph/source evidence -> answer draft -> preview/comment.
3. **Closure:** issue + comments + linked PRs -> closure policy -> recommendation -> preview/close.
4. **Summary:** workflow state -> aggregate report -> tracking issue preview/apply.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single maintainer, one repo | CLI + local JSON state is enough. |
| Many repos, manual runs | Add repo profiles and deterministic batching. |
| Scheduled team automation | Add GitHub App auth, queueing, database state, and stricter rate-limit handling. |

### Scaling Priorities

1. **First bottleneck:** GitHub API/CLI request volume. Fix with batching, pagination, caching labels, and rate-limit checks.
2. **Second bottleneck:** Model context size. Fix with evidence packet trimming and CodeGraph-targeted source retrieval.
3. **Third bottleneck:** Maintainer review load. Fix with concise previews and confidence filters.

## Anti-Patterns

### Anti-Pattern 1: Title-Only Classification

**What people do:** Label issues from title keywords.
**Why it's wrong:** Titles omit reproduction, linked fixes, and maintainer context.
**Do this instead:** Fetch body, labels, comments, and linked PR evidence before classification.

### Anti-Pattern 2: Age-Based Closure

**What people do:** Close old issues because they are old.
**Why it's wrong:** Roadmaps, feature requests, and contribution tasks can remain valid for years.
**Do this instead:** Require explicit resolved/duplicate/superseded/unsupported/waiting-for-info evidence.

### Anti-Pattern 3: Source Search After Answer Draft

**What people do:** Draft answer first, then look for code to support it.
**Why it's wrong:** This biases the evidence search.
**Do this instead:** Build source evidence before generating the answer.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| GitHub CLI | Subprocess commands with `--json` | Best local fit because auth already exists. |
| GitHub REST API | `gh api` or httpx fallback | Needed for comments, labels, rate limits, and less common operations. |
| GitHub GraphQL API | Future optional adapter | Useful for complex cross-linked issue/PR queries. |
| MiniMax API | OpenAI-compatible Chat Completions/Responses | Keep provider behind schema-validated adapter. |
| CodeGraph CLI | Shell adapter | Only use when `.codegraph/` exists in target repo. |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Workflow -> GitHub adapter | Typed request/response models | Avoid raw shell output outside adapter. |
| Workflow -> Model adapter | Evidence packet + schema | Keep prompts compact for simple models. |
| Model adapter -> Policy | Pydantic decision objects | Invalid model output never reaches apply. |
| Policy -> State | Final decision records | State should capture both model proposal and policy result. |

## Sources

- GitHub REST Issues docs: https://docs.github.com/rest/issues
- GitHub REST Issue Comments docs: https://docs.github.com/rest/issues/comments
- GitHub REST Labels docs: https://docs.github.com/en/rest/issues/labels
- GitHub GraphQL docs: https://docs.github.com/en/graphql
- GitHub CLI issue manual: https://cli.github.com/manual/gh_issue
- MiniMax OpenAI-compatible API docs: https://platform.minimax.io/docs/api-reference/text-chat-openai
- MiniMax tool-use guide: https://platform.minimax.io/docs/guides/text-m3-function-call
- Pydantic JSON Schema docs: https://pydantic.dev/docs/validation/latest/concepts/json_schema/

---
*Architecture research for: GitHub issue automation with code-aware LLM triage*
*Researched: 2026-06-15*

# Stack Research

**Domain:** GitHub issue automation with code-aware LLM triage
**Researched:** 2026-06-15
**Confidence:** HIGH for GitHub and schema validation, MEDIUM for model-provider abstraction

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.11+ | CLI, orchestration, state management | Mature subprocess, JSON, typing, packaging, and testing ecosystem; good fit for a maintainer automation tool. |
| GitHub CLI (`gh`) | current installed CLI | Issue/PR fetch and mutation | Already authenticated locally; supports issue list/view/comment/edit/close commands and JSON output. |
| GitHub REST API | 2022-11-28 API version or current `gh api` default | Direct API fallback for issues, comments, labels, rate limits | Official endpoints cover issues, issue comments, labels, and rate-limit status. |
| CodeGraph CLI | project-provided CLI when `.codegraph/` exists | Repository-aware code reading | Matches the user's repo instructions: use `codegraph explore` and `codegraph node` before grep/find when indexed. |
| MiniMax OpenAI-compatible API | MiniMax-M3 or M2.x | Budget-friendly structured LLM decisions | MiniMax documents OpenAI-compatible Chat Completions and Responses APIs, plus tool definitions for agentic flows. |
| Pydantic | v2 | Decision schemas and validation | Generates JSON Schema from typed models and validates model output before any side effect. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Typer | current | CLI commands | Use for `issue-agent classify`, `answer`, `close-preview`, `apply`, `summary`, and config commands. |
| Rich | current | Human-readable previews | Use for terminal tables and clear preview summaries. |
| PyYAML | current | Config loading | Use for repository profiles, provider settings, label maps, and policy rules. |
| httpx | current | Provider and REST calls | Use when `gh` is insufficient or for direct MiniMax/OpenAI-compatible calls. |
| pytest | current | Tests | Cover classification policy, schema validation, state replacement, and no-mutation preview behavior. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `gh` | Authenticated GitHub operations | Prefer `gh issue` commands for local user workflows; use `gh api` for endpoints not exposed cleanly by CLI commands. |
| `jq` | Shell JSON inspection | Helpful for debugging previews and state files, but Python code should use structured JSON parsing. |
| `codegraph` | Source discovery | Invoke only when target repo has `.codegraph/`; otherwise fall back to `rg`, `gh search`, or direct file reads. |
| `ruff` | Formatting/linting | Add once code exists; keep MVP checks simple. |

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
pip install typer rich pydantic pyyaml httpx pytest
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Python CLI | Node.js CLI | Use Node if the project later needs a VS Code extension or web dashboard first. |
| `gh` first | Direct GitHub REST everywhere | Use REST for fine-grained batching, rate-limit control, or GitHub App auth. |
| Pydantic schemas | Hand-written JSON validation | Only acceptable for tiny prototypes; schema drift becomes risky quickly. |
| MiniMax direct/OpenAI-compatible | LiteLLM proxy | Use LiteLLM when multiple providers must be switched at runtime or centralized cost tracking is needed. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Free-form LLM text as the action source | Hard to validate; unsafe before public comments, labels, or closure. | Typed decision schemas plus deterministic policy gates. |
| Browser scraping GitHub issues | Fragile and hard to audit. | `gh`, REST, or GraphQL APIs. |
| Auto-creating repo labels | Label taxonomies are maintainer-owned. | Fetch existing labels and only apply configured labels that exist. |
| Direct public mutation from model output | Simple models can overgeneralize. | Preview files, evidence checks, and explicit apply mode. |

## Stack Patterns by Variant

**If the target repo is already indexed by CodeGraph:**
- Use `codegraph explore "<issue question>"` to locate likely symbols and call paths.
- Use `codegraph node <symbol-or-file>` to capture exact source snippets for evidence.

**If the target repo lacks CodeGraph:**
- Fall back to `rg`, file reads, and targeted GitHub code search.
- Record `codegraph_available=false` in the decision evidence so downstream reviewers know the limitation.

**If MiniMax structured output is weak for a model/version:**
- Use provider JSON mode or tool calling when available.
- Validate with Pydantic and retry once with a compact repair prompt.
- If still invalid, mark the issue as `needs_human_review`.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| MiniMax OpenAI-compatible API | OpenAI SDK style calls | MiniMax documents Chat Completions and Responses compatible endpoints; verify exact model IDs at runtime. |
| Pydantic v2 | JSON Schema Draft 2020-12 | `BaseModel.model_json_schema()` can drive model response schemas. |
| `gh issue` commands | GitHub authenticated CLI | Use `--repo`, `--json`, and `--jq` for automation-friendly output. |

## Sources

- GitHub REST API Issues docs: https://docs.github.com/rest/issues
- GitHub REST API Issue Comments docs: https://docs.github.com/rest/issues/comments
- GitHub REST API Labels docs: https://docs.github.com/en/rest/issues/labels
- GitHub REST API Rate Limits docs: https://docs.github.com/rest/rate-limit/rate-limit
- GitHub CLI issue manual: https://cli.github.com/manual/gh_issue
- GitHub CLI issue list/view/edit/comment/close manuals: https://cli.github.com/manual/gh_issue_list, https://cli.github.com/manual/gh_issue_view, https://cli.github.com/manual/gh_issue_edit, https://cli.github.com/manual/gh_issue_comment, https://cli.github.com/manual/gh_issue_close
- MiniMax Chat Completions API: https://platform.minimax.io/docs/api-reference/text-chat-openai
- MiniMax OpenAI SDK compatibility: https://platform.minimax.io/docs/api-reference/text-openai-api
- MiniMax Tool Use guide: https://platform.minimax.io/docs/guides/text-m3-function-call
- Pydantic JSON Schema docs: https://pydantic.dev/docs/validation/latest/concepts/json_schema/
- Typer docs: https://typer.tiangolo.com/
- Rich table docs: https://rich.readthedocs.io/en/latest/tables.html

---
*Stack research for: GitHub issue automation with code-aware LLM triage*
*Researched: 2026-06-15*

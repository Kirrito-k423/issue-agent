<!-- GSD:project-start source:PROJECT.md -->

## Project

**Issue Agent**

Issue Agent is a lightweight GitHub issue handling assistant for code repositories. It uses simple LLMs such as MiniMax for bounded judgment tasks, combines them with repository-aware code reading through CodeGraph, and produces conservative issue actions: classify, answer, request information, mark as not actionable, or propose closure.

The project is for maintainers who want help processing large issue backlogs without letting automation guess beyond evidence. Existing `skills/github-issue-*` files and `.issue-agent/state/` records are reference material from prior experiments, not a required implementation baseline.

**Core Value:** Every public issue action must be grounded in visible repository evidence, and the default action under uncertainty is no public mutation.

### Constraints

- **Language**: Communicate with the user in Chinese — project operation and status updates should be Chinese-first when user-facing.
- **Network**: Support proxy-aware operation — GitHub and model-provider access may require local proxy configuration.
- **Local environment**: This project is commonly developed on a China-based macOS machine. When public internet access fails, try proxy-aware commands with `127.0.0.1:7890` via `HTTPS_PROXY`, `HTTP_PROXY`, or `ALL_PROXY`.
- **Secrets**: Never commit local machine credentials, remote-server passwords, provider API keys, or private config paths. Keep secret-bearing files outside the repo or in ignored `.env*` files.
- **Evidence**: Public comments, labels, and closures require concrete evidence references — issue links, comments, PRs, docs, or source paths.
- **Safety**: Default to preview mode — no GitHub mutation unless explicitly configured or requested.
- **Model capability**: Design for simple LLMs — constrain outputs with schemas, deterministic prechecks, and post-validation.
- **Code reading**: Use CodeGraph before grep/find when `.codegraph/` exists — this is a project-level rule from the repository instructions.
- **State**: Keep process state bounded and replaceable — avoid unbounded history growth in JSON records.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

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

- Use `codegraph explore "<issue question>"` to locate likely symbols and call paths.
- Use `codegraph node <symbol-or-file>` to capture exact source snippets for evidence.
- Fall back to `rg`, file reads, and targeted GitHub code search.
- Record `codegraph_available=false` in the decision evidence so downstream reviewers know the limitation.
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

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->

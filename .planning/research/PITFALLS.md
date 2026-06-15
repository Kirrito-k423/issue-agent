# Pitfalls Research

**Domain:** GitHub issue automation with code-aware LLM triage
**Researched:** 2026-06-15
**Confidence:** HIGH for safety pitfalls, MEDIUM for scaling pitfalls

## Critical Pitfalls

### Pitfall 1: Public Mutation From Unvalidated Model Output

**What goes wrong:**
The model proposes labels, comments, or closure and the tool applies them directly.

**Why it happens:**
The workflow treats the LLM as an action engine instead of a bounded classifier.

**How to avoid:**
Validate every model response with Pydantic, run deterministic policy checks, write preview state, and require explicit apply mode.

**Warning signs:**
Commands like `comment`, `edit`, or `close` can run without a preview file or `--apply`.

**Phase to address:**
Phase 1.

---

### Pitfall 2: Answering Reproduction Issues Without an Environment

**What goes wrong:**
The agent gives a confident answer to an experiment, hardware, dependency, or runtime issue it did not reproduce.

**Why it happens:**
Issue automation rewards activity, but reproduction issues require real environments.

**How to avoid:**
Classify these as `needs_repro_environment`, `request_info`, or `human_review`; do not answer unless the run evidence exists.

**Warning signs:**
Draft answer references expected behavior without source, docs, logs, or an executed command.

**Phase to address:**
Phase 2.

---

### Pitfall 3: Code Logic Answers Without Source Evidence

**What goes wrong:**
The agent answers "how this works" from general knowledge instead of the repository's actual code.

**Why it happens:**
Large context and old training data can make the model sound plausible.

**How to avoid:**
Require CodeGraph or source-search evidence before code-logic answers; include source paths/snippets in preview records.

**Warning signs:**
Answer draft has no source files, symbols, or line references.

**Phase to address:**
Phase 2.

---

### Pitfall 4: Closing Old But Still Useful Issues

**What goes wrong:**
Roadmap, help wanted, feature request, or contribution issues are closed because they are old.

**Why it happens:**
Age-based stale automation ignores issue purpose and active contribution value.

**How to avoid:**
Use explicit closure reasons only: resolved, duplicate, superseded, unsupported, or waiting on requested information. Require evidence references.

**Warning signs:**
Closure reason says "stale" or "old" without a maintainer answer, merged fix, duplicate link, or requested-info trail.

**Phase to address:**
Phase 3.

---

### Pitfall 5: Losing Maintainer Trust Through Noisy Replies

**What goes wrong:**
The agent posts generic, apologetic, or unsupported replies that increase noise.

**Why it happens:**
Reply-worthiness is not separated from answer generation.

**How to avoid:**
Add a reply-worthiness gate and skip when no public, evidence-based answer helps.

**Warning signs:**
High reply count with low evidence count, or many comments that only say "thanks" and ask vague follow-up.

**Phase to address:**
Phase 2.

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-code one repository's labels | Faster prototype | Cannot generalize to new repos. | Only in fixture tests. |
| Store full reply text in records JSON | Easy single-file debugging | Bloats state and makes summaries unsafe. | Avoid; store body files separately. |
| Shell string parsing of JSON | Quick script | Breaks on escaping and schema changes. | Avoid in application code. |
| Global prompt with all policies | One prompt to maintain | Simple models miss constraints. | Split prompts by task with schema validation. |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub labels | Applying labels that do not exist or wrong casing. | Fetch labels first and map only exact existing names. |
| GitHub comments | Posting in preview mode. | All comment/close/edit commands live only in apply engine. |
| GitHub rate limits | Treating search/GraphQL/REST limits as identical. | Query rate-limit status and back off per resource. |
| MiniMax tool use | Not preserving complete assistant responses in multi-turn tool calls. | Keep tool orchestration simple for MVP or follow provider tool-call guidance exactly. |
| CodeGraph | Assuming every repo has an index. | Detect `.codegraph/` and record fallback mode. |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Fetching every comment for every issue every run | Slow runs and rate-limit pressure. | Batch, cache records, skip processed issues unless forced. | Large backlogs. |
| Sending full source files to the model | High cost and weak answers. | Use CodeGraph-targeted snippets and compact evidence packets. | Medium-size repos. |
| Reprocessing closed records indefinitely | State grows and previews become noisy. | Bounded per-issue records and explicit reprocess flags. | Repeated runs. |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Logging tokens or provider keys | Credential leak in repo or preview. | Redact env and config secrets; never write keys to state. |
| Running issue-provided commands | Command injection or destructive actions. | Use allowlisted commands only; default no reproduction. |
| Publishing local paths or internal config | Privacy leak. | Convert evidence to repo-relative paths and public URLs. |
| Excessive token permissions | Accidental broad mutation. | Prefer existing `gh` auth for local MVP; future GitHub App with scoped permissions. |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Huge raw JSON previews | Maintainers cannot review quickly. | Markdown summary plus linked JSON record. |
| Hidden downgrades | User cannot tell why a model proposal was rejected. | Record model proposal and policy result separately. |
| Ambiguous "skipped" status | User cannot distinguish safe skip from failure. | Use explicit statuses: `needs_info`, `needs_repro`, `human_review`, `policy_rejected`. |

## "Looks Done But Isn't" Checklist

- [ ] **Classifier:** Has schema validation and invalid-output recovery.
- [ ] **Preview mode:** No GitHub mutation path can run without explicit apply.
- [ ] **Code answer:** Includes source evidence from CodeGraph or fallback search.
- [ ] **Closure:** Requires specific evidence references, not just age.
- [ ] **State:** Re-running replaces records instead of appending unbounded history.
- [ ] **Provider config:** Supports proxy/base URL and does not log secrets.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Bad label application | MEDIUM | Revert labels from state, add regression test, strengthen policy. |
| Bad public comment | HIGH | Post correction if needed, disable apply mode, add evidence gate. |
| Unsafe closure | HIGH | Reopen issue, explain mistake, add closure-policy regression fixture. |
| Invalid model outputs | LOW | Add retry/repair prompt and schema-specific tests. |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Public mutation from unvalidated model output | Phase 1 | Tests prove preview mode never calls `gh issue edit/comment/close`. |
| Answering reproduction issues without environment | Phase 2 | Fixture issue routes to no-answer with reason. |
| Code logic answers without source evidence | Phase 2 | Answer workflow fails closed when no source evidence exists. |
| Closing old but useful issues | Phase 3 | Closure fixtures for roadmap/help-wanted/open-PR cases stay open. |
| Losing maintainer trust through noisy replies | Phase 2 | Reply-worthiness gate skips low-evidence issues. |

## Sources

- GitHub CLI issue close manual: https://cli.github.com/manual/gh_issue_close
- GitHub CLI issue comment manual: https://cli.github.com/manual/gh_issue_comment
- GitHub REST Issues docs: https://docs.github.com/rest/issues
- GitHub REST Rate Limits docs: https://docs.github.com/rest/rate-limit/rate-limit
- MiniMax tool-use guide: https://platform.minimax.io/docs/guides/text-m3-function-call
- MiniMax OpenAI-compatible API docs: https://platform.minimax.io/docs/api-reference/text-openai-api
- Pydantic JSON Schema docs: https://pydantic.dev/docs/validation/latest/concepts/json_schema/
- Local reference state: `.issue-agent/state/verl-project__verl/close/latest-preview.md`

---
*Pitfalls research for: GitHub issue automation with code-aware LLM triage*
*Researched: 2026-06-15*

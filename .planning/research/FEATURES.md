# Feature Research

**Domain:** GitHub issue automation with code-aware LLM triage
**Researched:** 2026-06-15
**Confidence:** MEDIUM-HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Repository profile config | Maintainers need per-repo labels, policies, provider settings, and state paths. | MEDIUM | YAML profile with defaults and repo overrides. |
| Issue intake | Tool must fetch issue title, body, labels, author, comments, linked PRs, and timestamps. | MEDIUM | Use `gh issue list/view` first; REST fallback for comments/labels. |
| Existing-label awareness | Label mutation must respect existing repo labels. | LOW | Fetch labels before classification; never invent labels by default. |
| Structured classifier | Core product is a model-backed issue classifier. | MEDIUM | Output category, confidence, evidence needs, next action, and no-action reason. |
| Evidence model | Every answer or closure recommendation needs evidence references. | MEDIUM | Evidence can be issue comments, PRs, docs, source files, CodeGraph snippets. |
| CodeGraph-first code reading | User explicitly wants CodeGraph to accelerate source understanding. | MEDIUM | Detect `.codegraph/`; otherwise fall back to shell search. |
| Preview-first output | Maintainers need to review proposed labels/comments/closures before mutation. | LOW | Generate Markdown preview and JSON records. |
| Explicit apply mode | Public GitHub changes must require intentional action. | LOW | `--apply` or config `write_policy=apply`; default preview. |
| Bounded state | Runs should be resumable without unbounded logs. | MEDIUM | Replace record per issue; keep latest batch previews. |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| No-answer gate for unverified experiments | Prevents speculative public answers when environment reproduction is impossible. | MEDIUM | Classifier should route to `needs_repro_environment` or `request_info`. |
| Code logic answer mode | Reads code and explains behavior for usage or logic questions. | HIGH | Needs source retrieval, citation formatting, and confidence gating. |
| Stale PR/issue closure policy | Helps maintainers shrink backlog without unfairly closing live work. | HIGH | Requires PR state, maintainer comments, activity recency, and supersession evidence. |
| Small-model prompt profiles | Makes MiniMax/budget models usable through compact schemas and deterministic postchecks. | MEDIUM | Avoid large unconstrained prompts. |
| China/proxy-aware provider config | Fits the user's operating environment. | LOW | Support `HTTPS_PROXY`, `ALL_PROXY`, and per-provider base URLs. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Fully automatic closure | Saves time quickly. | High trust risk; stale does not mean safe to close. | Closure preview plus evidence threshold and explicit apply. |
| Answer every issue | Looks helpful. | Reproduction and roadmap questions often require unverified claims. | Route to no-answer, request info, or human review. |
| Let model run arbitrary commands | Feels agentic. | Security and reproducibility risk. | Deterministic command allowlist owned by code. |
| One global label taxonomy | Simple setup. | Different repos use different labels and casing. | Per-repo label map from fetched labels. |

## Feature Dependencies

```text
Repository profile
    -> Issue intake
        -> Evidence model
            -> Structured classifier
                -> Preview output
                    -> Explicit apply mode

CodeGraph detection
    -> Source retrieval
        -> Code logic answer mode

Linked PR/comment inspection
    -> Stale cleanup policy
        -> Closure preview
```

### Dependency Notes

- **Structured classifier requires issue intake and evidence model:** the model cannot make bounded decisions from title text alone.
- **Code logic answers require source retrieval:** answering without code violates the project core value.
- **Apply mode requires preview artifacts:** the user needs inspectable evidence and deterministic state before mutation.

## MVP Definition

### Launch With (v1)

- [ ] Repository profile config — needed before any repo-specific policy can work.
- [ ] Issue intake through `gh` — needed for real GitHub data.
- [ ] Existing-label fetch and classification preview — validates the simple-model classifier.
- [ ] CodeGraph detection and source evidence capture — validates the code-aware core.
- [ ] No-answer gate for experiment/reproduction issues — enforces the user's key safety rule.
- [ ] Bounded JSON/Markdown state — supports review and reruns.

### Add After Validation (v1.x)

- [ ] Draft code-logic answers with source citations — add after classifier and source retrieval are stable.
- [ ] Stale PR/issue closure preview — add once evidence model handles linked PRs and comments.
- [ ] Apply mode for labels/comments/closures — add after preview format is trusted.

### Future Consideration (v2+)

- [ ] GitHub App auth — useful for teams and better permission boundaries.
- [ ] Web dashboard — useful after CLI workflow proves valuable.
- [ ] Multi-repo batch scheduling — useful after per-repo profiles are mature.
- [ ] Provider router across MiniMax/OpenAI/local models — useful when cost and latency data exist.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Repository profile config | HIGH | MEDIUM | P1 |
| Issue intake | HIGH | MEDIUM | P1 |
| Existing-label-aware classifier preview | HIGH | MEDIUM | P1 |
| CodeGraph detection/source capture | HIGH | MEDIUM | P1 |
| No-answer gate | HIGH | LOW | P1 |
| Bounded state | HIGH | MEDIUM | P1 |
| Code-logic answer draft | HIGH | HIGH | P2 |
| Stale closure preview | HIGH | HIGH | P2 |
| Apply mode | MEDIUM | MEDIUM | P2 |
| Dashboard | LOW | HIGH | P3 |

## Competitor Feature Analysis

| Feature | Common Automation Scripts | GitHub Native Tools | Our Approach |
|---------|---------------------------|---------------------|--------------|
| Labeling | Keyword or regex labelers | Labels and issue forms | LLM classifier constrained by repo label set and evidence. |
| Stale closure | Age-based stale bots | Manual close reason | Evidence-based stale policy, not age-only closure. |
| Code-aware answers | Usually absent | Maintainer manual work | CodeGraph-first source retrieval before answer drafting. |
| Safety | Often direct mutation | Permission checks | Preview-first, bounded state, explicit apply. |

## Sources

- GitHub CLI issue manual: https://cli.github.com/manual/gh_issue
- GitHub REST Issues docs: https://docs.github.com/rest/issues
- GitHub REST Issue Comments docs: https://docs.github.com/rest/issues/comments
- GitHub REST Labels docs: https://docs.github.com/en/rest/issues/labels
- MiniMax OpenAI-compatible API docs: https://platform.minimax.io/docs/api-reference/text-chat-openai
- MiniMax Tool Use guide: https://platform.minimax.io/docs/guides/text-m3-function-call
- Pydantic JSON Schema docs: https://pydantic.dev/docs/validation/latest/concepts/json_schema/

---
*Feature research for: GitHub issue automation with code-aware LLM triage*
*Researched: 2026-06-15*

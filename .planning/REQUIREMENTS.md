# Requirements: Issue Agent

**Defined:** 2026-06-15
**Core Value:** Every public issue action must be grounded in visible repository evidence, and the default action under uncertainty is no public mutation.

## v1 Requirements

Requirements for the initial release. Each maps to roadmap phases.

### Configuration

- [x] **CONF-01**: User can define a repository profile with repo name, state path, label policy, model provider, and write policy.
- [x] **CONF-02**: User can configure MiniMax or another OpenAI-compatible model endpoint without storing secrets in tracked files.
- [x] **CONF-03**: User can configure proxy-related environment behavior for GitHub and model-provider access.

### GitHub Intake

- [x] **GH-01**: User can fetch open GitHub issues in deterministic batches with title, body, labels, author, URL, timestamps, and comments.
- [x] **GH-02**: User can fetch the repository's existing label set and prevent proposals for labels that do not exist.
- [x] **GH-03**: User can inspect linked issue and PR references needed for stale cleanup decisions.

### Classification

- [x] **CLSF-01**: User can run an LLM-backed classifier that returns a structured decision schema for each issue.
- [x] **CLSF-02**: Classifier decisions include category, confidence, proposed action, evidence requirements, no-action reason, and proposed labels.
- [x] **CLSF-03**: Classifier supports at least these categories: experiment/reproduction, code logic question, usage question, stale cleanup candidate, feature/enhancement, bug report, and unknown/unsafe.
- [x] **CLSF-04**: Invalid model output is rejected or repaired once; unresolved invalid output becomes human review instead of public action.

### Code Evidence

- [x] **CODE-01**: When the target repository contains `.codegraph/`, the agent uses CodeGraph before grep/find to locate relevant code.
- [x] **CODE-02**: When CodeGraph is unavailable, the agent records fallback mode and uses source search or file reads to gather evidence.
- [x] **CODE-03**: Code logic answers require source evidence before a draft answer can be generated.
- [x] **CODE-04**: Source evidence records include repository-relative paths, symbols or snippets, and the reason each item is relevant.

### Safety Policy

- [x] **SAFE-01**: Experiment, hardware, dependency, or environment reproduction issues are not answered unless verified run evidence exists.
- [x] **SAFE-02**: Under uncertainty, the agent emits no public mutation and records why the issue needs human review or more information.
- [x] **SAFE-03**: Public comments, labels, and closures are impossible in preview mode.
- [x] **SAFE-04**: Closure recommendations require explicit evidence for resolved, duplicate, superseded, unsupported, or waiting-for-information status.
- [x] **SAFE-05**: The agent never creates new GitHub labels unless the user explicitly enables label creation.

### Answer Drafting

- [x] **ANS-01**: User can generate preview-only draft replies for code logic or usage questions when evidence supports an answer.
- [x] **ANS-02**: Draft replies cite source files, docs, issue comments, or PR references used as evidence.
- [x] **ANS-03**: Reply-worthiness is assessed separately from reply generation, so low-evidence issues are skipped.

### Stale Cleanup

- [x] **CLOSE-01**: User can preview stale issue or PR cleanup recommendations with current state, closure reason, evidence references, and risk level.
- [x] **CLOSE-02**: Roadmap, help-wanted, open contribution, and open-PR issues are not recommended for closure unless clear supersession or completion evidence exists.
- [ ] **CLOSE-03**: User can apply approved closure actions only in explicit apply mode.

### State and Review

- [x] **STATE-01**: Each workflow writes bounded `records.json`, `pending-batch.json`, and `latest-preview.md` artifacts.
- [x] **STATE-02**: Reprocessing an issue replaces that issue's canonical record instead of appending unbounded history.
- [x] **STATE-03**: Preview files show model proposal, policy result, evidence references, and whether any GitHub mutation was applied.
- [ ] **STATE-04**: User can generate an aggregate summary report from classification, answer, and closure records.

### Apply Mode

- [ ] **APPLY-01**: User can apply approved label changes through GitHub only after preview artifacts exist.
- [ ] **APPLY-02**: User can post approved comments through GitHub only after preview artifacts exist.
- [ ] **APPLY-03**: User can close approved issues through GitHub only after preview artifacts exist.
- [ ] **APPLY-04**: Apply failures preserve preview records and mark the affected issue as failed without retry loops.

## User Stories

- As a maintainer, I can preview classifications for a batch of GitHub issues before changing labels.
- As a maintainer, I can see why an issue is not answered when it requires an environment the agent cannot reproduce.
- As a maintainer, I can get a code-backed answer draft for a code logic question with source evidence attached.
- As a maintainer, I can review stale cleanup recommendations that explain why closure is safe or unsafe.
- As a maintainer, I can explicitly apply only the actions I trust.

## Acceptance Criteria

- Preview mode can run end-to-end without calling `gh issue edit`, `gh issue comment`, or `gh issue close`.
- A reproduction-only fixture issue routes to no-answer or request-info unless run evidence is present.
- A code-logic fixture issue cannot produce an answer when no source evidence exists.
- A roadmap/help-wanted/open-PR fixture issue is not recommended for closure solely because it is old.
- Invalid model JSON cannot reach apply mode.
- Bounded state files can be regenerated deterministically for a fixed fixture batch.

## Definition of Done

- Unit tests cover schema validation, policy downgrades, bounded state replacement, and preview/apply separation.
- At least one fixture batch demonstrates classify, answer-preview, close-preview, and summary flows.
- Documentation explains configuration, proxy setup, preview mode, apply mode, and CodeGraph fallback behavior.
- No secrets are written to tracked config, preview, or state files.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Authentication and Hosting

- **AUTH-01**: User can configure a GitHub App with scoped permissions instead of relying on local `gh` auth.
- **AUTH-02**: Team users can share server-side state without committing local process files.

### Operations

- **OPS-01**: User can schedule recurring multi-repo runs.
- **OPS-02**: User can view run history and decisions in a web dashboard.
- **OPS-03**: User can compare provider cost, latency, and invalid-output rates across model providers.

### Provider Routing

- **PROV-01**: User can route tasks across MiniMax, OpenAI-compatible, and local models based on policy.
- **PROV-02**: User can maintain per-task prompt profiles and evaluate them against fixture sets.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Fully automated experimental reproduction | The project must not claim unverified runtime behavior when no environment exists. |
| Public mutation without preview | Maintainer trust depends on reviewable evidence and explicit apply. |
| Automatic label creation | Repository label taxonomy belongs to maintainers. |
| Browser scraping GitHub | GitHub CLI/API workflows are more auditable and stable. |
| Replacing maintainer decisions on roadmap or policy | The agent should recommend with evidence, not decide project direction. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CONF-01 | Phase 1 | Complete |
| CONF-02 | Phase 1 | Complete |
| CONF-03 | Phase 1 | Complete |
| GH-01 | Phase 1 | Complete |
| GH-02 | Phase 1 | Complete |
| GH-03 | Phase 3 | Complete |
| CLSF-01 | Phase 1 | Complete |
| CLSF-02 | Phase 1 | Complete |
| CLSF-03 | Phase 1 | Complete |
| CLSF-04 | Phase 1 | Complete |
| CODE-01 | Phase 2 | Complete |
| CODE-02 | Phase 2 | Complete |
| CODE-03 | Phase 2 | Complete |
| CODE-04 | Phase 2 | Complete |
| SAFE-01 | Phase 2 | Complete |
| SAFE-02 | Phase 2 | Complete |
| SAFE-03 | Phase 1 | Complete |
| SAFE-04 | Phase 3 | Complete |
| SAFE-05 | Phase 1 | Complete |
| ANS-01 | Phase 2 | Complete |
| ANS-02 | Phase 2 | Complete |
| ANS-03 | Phase 2 | Complete |
| CLOSE-01 | Phase 3 | Complete |
| CLOSE-02 | Phase 3 | Complete |
| CLOSE-03 | Phase 3 | Pending |
| STATE-01 | Phase 1 | Complete |
| STATE-02 | Phase 1 | Complete |
| STATE-03 | Phase 1 | Complete |
| STATE-04 | Phase 4 | Pending |
| APPLY-01 | Phase 3 | Pending |
| APPLY-02 | Phase 3 | Pending |
| APPLY-03 | Phase 3 | Pending |
| APPLY-04 | Phase 3 | Pending |

**Coverage:**

- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-06-15*
*Last updated: 2026-06-15 after roadmap creation*

# Roadmap: Issue Agent

## Overview

Issue Agent starts with a safe preview pipeline, then adds code-aware issue understanding, then enables stale cleanup and explicit GitHub mutations, and finally hardens the tool for repeatable maintainer use. The roadmap is intentionally ordered so that schema validation, evidence capture, bounded state, and preview-only behavior exist before any public comments, labels, or closures can be applied.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Core Preview Pipeline** - Config, GitHub intake, schemas, classifier preview, and bounded state. (completed 2026-06-15)
- [x] **Phase 2: Code-Aware Triage and Answers** - CodeGraph-first evidence, no-answer gates, and answer previews. (completed 2026-06-15)
- [ ] **Phase 3: Stale Cleanup and Controlled Apply** - Evidence-based stale cleanup plus explicit GitHub apply mode.
- [ ] **Phase 4: Summary, Tests, and Operator Docs** - Aggregate reporting, fixture coverage, proxy docs, and workflow hardening.

## Phase Details

### Phase 1: Core Preview Pipeline

**Goal**: User can configure a repository, fetch an issue batch, run a schema-validated classifier, and inspect bounded preview artifacts without any GitHub mutation.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: [CONF-01, CONF-02, CONF-03, GH-01, GH-02, CLSF-01, CLSF-02, CLSF-03, CLSF-04, SAFE-03, SAFE-05, STATE-01, STATE-02, STATE-03]
**Success Criteria** (what must be TRUE):

  1. User can run a preview classification command against fixture issue data and get structured decisions.
  2. User can fetch the repository label set and the classifier never proposes absent labels as applyable.
  3. Invalid model output is rejected or downgraded to human review before preview records are written.
  4. Preview mode writes `records.json`, `pending-batch.json`, and `latest-preview.md` without calling GitHub mutation commands.

**Plans**: 3 plans
Plans:
**Wave 1**

- [x] 01-01: CLI, config, provider settings, and proxy-safe secret handling

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02: GitHub issue and label intake with fixture-backed tests

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03: Classifier schema, policy validation, preview state, and bounded record writes

### Phase 2: Code-Aware Triage and Answers

**Goal**: User can distinguish reproduction issues from code logic questions, refuse unsupported experiments, and generate source-backed answer previews.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: [CODE-01, CODE-02, CODE-03, CODE-04, SAFE-01, SAFE-02, ANS-01, ANS-02, ANS-03]
**Success Criteria** (what must be TRUE):

  1. When `.codegraph/` exists, code-question workflows use CodeGraph before grep/find.
  2. When CodeGraph is unavailable, fallback mode is recorded in the preview evidence.
  3. Reproduction-only issues route to no-answer or request-info unless run evidence is present.
  4. Code logic answer drafts include source evidence and are skipped when evidence is missing.

**Plans**: 3 plans
Plans:
**Wave 1**

- [x] 02-01: CodeGraph detection, source lookup adapter, and fallback evidence mode

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 02-02: No-answer gates for experiment, hardware, dependency, and environment issues

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 02-03: Source-backed answer draft previews and reply-worthiness policy

### Phase 3: Stale Cleanup and Controlled Apply

**Goal**: User can preview stale cleanup recommendations with evidence and explicitly apply approved label, comment, or closure actions.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: [GH-03, SAFE-04, CLOSE-01, CLOSE-02, CLOSE-03, APPLY-01, APPLY-02, APPLY-03, APPLY-04]
**Success Criteria** (what must be TRUE):

  1. Stale cleanup previews include current state, closure reason, risk level, and evidence references.
  2. Roadmap, help-wanted, active contribution, and open-PR issues are not recommended for closure only because they are old.
  3. Label/comment/close commands run only in explicit apply mode and only after matching preview records exist.
  4. Apply failures preserve preview data and mark the affected issue failed without retry loops.

**Plans**: 3 plans
Plans:
**Wave 1**

- [ ] 03-01: Linked issue and PR evidence extraction for stale cleanup

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 03-02: Closure policy and stale recommendation previews

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 03-03: Explicit apply engine for labels, comments, closures, and failure recording

### Phase 4: Summary, Tests, and Operator Docs

**Goal**: User can trust the workflow through aggregate reports, regression fixtures, documentation, and repeatable commands.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: [STATE-04]
**Success Criteria** (what must be TRUE):

  1. User can generate an aggregate summary from classification, answer, and closure records.
  2. Fixture tests cover schema validation, policy downgrades, preview/apply separation, and bounded state replacement.
  3. Documentation explains config, proxy setup, preview mode, apply mode, CodeGraph fallback, and remote-server network considerations.
  4. No tracked config, preview, state, or docs file contains provider secrets or local-only sensitive details.

**Plans**: 3 plans

Plans:

- [ ] 04-01: Aggregate summary report and tracking-output preview
- [ ] 04-02: Regression fixture suite and safety verification
- [ ] 04-03: Operator documentation, proxy guidance, and release readiness cleanup

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Preview Pipeline | 3/3 | Complete    | 2026-06-15 |
| 2. Code-Aware Triage and Answers | 3/3 | Complete   | 2026-06-15 |
| 3. Stale Cleanup and Controlled Apply | 0/3 | Planned    |  |
| 4. Summary, Tests, and Operator Docs | 0/3 | Not started | - |

# Issue Agent Operator Guide

This guide explains the v1 local workflow for maintainers. Issue Agent is preview-first: it writes local artifacts for review before any public GitHub mutation is possible.

## Configuration

Use `examples/config.yaml` as the tracked non-secret profile shape. Keep provider keys, GitHub tokens, proxy values that differ by machine, and local-only server details in environment variables or ignored files.

Common environment variables:

```bash
export MINIMAX_API_KEY=
export MINIMAX_BASE_URL=
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export ALL_PROXY=socks5://127.0.0.1:7890
```

The `127.0.0.1:7890` proxy convention matches the local macOS development environment. On a remote server, forward network access explicitly when needed, for example by exposing a local proxy to the remote shell over SSH. Do not commit the remote host name, login details, private config paths, or credential values.

## Fixture Quickstart

Install in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Run classification preview:

```bash
python -m issue_agent.cli preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --state-root /tmp/issue-agent-preview
```

Run answer preview:

```bash
python -m issue_agent.cli answer-preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --repo-root tests/fixtures/source_repo \
  --state-root /tmp/issue-agent-preview
```

Run close preview:

```bash
python -m issue_agent.cli close-preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --repo Kirrito-k423/issue-agent \
  --state-root /tmp/issue-agent-preview
```

Run aggregate summary preview:

```bash
python -m issue_agent.cli summary-preview \
  --config examples/config.yaml \
  --state-root /tmp/issue-agent-preview
```

## Preview And Apply Safety

Preview commands are local-only:

- `preview` classifies fixture issues and writes `classify/`.
- `answer-preview` writes answer decisions and local drafts under `answer/`.
- `close-preview` writes closure recommendations under `close/`.
- `summary-preview` reads local state and writes `summary/`.

These commands do not edit labels, post comments, or close issues.

`apply-close` is intentionally different. It can run `gh issue` label, comment, and close commands, but only after a matching close preview record exists under the selected state root:

```bash
python -m issue_agent.cli apply-close \
  --config examples/config.yaml \
  --repo Kirrito-k423/issue-agent \
  --state-root /tmp/issue-agent-preview \
  --issue-number 6 \
  --action close
```

Use apply mode only after reviewing `close/latest-preview.md` and `close/records.json`.

## CodeGraph Fallback

For code questions, Issue Agent follows the project rule from `AGENTS.md`: when the target repository contains `.codegraph/`, use CodeGraph before grep, `rg`, or manual file reads.

When CodeGraph is not available, answer preview may use fallback source search. The fallback mode is recorded in evidence fields so maintainers can tell whether an answer was CodeGraph-backed or only search-backed.

## When Not To Answer Or Close

Do not answer an issue when:

- it asks for experiment, hardware, dependency, or environment reproduction and there is no verified run evidence;
- there is insufficient source evidence for a code logic answer;
- the question depends on external state the agent cannot verify.

Do not recommend closure when:

- linked issue or pull request state is unresolved;
- the issue is roadmap, help-wanted, good-first-issue, feature, or active contribution work without explicit completion or supersession evidence;
- the only signal is age;
- closure evidence is unsafe, ambiguous, or missing.

Under uncertainty, the correct output is local preview state that asks for human review or more information.

## State Layout

Generated state is local and ignored by git under `.issue-agent/state/`. When a command receives `--state-root`, it writes under that path instead.

Workflow directories:

- `classify/records.json`, `pending-batch.json`, `latest-preview.md`
- `answer/records.json`, `pending-batch.json`, `latest-preview.md`, `drafts/`
- `close/records.json`, `pending-batch.json`, `latest-preview.md`
- `apply/records.json`, `latest-preview.md`
- `summary/records.json`, `latest-preview.md`

Reprocessing replaces canonical records instead of appending unbounded history.

## Release Verification

Run the full local suite:

```bash
.venv/bin/python -m pytest
```

Useful targeted checks:

```bash
.venv/bin/python -m pytest tests/test_regression_workflows.py tests/test_safety_regression.py
.venv/bin/python -m pytest tests/test_operator_docs.py tests/test_summary_preview.py
```

Before shipping, confirm:

- preview commands still print no-mutation safety text;
- `summary-preview` works with partial and complete local state;
- `apply-close` is the only operator command that can request GitHub mutations;
- safety scans pass with no tracked generated state or obvious secrets.

## Out Of Scope For v1

These remain future work and are not part of Phase 4:

- dashboards or hosted HTML reports;
- recurring automation or scheduled jobs;
- GitHub App authentication;
- multi-repo scheduling;
- provider quality or cost dashboards.

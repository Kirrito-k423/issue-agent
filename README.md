# Issue Agent

Issue Agent is a preview-first GitHub issue triage assistant. It is built for maintainers who want simple-model help with issue classification while keeping every public GitHub mutation behind deterministic policy and explicit apply steps.

For the full local workflow, proxy notes, CodeGraph behavior, and release checks, see [docs/OPERATOR_GUIDE.md](docs/OPERATOR_GUIDE.md).

## Quickstart

```bash
python -m pip install -e ".[dev]"
python -m issue_agent.cli preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --state-root /tmp/issue-agent-preview

python -m issue_agent.cli answer-preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --repo-root tests/fixtures/source_repo \
  --state-root /tmp/issue-agent-answer-preview

python -m issue_agent.cli close-preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --repo Kirrito-k423/issue-agent \
  --state-root /tmp/issue-agent-close-preview

python -m issue_agent.cli summary-preview \
  --config examples/config.yaml \
  --state-root /tmp/issue-agent-close-preview

python -m issue_agent.cli apply-close \
  --config examples/config.yaml \
  --repo Kirrito-k423/issue-agent \
  --state-root /tmp/issue-agent-close-preview \
  --issue-number 6 \
  --action close
```

The preview commands write local artifacts only. They do not edit, comment on, close, or label GitHub issues.
`apply-close` is different: it can run `gh issue` label, comment, and close commands, but only after a matching close preview record exists under the selected state root.

## Configuration

Tracked config files must contain non-secret settings only. Keep provider keys, GitHub tokens, and proxy values in the environment:

```bash
export MINIMAX_API_KEY=
export MINIMAX_BASE_URL=
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export ALL_PROXY=socks5://127.0.0.1:7890
```

Use the proxy variables when local GitHub or model-provider access needs the China-based Mac proxy convention.

## Safety Model

- Preview mode is the default and only Phase 1 behavior.
- Model output is treated as proposal data, not an action source.
- State is bounded under `.issue-agent/state/<owner>__<repo>/`.
- Missing GitHub labels are rejected rather than created.
- Answer drafts require supporting evidence and are written locally under `answer/drafts/`.
- Close previews require explicit evidence and are written locally under `close/`.
- Apply mode requires reviewed close preview records and never creates missing labels automatically.

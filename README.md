# Issue Agent

Issue Agent is a preview-first GitHub issue triage assistant. It is built for maintainers who want simple-model help with issue classification while keeping every public GitHub mutation behind deterministic policy and explicit apply steps.

## Quickstart

```bash
python -m pip install -e ".[dev]"
python -m issue_agent.cli preview \
  --config examples/config.yaml \
  --issues-file examples/issues.fixture.json \
  --state-root /tmp/issue-agent-preview
```

The preview command writes local artifacts only. It does not edit, comment on, close, or label GitHub issues.

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

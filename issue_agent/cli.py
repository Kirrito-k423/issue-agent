from pathlib import Path

import typer

from issue_agent.answer import build_answer_preview_records
from issue_agent.apply import ApplyValidationError, apply_close_actions
from issue_agent.classifier import ClassifierProvider, FixtureClassifierProvider
from issue_agent.closure import build_close_preview_records
from issue_agent.config import load_config
from issue_agent.github import load_fixture_issues, load_fixture_labels
from issue_agent.models import ApplyAction, PreviewRecord
from issue_agent.policy import apply_policy
from issue_agent.state import write_answer_preview, write_apply_results, write_batch_preview, write_close_preview


app = typer.Typer(help="Preview-first GitHub issue triage assistant.")


@app.callback()
def main() -> None:
    """Preview-first GitHub issue triage assistant."""


@app.command()
def preview(
    config: Path = typer.Option(..., "--config", exists=True, readable=True, help="Repository profile YAML."),
    issues_file: Path = typer.Option(..., "--issues-file", exists=True, readable=True, help="Fixture issue JSON."),
    state_root: Path | None = typer.Option(None, "--state-root", help="Override preview state root."),
) -> None:
    """Run a local preview classification pass."""
    app_config = load_config(config)
    target_state = state_root or app_config.state_root
    issues = load_fixture_issues(issues_file)
    labels = load_fixture_labels(app_config.label_policy.allowed_labels)
    available_label_set = {label.name for label in labels}
    provider: ClassifierProvider = FixtureClassifierProvider()
    records = [
        PreviewRecord(
            issue_number=issue.number,
            title=issue.title,
            model_proposal=(proposal := provider.classify(issue)),
            policy_decision=apply_policy(proposal, available_label_set),
            evidence_refs=[],
            github_mutation_applied=False,
        )
        for issue in issues[: app_config.batch_size]
    ]
    paths = write_batch_preview(target_state, "classify", records)
    typer.echo("Mode: preview; no GitHub issues were changed.")
    typer.echo(f"Latest preview: {paths['latest_preview']}")


@app.command("answer-preview")
def answer_preview(
    config: Path = typer.Option(..., "--config", exists=True, readable=True, help="Repository profile YAML."),
    issues_file: Path = typer.Option(..., "--issues-file", exists=True, readable=True, help="Fixture issue JSON."),
    repo_root: Path = typer.Option(..., "--repo-root", exists=True, file_okay=False, help="Target repository root."),
    state_root: Path | None = typer.Option(None, "--state-root", help="Override preview state root."),
) -> None:
    """Run a local preview pass for evidence-backed answer drafts."""
    app_config = load_config(config)
    target_state = state_root or app_config.state_root
    issues = load_fixture_issues(issues_file)
    provider: ClassifierProvider = FixtureClassifierProvider()
    records = build_answer_preview_records(issues[: app_config.batch_size], repo_root, provider)
    paths = write_answer_preview(target_state, records)
    typer.echo("Mode: preview; no GitHub comments were posted.")
    typer.echo(f"Latest preview: {paths['latest_preview']}")


@app.command("close-preview")
def close_preview(
    config: Path = typer.Option(..., "--config", exists=True, readable=True, help="Repository profile YAML."),
    issues_file: Path = typer.Option(..., "--issues-file", exists=True, readable=True, help="Fixture issue JSON."),
    repo: str = typer.Option(..., "--repo", help="Repository in OWNER/REPO format."),
    state_root: Path | None = typer.Option(None, "--state-root", help="Override preview state root."),
) -> None:
    """Run a local preview pass for evidence-backed closure recommendations."""
    app_config = load_config(config)
    target_state = state_root or app_config.state_root
    issues = load_fixture_issues(issues_file)
    records = build_close_preview_records(issues[: app_config.batch_size], repo)
    paths = write_close_preview(target_state, records)
    typer.echo("Mode: preview; no GitHub issues were closed.")
    typer.echo(f"Latest preview: {paths['latest_preview']}")


@app.command("apply-close")
def apply_close(
    config: Path = typer.Option(..., "--config", exists=True, readable=True, help="Repository profile YAML."),
    repo: str = typer.Option(..., "--repo", help="Repository in OWNER/REPO format."),
    state_root: Path = typer.Option(..., "--state-root", exists=True, file_okay=False, help="Existing state root."),
    issue_number: int = typer.Option(..., "--issue-number", min=1, help="Issue number with a reviewed close preview."),
    action: str = typer.Option(..., "--action", help="One of: add-label, remove-label, comment, close."),
    label: str | None = typer.Option(None, "--label", help="Label for add-label or remove-label."),
    reason: str | None = typer.Option(None, "--reason", help="Optional close reason: completed or not planned."),
) -> None:
    """Apply one reviewed close-preview action through GitHub CLI."""
    load_config(config)
    apply_action = _build_apply_action(issue_number, action, label, reason)
    try:
        results = apply_close_actions(state_root, repo, [apply_action])
    except ApplyValidationError as exc:
        raise typer.BadParameter(str(exc)) from exc

    paths = write_apply_results(state_root, results)
    typer.echo("Mode: apply; GitHub issue mutations were requested explicitly.")
    typer.echo(f"Latest apply results: {paths['latest_preview']}")


def _build_apply_action(issue_number: int, action: str, label: str | None, reason: str | None) -> ApplyAction:
    action_map = {
        "add-label": "add_label",
        "remove-label": "remove_label",
        "comment": "comment",
        "close": "close",
    }
    action_type = action_map.get(action)
    if action_type is None:
        raise typer.BadParameter("action must be one of: add-label, remove-label, comment, close")
    if action_type in {"add_label", "remove_label"} and not label:
        raise typer.BadParameter("--label is required for label actions")
    if action_type not in {"add_label", "remove_label"} and label:
        raise typer.BadParameter("--label is only valid for label actions")
    if reason is not None and reason not in {"completed", "not planned"}:
        raise typer.BadParameter("--reason must be 'completed' or 'not planned'")
    if action_type != "close" and reason is not None:
        raise typer.BadParameter("--reason is only valid for close actions")

    return ApplyAction(
        issue_number=issue_number,
        action_type=action_type,
        value=label if action_type in {"add_label", "remove_label"} else reason,
    )


if __name__ == "__main__":
    app()

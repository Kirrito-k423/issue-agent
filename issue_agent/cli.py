from pathlib import Path

import typer

from issue_agent.answer import build_answer_preview_records
from issue_agent.classifier import ClassifierProvider, FixtureClassifierProvider
from issue_agent.config import load_config
from issue_agent.github import load_fixture_issues, load_fixture_labels
from issue_agent.models import PreviewRecord
from issue_agent.policy import apply_policy
from issue_agent.state import write_answer_preview, write_batch_preview


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


if __name__ == "__main__":
    app()

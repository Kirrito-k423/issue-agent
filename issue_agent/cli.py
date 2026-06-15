import json
from pathlib import Path

import typer

from issue_agent.config import load_config
from issue_agent.state import write_batch_preview


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
    issues = json.loads(issues_file.read_text(encoding="utf-8"))
    records = [
        {
            "issue_number": issue["number"],
            "title": issue["title"],
            "category": "unknown_unsafe",
            "status": "preview_only",
            "model_provider": app_config.provider.name,
            "labels_proposed": list(issue.get("labels", [])),
            "labels_available": list(app_config.label_policy.allowed_labels),
            "labels_rejected": [],
            "no_action_reason": "Phase 1 skeleton records previews only.",
            "github_mutation_applied": False,
        }
        for issue in issues[: app_config.batch_size]
    ]
    paths = write_batch_preview(target_state, "classify", records)
    typer.echo("Mode: preview; no GitHub issues were changed.")
    typer.echo(f"Latest preview: {paths['latest_preview']}")


if __name__ == "__main__":
    app()

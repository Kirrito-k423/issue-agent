from pathlib import Path

import typer
from rich.console import Console


app = typer.Typer(help="Preview-first GitHub issue triage assistant.")
console = Console()


@app.command()
def preview(
    config: Path = typer.Option(..., "--config", exists=True, readable=True, help="Repository profile YAML."),
    issues_file: Path = typer.Option(..., "--issues-file", exists=True, readable=True, help="Fixture issue JSON."),
    state_root: Path | None = typer.Option(None, "--state-root", help="Override preview state root."),
) -> None:
    """Run a local preview classification pass."""
    target_state = state_root or Path(".issue-agent/state")
    console.print(f"Preview requested for {issues_file} using {config}")
    console.print(f"State root: {target_state}")
    console.print("Mode: preview; no GitHub issues were changed.")


if __name__ == "__main__":
    app()

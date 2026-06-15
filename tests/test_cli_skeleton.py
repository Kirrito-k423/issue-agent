import json

from typer.testing import CliRunner

from issue_agent.cli import app


def test_preview_writes_bounded_state_artifacts(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "preview",
            "--config",
            "examples/config.yaml",
            "--issues-file",
            "examples/issues.fixture.json",
            "--state-root",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    workflow_root = tmp_path / "classify"
    records_path = workflow_root / "records.json"
    pending_path = workflow_root / "pending-batch.json"
    preview_path = workflow_root / "latest-preview.md"

    assert records_path.exists()
    assert pending_path.exists()
    assert preview_path.exists()

    records = json.loads(records_path.read_text(encoding="utf-8"))
    assert isinstance(records, dict)
    assert set(records) == {"1", "2", "3", "4"}
    assert records["1"]["github_mutation_applied"] is False
    assert "model_proposal" in records["1"]
    assert "policy_decision" in records["1"]
    assert records["1"]["policy_decision"]["labels_applyable"] == ["question"]

    preview = preview_path.read_text(encoding="utf-8")
    assert "Mode: preview" in preview
    assert "no GitHub issues were changed" in preview
    assert "Applyable" in preview
    assert "Rejected" in preview
    assert str(preview_path) in result.output

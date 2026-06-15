import json
from pathlib import Path

from issue_agent.closure import build_close_preview_records
from issue_agent.github import load_fixture_issues
from issue_agent.state import write_close_preview


FIXTURE_PATH = Path("examples/issues.fixture.json")
REPO = "Kirrito-k423/issue-agent"


def test_close_preview_records_are_conservative() -> None:
    issues = load_fixture_issues(FIXTURE_PATH)

    records = build_close_preview_records(issues, REPO)
    old_help_wanted = next(record for record in records if record.issue_number == 5)
    waiting_for_info = next(record for record in records if record.issue_number == 6)

    assert old_help_wanted.suitable_to_close is False
    assert old_help_wanted.github_mutation_applied is False
    assert waiting_for_info.suitable_to_close is True
    assert waiting_for_info.closure_reason == "stale_waiting_for_info"


def test_write_close_preview_creates_bounded_state(tmp_path) -> None:
    issues = load_fixture_issues(FIXTURE_PATH)
    records = build_close_preview_records(issues, REPO)

    paths = write_close_preview(tmp_path, records)

    assert paths["records"].exists()
    assert paths["pending_batch"].exists()
    assert paths["latest_preview"].exists()

    data = json.loads(paths["records"].read_text(encoding="utf-8"))
    assert "5" in data
    assert "6" in data
    assert all(record["github_mutation_applied"] is False for record in data.values())


def test_reprocessing_close_preview_replaces_records_entry(tmp_path) -> None:
    issues = load_fixture_issues(FIXTURE_PATH)
    record = next(record for record in build_close_preview_records(issues, REPO) if record.issue_number == 6)

    write_close_preview(tmp_path, [record])
    record.current_state = "Replacement state"
    write_close_preview(tmp_path, [record])

    data = json.loads((tmp_path / "close" / "records.json").read_text(encoding="utf-8"))
    assert list(data) == ["6"]
    assert data["6"]["current_state"] == "Replacement state"


def test_close_preview_markdown_mentions_safety(tmp_path) -> None:
    issues = load_fixture_issues(FIXTURE_PATH)
    records = build_close_preview_records(issues, REPO)

    paths = write_close_preview(tmp_path, records)

    preview = paths["latest_preview"].read_text(encoding="utf-8")
    assert "Mode: preview" in preview
    assert "no GitHub issues were closed" in preview

from pathlib import Path


README = Path("README.md")
GUIDE = Path("docs/OPERATOR_GUIDE.md")


def test_readme_links_to_operator_guide() -> None:
    readme = README.read_text(encoding="utf-8")

    assert "docs/OPERATOR_GUIDE.md" in readme


def test_operator_guide_documents_all_cli_commands() -> None:
    guide = GUIDE.read_text(encoding="utf-8")

    for command in ["preview", "answer-preview", "close-preview", "summary-preview", "apply-close"]:
        assert command in guide


def test_operator_guide_covers_operational_safety_topics() -> None:
    guide = GUIDE.read_text(encoding="utf-8")

    required_text = [
        "127.0.0.1:7890",
        "CodeGraph",
        "Preview And Apply Safety",
        "When Not To Answer Or Close",
        "Release Verification",
        ".venv/bin/python -m pytest",
        ".issue-agent/state/",
        "GitHub App authentication",
        "multi-repo scheduling",
        "provider quality or cost dashboards",
    ]
    for text in required_text:
        assert text in guide

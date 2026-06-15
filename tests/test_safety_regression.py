import re
import subprocess
from pathlib import Path


MUTATION_ALLOWED_PATHS = {
    Path("issue_agent/github.py"),
    Path("tests/test_apply.py"),
    Path("tests/test_regression_workflows.py"),
    Path("tests/test_safety_regression.py"),
    Path("README.md"),
    Path("docs/OPERATOR_GUIDE.md"),
}

SECRET_VALUE_PATTERNS = [
    re.compile(r"/Users/[^/\s]+/Documents/autoresearch/config/config\.yaml"),
    re.compile(r"\bghp_[A-Za-z0-9_]{10,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{10,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{10,}\b"),
    re.compile(r"(?m)^\s*MINIMAX_API_KEY\s*=\s*['\"]?[^'\"\s#]+"),
    re.compile(r"(?im)^\s*(password|passwd)\s*[:=]\s*[^#\s]+"),
]


def test_github_mutation_commands_are_isolated_to_apply_boundaries() -> None:
    offenders: list[str] = []
    for path in _tracked_files():
        if not _is_surface_file(path):
            continue
        text = path.read_text(encoding="utf-8")
        if "gh issue" not in text and '"gh", "issue"' not in text:
            continue
        if path not in MUTATION_ALLOWED_PATHS:
            offenders.append(str(path))

    assert offenders == []


def test_tracked_files_do_not_contain_generated_state_or_obvious_secrets() -> None:
    tracked = _tracked_files()

    assert all(not path.as_posix().startswith(".issue-agent/state/") for path in tracked)

    offenders: list[str] = []
    for path in tracked:
        if path.suffix not in {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt", ""}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(text):
                offenders.append(f"{path}: {pattern.pattern}")

    assert offenders == []


def _tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        check=True,
        text=True,
    )
    return [Path(line) for line in completed.stdout.splitlines() if line]


def _is_surface_file(path: Path) -> bool:
    if path.suffix not in {".py", ".md"}:
        return False
    return (
        path.as_posix().startswith("issue_agent/")
        or path.as_posix().startswith("tests/")
        or path.as_posix().startswith("docs/")
        or path == Path("README.md")
    )

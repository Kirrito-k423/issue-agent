import re
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol

from issue_agent.models import EvidenceRef


class CommandResult(Protocol):
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[[Sequence[str]], CommandResult]

_SOURCE_PATH_RE = re.compile(r"(?P<path>[\w./-]+\.(?:py|md|toml|ya?ml|json))")


def has_codegraph_index(repo_root: Path) -> bool:
    return (repo_root / ".codegraph").is_dir()


def lookup_source_evidence(
    repo_root: Path,
    query: str,
    runner: CommandRunner | None = None,
) -> list[EvidenceRef]:
    target_root = repo_root.resolve()
    command_runner = runner or _run_command

    if has_codegraph_index(target_root):
        result = command_runner(["codegraph", "explore", query])
        if result.returncode == 0 and result.stdout.strip():
            return [_evidence_from_codegraph_output(target_root, query, result.stdout)]

    return []


def _run_command(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        capture_output=True,
        check=False,
        text=True,
    )


def _evidence_from_codegraph_output(repo_root: Path, query: str, output: str) -> EvidenceRef:
    snippet = _first_nonempty_line(output)
    path = _extract_relative_path(repo_root, output) or "codegraph"
    return EvidenceRef(
        kind="source",
        value=path,
        reason=f"CodeGraph result for query: {query}",
        lookup_mode="codegraph",
        path=path,
        snippet=snippet,
        codegraph_available=True,
    )


def _first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _extract_relative_path(repo_root: Path, text: str) -> str | None:
    match = _SOURCE_PATH_RE.search(text)
    if match is None:
        return None
    raw_path = Path(match.group("path"))
    if raw_path.is_absolute():
        try:
            return raw_path.relative_to(repo_root).as_posix()
        except ValueError:
            return raw_path.name
    return raw_path.as_posix()

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


CommandRunner = Callable[[Sequence[str], Path], CommandResult]

_SOURCE_PATH_RE = re.compile(r"(?P<path>[\w./-]+\.(?:py|md|toml|ya?ml|json))")
_SEARCH_EXTENSIONS = {".py", ".md", ".toml", ".yaml", ".yml", ".json"}
_SKIP_DIRS = {".codegraph", ".git", ".mypy_cache", ".pytest_cache", ".venv", "__pycache__"}


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
        try:
            result = command_runner(["codegraph", "explore", query], target_root)
        except Exception:
            return _fallback_search(target_root, query, True, "codegraph_failed")
        if result.returncode == 0 and result.stdout.strip():
            return [_evidence_from_codegraph_output(target_root, query, result.stdout)]
        return _fallback_search(target_root, query, True, "codegraph_failed")

    return _fallback_search(target_root, query, False, "codegraph_missing")


def _run_command(argv: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        capture_output=True,
        check=False,
        cwd=cwd,
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


def _fallback_search(
    repo_root: Path,
    query: str,
    codegraph_available: bool,
    fallback_reason: str,
) -> list[EvidenceRef]:
    query_terms = _query_terms(query)
    for path in _iter_searchable_files(repo_root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if _line_matches(line, query_terms):
                relative_path = path.relative_to(repo_root).as_posix()
                return [
                    EvidenceRef(
                        kind="source",
                        value=relative_path,
                        reason=f"Fallback source search matched query: {query}",
                        lookup_mode="fallback_search",
                        path=relative_path,
                        snippet=line.strip(),
                        line_start=line_number,
                        line_end=line_number,
                        codegraph_available=codegraph_available,
                        fallback_reason=fallback_reason,
                    )
                ]
    return [
        EvidenceRef(
            kind="source_lookup",
            value="no_source_match",
            reason=f"Fallback source search found no source evidence for query: {query}",
            lookup_mode="fallback_search",
            codegraph_available=codegraph_available,
            fallback_reason=fallback_reason,
        )
    ]


def _iter_searchable_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in _SEARCH_EXTENSIONS:
            files.append(path)
    return sorted(files)


def _query_terms(query: str) -> list[str]:
    return [term for term in re.split(r"\W+", query.lower()) if len(term) >= 3]


def _line_matches(line: str, query_terms: list[str]) -> bool:
    if not query_terms:
        return False
    normalized = line.lower()
    return any(term in normalized for term in query_terms)

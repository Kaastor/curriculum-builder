"""Scope file path and section-selection helpers."""

from __future__ import annotations

import re
from pathlib import Path

from learning_compiler.agent import ScopeIngestMode
from learning_compiler.config import load_config
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.orchestration.fs import resolve_within


def resolve_scope_path(run_dir: Path, scope_file: str) -> Path:
    candidate = Path(scope_file).expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.exists() or not candidate.is_file():
        raise LearningCompilerError(
            ErrorCode.NOT_FOUND,
            f"Scope file not found: {scope_file}",
            {"scope_file": str(candidate)},
        )

    config = load_config()
    allowed_roots = (config.repo_root.resolve(), config.runs_dir.resolve(), run_dir.resolve())
    for root in allowed_roots:
        try:
            resolve_within(root, candidate)
            return candidate
        except LearningCompilerError:
            continue

    raise LearningCompilerError(
        ErrorCode.INVALID_ARGUMENT,
        "Scope file must be inside the repository, runs directory, or current run directory.",
        {"scope_file": str(candidate)},
    )


def _canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _section_match(heading_path: tuple[str, ...], section_filters: tuple[str, ...]) -> bool:
    if not section_filters:
        return True
    normalized_path = " / ".join(_canonical_key(heading) for heading in heading_path if heading.strip())
    return any(filter_text in normalized_path for filter_text in section_filters)


def selected_scope_text(
    scope_path: Path,
    *,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> str:
    lines = scope_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Scope document is empty: {scope_path}",
            {"scope_file": str(scope_path)},
        )

    heading_re = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
    bullet_re = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")

    selected: list[str] = []
    heading_stack: list[str] = []
    in_code_block = False
    in_front_matter = bool(lines and lines[0].strip() == "---")

    normalized_filters = tuple(
        filter_text
        for filter_text in (_canonical_key(item) for item in section_filters)
        if filter_text
    )

    for index, raw_line in enumerate(lines):
        line_no = index + 1
        stripped = raw_line.strip()

        if in_front_matter:
            if line_no == 1:
                continue
            if stripped == "---":
                in_front_matter = False
            continue

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        heading_match = heading_re.match(raw_line)
        if heading_match:
            depth = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            while len(heading_stack) >= depth:
                heading_stack.pop()
            heading_stack.append(heading)
            if mode == ScopeIngestMode.SEED_LIST:
                continue
            if mode == ScopeIngestMode.SECTION and not _section_match(tuple(heading_stack), normalized_filters):
                continue
            selected.append(raw_line)
            continue

        if mode == ScopeIngestMode.SECTION and not _section_match(tuple(heading_stack), normalized_filters):
            continue
        if mode == ScopeIngestMode.SEED_LIST and not bullet_re.match(raw_line):
            continue
        if stripped:
            selected.append(raw_line)

    normalized = "\n".join(selected).strip()
    if not normalized:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Selected scope content is empty after applying mode/section filters.",
            {"scope_file": str(scope_path), "mode": mode.value, "section_filters": list(section_filters)},
        )
    return normalized + "\n"

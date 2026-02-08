"""Markdown parsing utilities for scope extraction."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from learning_compiler.agent.scope_contracts import ScopeIngestMode, ScopeItem
from learning_compiler.errors import ErrorCode, LearningCompilerError


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*?)\s*$")
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?[\s:-]+\|[\s|:-]*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_WHITESPACE_RE = re.compile(r"\s+")
_META_PREFIXES = (
    "purpose:",
    "acceptance:",
    "rationale:",
    "related design:",
    "suggested execution order",
)


def normalize_text(raw: str) -> str:
    value = raw.strip()
    value = _LINK_RE.sub(r"\1", value)
    value = value.replace("`", "")
    value = value.replace("**", "").replace("*", "").replace("_", "")
    value = value.replace("->", " to ")
    value = _WHITESPACE_RE.sub(" ", value).strip(" -:;,.")
    return value


def canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def build_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}{digest}"


def matches_section(heading_path: tuple[str, ...], section_filters: tuple[str, ...]) -> bool:
    if not section_filters:
        return True
    normalized_path = " / ".join(
        fragment
        for fragment in (canonical_key(heading) for heading in heading_path)
        if fragment
    )
    return any(filter_text in normalized_path for filter_text in section_filters)


def is_meta_line(text: str) -> bool:
    lowered = text.lower().strip()
    if not lowered:
        return True
    if lowered in {"abstract", "reader's guide", "how to use the granularity levels"}:
        return True
    return any(lowered.startswith(prefix) for prefix in _META_PREFIXES)


def collect_scope_items(
    scope_path: Path,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> tuple[ScopeItem, ...]:
    lines = scope_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Scope document is empty: {scope_path}",
            {"scope_file": str(scope_path)},
        )

    items: list[ScopeItem] = []
    heading_stack: list[str] = []
    in_code_block = False
    in_front_matter = bool(lines and lines[0].strip() == "---")

    for index, raw_line in enumerate(lines):
        line_no = index + 1
        stripped = raw_line.strip()
        if not stripped:
            continue

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

        heading_match = _HEADING_RE.match(raw_line)
        if heading_match:
            depth = len(heading_match.group(1))
            heading = normalize_text(heading_match.group(2))
            if not heading:
                continue
            while len(heading_stack) >= depth:
                heading_stack.pop()
            heading_stack.append(heading)
            if mode == ScopeIngestMode.SEED_LIST:
                continue
            if mode == ScopeIngestMode.SECTION and not section_filters:
                continue
            if not matches_section(tuple(heading_stack), section_filters):
                continue
            if is_meta_line(heading):
                continue
            items.append(
                ScopeItem(
                    id=build_id("S", str(scope_path), str(line_no), heading),
                    text=heading,
                    kind="heading",
                    source_path=str(scope_path),
                    heading_path=tuple(heading_stack),
                    line_span=(line_no, line_no),
                )
            )
            continue

        if mode == ScopeIngestMode.SECTION and section_filters:
            if not matches_section(tuple(heading_stack), section_filters):
                continue

        bullet_match = _BULLET_RE.match(raw_line)
        if bullet_match:
            item_text = normalize_text(bullet_match.group(1))
            if item_text and not is_meta_line(item_text):
                items.append(
                    ScopeItem(
                        id=build_id("S", str(scope_path), str(line_no), item_text),
                        text=item_text,
                        kind="bullet",
                        source_path=str(scope_path),
                        heading_path=tuple(heading_stack),
                        line_span=(line_no, line_no),
                    )
                )
            continue

        if "|" in raw_line and raw_line.count("|") >= 2:
            if _TABLE_SEPARATOR_RE.match(raw_line):
                continue
            for cell_index, cell in enumerate(raw_line.strip().strip("|").split("|")):
                cell_text = normalize_text(cell)
                if not cell_text or is_meta_line(cell_text):
                    continue
                items.append(
                    ScopeItem(
                        id=build_id("S", str(scope_path), str(line_no), str(cell_index), cell_text),
                        text=cell_text,
                        kind="table_cell",
                        source_path=str(scope_path),
                        heading_path=tuple(heading_stack),
                        line_span=(line_no, line_no),
                    )
                )
            continue

        if mode == ScopeIngestMode.SEED_LIST:
            continue

        for sentence in re.split(r"[.!?]+", raw_line):
            item_text = normalize_text(sentence)
            if len(item_text) < 6 or is_meta_line(item_text):
                continue
            items.append(
                ScopeItem(
                    id=build_id("S", str(scope_path), str(line_no), item_text),
                    text=item_text,
                    kind="prose",
                    source_path=str(scope_path),
                    heading_path=tuple(heading_stack),
                    line_span=(line_no, line_no),
                )
            )

    return tuple(items)

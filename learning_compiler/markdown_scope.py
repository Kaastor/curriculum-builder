"""Shared markdown phrase extraction utilities for scope-driven flows."""

from __future__ import annotations

import re


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*?)\s*$")


def normalize_markdown_phrase(raw: str) -> str:
    """Normalize markdown-derived text into a compact phrase."""
    value = raw.strip()
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("`", "")
    value = re.sub(r"\s+", " ", value).strip(" -:;,.")
    return value


def markdown_phrase_candidates(
    text: str,
    *,
    max_heading_depth: int = 3,
    min_sentence_words: int = 1,
) -> tuple[str, ...]:
    """Extract heading/bullet/sentence phrases from markdown-like text.

    Parsing skips YAML front matter and fenced code blocks.
    """
    candidates: list[str] = []
    lines = text.splitlines()
    in_code = False
    in_front_matter = bool(lines and lines[0].strip() == "---")

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
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue

        heading_match = HEADING_RE.match(raw_line)
        if heading_match:
            depth = len(heading_match.group(1))
            if depth <= max_heading_depth:
                heading = normalize_markdown_phrase(heading_match.group(2))
                if heading:
                    candidates.append(heading)
            continue

        bullet_match = BULLET_RE.match(raw_line)
        if bullet_match:
            bullet = normalize_markdown_phrase(bullet_match.group(1))
            if bullet:
                candidates.append(bullet)
            continue

        for fragment in re.split(r"[.!?;]+", stripped):
            sentence = normalize_markdown_phrase(fragment)
            if not sentence:
                continue
            if len(sentence.split()) < min_sentence_words:
                continue
            candidates.append(sentence)

    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return tuple(deduped)

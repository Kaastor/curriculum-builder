"""Centralized application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class AppConfig:
    repo_root: Path
    runs_dir: Path
    runs_archive_dir: Path
    topic_spec_template: Path
    agent_provider: str
    agent_model: str
    coding_agent_cmd: str


def load_config() -> AppConfig:
    repo_root = Path(__file__).resolve().parents[1]
    runs_dir = Path(os.environ.get("ORCHESTRATION_BASE_DIR", str(repo_root / "runs")))
    archive_dir = Path(
        os.environ.get("ORCHESTRATION_ARCHIVE_DIR", str(runs_dir / "archives"))
    )
    template_path = Path(
        os.environ.get(
            "ORCHESTRATION_TEMPLATE_FILE",
            str(runs_dir / "templates" / "topic_spec.template.json"),
        )
    )
    agent_provider = os.environ.get("AGENT_PROVIDER", "codex_exec")
    agent_model = os.environ.get("AGENT_MODEL", "")
    coding_agent_cmd = os.environ.get("CODING_AGENT_CMD", "codex")

    return AppConfig(
        repo_root=repo_root,
        runs_dir=runs_dir,
        runs_archive_dir=archive_dir,
        topic_spec_template=template_path,
        agent_provider=agent_provider,
        agent_model=agent_model,
        coding_agent_cmd=coding_agent_cmd,
    )


def reset_config_cache() -> None:
    """Compatibility no-op; config is loaded directly per call."""
    return None

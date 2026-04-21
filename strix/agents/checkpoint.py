import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from strix.config import Config

from .state import AgentState


CHECKPOINT_VERSION = 1
CHECKPOINT_FILENAME = "checkpoint.json"


def _is_enabled() -> bool:
    return str(Config.get("strix_checkpoint_enabled") or "true").lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


def _state_to_dict(state: AgentState) -> dict[str, Any]:
    return state.model_dump(mode="json")


def _runs_dir() -> Path:
    runs_dir = Path.cwd() / "strix_runs"
    runs_dir.mkdir(exist_ok=True)
    return runs_dir


def _checkpoint_path(identifier: str | Path) -> Path:
    path = Path(identifier)
    if path.exists():
        if path.is_dir():
            return path / CHECKPOINT_FILENAME
        return path

    if str(identifier) == "latest":
        checkpoints = sorted(
            _runs_dir().glob(f"*/{CHECKPOINT_FILENAME}"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        if checkpoints:
            return checkpoints[0]
        return _runs_dir() / "latest" / CHECKPOINT_FILENAME

    return _runs_dir() / str(identifier) / CHECKPOINT_FILENAME


class CheckpointManager:
    def __init__(self, run_name: str):
        self.run_name = run_name

    @property
    def run_dir(self) -> Path:
        run_dir = _runs_dir() / self.run_name
        run_dir.mkdir(exist_ok=True)
        return run_dir

    @property
    def path(self) -> Path:
        return self.run_dir / CHECKPOINT_FILENAME

    def save(
        self,
        *,
        root_state: AgentState,
        scan_config: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        if not _is_enabled():
            return self.path

        payload = {
            "version": CHECKPOINT_VERSION,
            "run_name": self.run_name,
            "saved_at": datetime.now(UTC).isoformat(),
            "scan_config": scan_config,
            "root_state": _state_to_dict(root_state),
            "metadata": metadata or {},
        }

        tmp_path = self.path.with_suffix(".json.tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.path)
        return self.path


def load_checkpoint(identifier: str | Path) -> dict[str, Any]:
    path = _checkpoint_path(identifier)
    if not path.exists():
        raise FileNotFoundError(f"No checkpoint found for '{identifier}'")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or data.get("version") != CHECKPOINT_VERSION:
        raise ValueError(f"Unsupported checkpoint format: {path}")
    return data


def restore_root_state(checkpoint: dict[str, Any]) -> AgentState:
    state = AgentState.model_validate(checkpoint["root_state"])
    state.sandbox_id = None
    state.sandbox_token = None
    state.sandbox_info = None
    state.waiting_for_input = False
    state.waiting_start_time = None
    state.stop_requested = False
    state.completed = False
    state.llm_failed = False
    state.add_message(
        "user",
        (
            "<checkpoint_resume>"
            "Resume from the saved checkpoint. Previous live subagents are not restored; "
            "use the retained conversation, notes, artifacts, and reports to continue from "
            "the last saved progress instead of restarting discovery."
            "</checkpoint_resume>"
        ),
    )
    return state

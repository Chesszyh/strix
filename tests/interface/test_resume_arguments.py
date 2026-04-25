import sys
from types import SimpleNamespace

from strix.agents.checkpoint import CheckpointManager
from strix.agents.state import AgentState
from strix.interface.main import apply_resume_checkpoint, parse_arguments


def test_parse_arguments_allows_resume_without_target(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["strix", "--resume", "resume-run"])

    args = parse_arguments()

    assert args.resume == "resume-run"
    assert args.target is None
    assert args.targets_info == []


def test_parse_arguments_defaults_resume_to_latest(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["strix", "--resume"])

    args = parse_arguments()

    assert args.resume == "latest"
    assert args.targets_info == []


def test_apply_resume_checkpoint_populates_targets_and_run_name(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    CheckpointManager("resume-run").save(
        root_state=AgentState(task="scan"),
        scan_config={
            "run_name": "resume-run",
            "targets": [
                {
                    "type": "local_code",
                    "details": {"target_path": str(tmp_path / "app")},
                    "original": str(tmp_path / "app"),
                }
            ],
            "user_instructions": "focus auth",
        },
    )

    args = SimpleNamespace(
        resume="resume-run",
        targets_info=[],
        instruction=None,
    )

    apply_resume_checkpoint(args)

    assert args.run_name == "resume-run"
    assert args.instruction == "focus auth"
    assert args.resume_checkpoint["run_name"] == "resume-run"
    assert args.targets_info[0]["details"]["workspace_subdir"] == "app"

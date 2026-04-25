from strix.agents.checkpoint import CheckpointManager, load_checkpoint
from strix.agents.state import AgentState


def test_checkpoint_roundtrips_root_state(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    state = AgentState(
        agent_id="agent-root",
        agent_name="Root Agent",
        task="scan /workspace/app",
        iteration=7,
        max_iterations=42,
    )
    state.add_message("user", "initial task")
    state.add_message("assistant", "latest useful progress")

    manager = CheckpointManager("resume-run")
    checkpoint_path = manager.save(
        root_state=state,
        scan_config={"run_name": "resume-run", "targets": [{"original": "."}]},
        metadata={"reason": "iteration"},
    )

    assert checkpoint_path == tmp_path / "strix_runs" / "resume-run" / "checkpoint.json"
    loaded = load_checkpoint("resume-run")

    assert loaded["version"] == 1
    assert loaded["scan_config"]["run_name"] == "resume-run"
    assert loaded["root_state"]["agent_id"] == "agent-root"
    assert loaded["root_state"]["iteration"] == 7
    assert loaded["root_state"]["messages"][-1]["content"] == "latest useful progress"


def test_checkpoint_loads_from_explicit_file_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    state = AgentState(agent_id="agent-root", agent_name="Root Agent", task="scan")
    checkpoint_path = CheckpointManager("explicit-run").save(
        root_state=state,
        scan_config={"run_name": "explicit-run"},
    )

    loaded = load_checkpoint(str(checkpoint_path))

    assert loaded["run_name"] == "explicit-run"
    assert loaded["root_state"]["task"] == "scan"

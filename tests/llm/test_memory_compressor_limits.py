from strix.llm import memory_compressor
from strix.llm.memory_compressor import MemoryCompressor


def test_compressor_uses_configured_budget_and_keeps_recent_messages(monkeypatch) -> None:
    monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")
    monkeypatch.setenv("STRIX_CONTEXT_MAX_TOKENS", "60")
    monkeypatch.setenv("STRIX_CONTEXT_RECENT_MESSAGES", "2")
    monkeypatch.setenv("STRIX_CONTEXT_SUMMARY_CHUNK_MESSAGES", "10")

    monkeypatch.setattr(
        memory_compressor,
        "_get_message_tokens",
        lambda msg, _model: len(str(msg.get("content", "")).split()),
    )

    summarized_counts: list[int] = []

    def fake_summarize(messages, _model, _timeout=30):
        summarized_counts.append(len(messages))
        return {
            "role": "user",
            "content": (
                f"<context_summary message_count='{len(messages)}'>"
                "summary</context_summary>"
            ),
        }

    monkeypatch.setattr(memory_compressor, "_summarize_messages", fake_summarize)

    messages = [
        {"role": "user", "content": ("old context " * 12).strip()},
        {"role": "assistant", "content": ("tool output " * 12).strip()},
        {"role": "user", "content": ("more old context " * 10).strip()},
        {"role": "assistant", "content": "recent assistant"},
        {"role": "user", "content": "recent user"},
    ]

    compressed = MemoryCompressor().compress_history(messages)

    assert summarized_counts == [3]
    assert compressed[0]["content"].startswith("<context_summary")
    assert compressed[-2:] == messages[-2:]


def test_compressor_does_not_call_model_when_under_budget(monkeypatch) -> None:
    monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")
    monkeypatch.setenv("STRIX_CONTEXT_MAX_TOKENS", "1000")
    monkeypatch.setenv("STRIX_CONTEXT_RECENT_MESSAGES", "2")
    monkeypatch.setattr(memory_compressor, "_get_message_tokens", lambda _msg, _model: 10)

    def fail_summarize(*_args, **_kwargs):
        raise AssertionError("summary should not run below budget")

    monkeypatch.setattr(memory_compressor, "_summarize_messages", fail_summarize)

    messages = [
        {"role": "user", "content": "small"},
        {"role": "assistant", "content": "small"},
    ]

    assert MemoryCompressor().compress_history(messages) is messages

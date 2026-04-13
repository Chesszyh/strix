import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_utils_module():
    module_path = Path(__file__).resolve().parents[2] / "strix" / "interface" / "utils.py"
    spec = importlib.util.spec_from_file_location("strix_interface_utils_llm_test", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load strix.interface.utils for tests")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


utils = _load_utils_module()


def _response(
    *,
    content=None,
    tool_calls=None,
    reasoning_content=None,
    finish_reason="stop",
):
    message = SimpleNamespace(
        content=content,
        tool_calls=tool_calls,
        reasoning_content=reasoning_content,
    )
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice])


def _chunk(content=None):
    return SimpleNamespace(
        choices=[SimpleNamespace(delta=SimpleNamespace(content=content))]
    )


def test_validate_llm_response_includes_response_shape_details() -> None:
    response = _response(content=None, tool_calls=None, reasoning_content=None)

    with pytest.raises(RuntimeError, match=r"content=empty"):
        utils.validate_llm_response(response)


def test_extract_streamed_llm_text_joins_content_chunks() -> None:
    chunks = [_chunk("O"), _chunk(None), _chunk("K")]

    assert utils.extract_streamed_llm_text(chunks) == "OK"

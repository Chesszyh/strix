## Summary

Update the LLM startup warm-up check to use a streaming completion probe, matching the request path used by the main agent loop. This avoids rejecting OpenAI-compatible local gateways that return valid streamed deltas but leave non-streaming `message.content` empty.

## Root Cause

`warm_up_llm()` previously called `litellm.completion()` without `stream=True` and then required `response.choices[0].message.content` to be present. Some OpenAI-compatible gateways can return `content: null` for non-streaming chat completions while still returning usable text through streaming chunks. Since Strix's runtime generation path already streams responses, the warm-up check could fail even when the configured model was usable by the actual scan flow.

## Changes

- Make the warm-up LLM probe request streamed completions.
- Extract text from streamed delta chunks before treating the response as invalid.
- Add more diagnostic detail when an LLM response is invalid, including content, tool call, reasoning content, and finish reason state.
- Add regression tests for empty-response diagnostics and streamed chunk extraction.

## Validation

- `uv run pytest -q tests/interface/test_diff_scope.py tests/interface/test_llm_response_validation.py`
- Manual warm-up check against an OpenAI-compatible local endpoint where non-streaming responses have `content: null` but streaming responses return text.

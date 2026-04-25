# Repository Guidelines

## Project Structure & Module Organization

Core application code lives in `strix/`. Key areas include `agents/` for orchestration and checkpoints, `llm/` for model integration and memory compression, `tools/` for sandboxed capabilities, `interface/` for CLI/TUI entrypoints, and `config/`/`telemetry/` for runtime settings and observability. Tests mirror the package layout under `tests/` (`tests/interface/`, `tests/llm/`, `tests/tools/`, etc.). Documentation is in `docs/`, prompt templates in `strix/prompts/`, and reusable scanning knowledge in `strix/skills/`.

## Build, Test, and Development Commands

- `make setup-dev`: install development dependencies with `uv` and register pre-commit hooks.
- `uv run strix --target ./app`: run the local source checkout instead of any globally installed `strix`.
- `make format`: format Python with Ruff.
- `make lint`: run Ruff with fixes plus Pylint.
- `make type-check`: run MyPy and Pyright in strict mode.
- `make test`: run the full pytest suite.
- `make test-cov`: run tests with terminal, HTML, and XML coverage reports.
- `make check-all`: run format, lint, type, and security checks.

## Coding Style & Naming Conventions

Target Python 3.12+ and keep code compatible with the strict settings in `pyproject.toml`. Use 4-space indentation, double quotes, and a 100-character line limit. Prefer explicit type hints on production code. Follow snake_case for modules, functions, and test files; use `Test*` classes only when they improve grouping. Keep imports Ruff/isort-compatible and avoid ad hoc formatting changes unrelated to your patch.

## Testing Guidelines

Pytest is the test framework, with coverage enabled by default. Name tests `test_*.py` or `*_test.py`, and add focused regression tests for every bug fix. Prefer targeted runs while iterating, for example: `uv run pytest tests/interface/test_resume_arguments.py -q`. Before opening a PR, run at least the most relevant file-level tests plus any affected cross-cutting suites.

## Commit & Pull Request Guidelines

Recent history follows concise Conventional Commit-style subjects such as `fix:`, `feat:`, and `chore:`. Keep commit messages imperative and scoped to one change. PRs should explain what changed, why it changed, and how it was verified. Link related issues when applicable, include exact commands used for validation, and update docs when changing CLI flags, configuration behavior, prompts, or skills. Add screenshots only for visible TUI or documentation UI changes.

## Security & Configuration Tips

Do not commit API keys, sandbox tokens, or generated scan output. Configure local runs with environment variables such as `STRIX_LLM`, `LLM_API_KEY`, and `LLM_API_BASE`. Docker must be running for sandbox-backed scans. Treat `strix_runs/` as generated output, not source-controlled content.

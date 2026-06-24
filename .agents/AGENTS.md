# AGENTS.md - Workspace Rules

## Technology Stack
- **Python**: `>=3.11,<3.13`
- **Dependency Manager**: `uv` (use `uv sync` and `uv run`)
- **Web UI**: Streamlit (`webui/Main.py`)
- **API Frame**: FastAPI (`app/asgi.py`)
- **Logging**: `loguru` (prefer standard logger over print)

## Code Guidelines
- **YAGNI**: Keep implementation simple. No over-engineering.
- **Imports**: Group imports (standard library, third-party, local `app.*`).
- **Error Handling**: Log failures with traceback/context.
- **Tests**: Add test cases to `test/services/` for logic changes. Run tests before completing.

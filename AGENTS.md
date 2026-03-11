# AGENTS.md

## Project Guidelines
- Always propose a plan in numbered steps before editing code.
- Keep changes minimal and avoid overengineering.
- Remove temporary or large data files, never commit datasets.

## Conventions
- Python: PEP8 style, Ruff linting, NumPy-style docstrings.
- Use pytest for testing, prefer pandas/NumPy/scikit-learn for analysis.
- Jupyter notebooks must remain reproducible: no hard-coded paths, use relative paths.

## Agent Instructions
- Runs `pytest -q` after changes and share results.
- Confirm before installing new dependencies.
- Use Poetry for dependency management.
- Never write secrets, always use environment variables.
- IMPORTANT: Always use PandasAI v3 (pandasai >= 3.0.0) functions and conventions.
- Check official PandasAI v3 docs before writing or modifying any PandasAI code.
- Use a framework like LangChain/LangGraph if needed for orchestration.
- CRITICAL: Keep development modular, simple and fit for production for easy maintenance.

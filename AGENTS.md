# Repository Guidelines

## Project Structure & Module Organization

This repository contains small Python learning projects. `codex-lab/` is the customer-management SQLite project: `models.py` defines the four SQLAlchemy models, `database.py` configures the engine and sessions, `seed.py` generates sample data, and `erd.md` documents the schema. `README.md` explains setup and usage. `codex-practice/` contains a separate practice project. There is no checked-in test or asset directory. The generated `codex-lab/customer.db` is local data; avoid committing it unless a task specifically requires the database artifact.

## Build, Test, and Development Commands

Run commands from `codex-lab/`:

- `python -m pip install "SQLAlchemy>=2.0,<3.0" Faker` installs the project dependencies.
- `python database.py` creates `customer.db` and its tables.
- `python seed.py` repopulates the four tables with deterministic sample data. This deletes existing rows first.
- `python -m compileall models.py database.py seed.py` checks Python syntax without changing the database.

No build system or automated test suite is configured. When changing the schema or seed logic, run the relevant script and verify table counts and foreign keys with SQLite.

## Coding Style & Naming Conventions

Use Python 3.10+ and four spaces per indentation level. Follow standard Python naming: `snake_case` for modules, functions, variables, and columns; `PascalCase` for ORM classes; uppercase names for constants. Keep SQLAlchemy models and relationships in `models.py`, and database setup in `database.py`. Add clear column comments and preserve SQLite foreign-key enforcement. Keep seed data generation reproducible by fixing random seeds and avoiding per-row database commits.

## Testing Guidelines

There is no pytest or coverage configuration yet. If adding tests, use pytest, place them under `tests/`, and name files `test_*.py`. Tests should use a temporary SQLite database rather than overwrite the checked-in working database. Cover model relationships, seed counts, and computed order totals.

## Commit & Pull Request Guidelines

Recent commits use conventional prefixes such as `feat:`, `docs:`, and `chore:`, followed by a concise Korean or English summary. Keep each commit focused. Pull requests should explain the behavior or schema change, include the commands used to verify it, and call out destructive seed behavior or database migrations. Include screenshots only when a visual artifact changes.

## Security & Local Data

Do not commit credentials or local environment files. `.env`, Python bytecode, and `__pycache__/` are ignored. Treat `seed.py` as destructive to existing table rows and retain deterministic seeds for reproducible practice data.

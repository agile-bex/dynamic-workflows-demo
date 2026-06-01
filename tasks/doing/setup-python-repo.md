# Setup Python repo

## Goal

A working Python project managed by **uv**, ready for the other tasks to build on.
"Done" means `uv run` works and there's a clean package layout to add modules to.

## Dependencies

None — this is the foundation.

## What it needs

- A uv-managed project: `pyproject.toml`, a lockfile, Python 3.
- A package directory for the app's code to live in.
- A trivial runnable entry (a hello / health check) so `uv run` proves the
  toolchain works.
- pytest available as a dev dependency, so later tasks can add tests and
  `uv run pytest` works.

## Done when

- `uv run` executes without error.
- `uv run pytest` runs without config errors (even with one trivial test).
- The layout is clean enough to drop new modules into.

## Out of scope

- No app features, no todo logic, no UI. Just the scaffold.

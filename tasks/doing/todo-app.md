# Todo app (PySide6)

## Goal

A PySide6 desktop app giving a simple CRUD UI over the todo store — add, list,
complete / un-complete, delete — so a person can manage their to-dos. The human
launches it with `uv run app`.

## Dependencies

Needs the **`todo_store` module** from `todo-store` to exist — this app imports it
and calls its CRUD functions. If the module isn't there, stop and flag it; do not
stub it.

## What it needs

- A PySide6 window: add a todo, see the list, toggle complete, delete.
- All data goes through the existing `todo_store` module — no separate persistence
  logic here.
- An **`app` script wired into `pyproject.toml`** so the human can launch it with
  `uv run app`.

## Notes for the implementer

- 🚨 **DO NOT RUN THIS APP. DO NOT CALL `exec()` OR LAUNCH THE GUI.** It is a
  desktop GUI on the human's machine — launching it will hang you, and running it
  is the human's job. There are **no automated tests here, by design.**
- Your bar for "done" is: **code complete, `uv run app` wired into `pyproject.toml`,
  and the modules import cleanly.** The most you may do to check is
  `python -c "import <module>"` to catch import / syntax errors — never instantiate
  a window, never enter an event loop.

## Notes for the reviewer

- This is a GUI app with **no tests, by design, and you cannot run it.** Do **not**
  try to launch it, and **do not block it for missing tests or missing runtime
  verification** — that is intentional.
- Review the code for quality and whether it matches the goal, and confirm
  `uv run app` is wired into `pyproject.toml`. The human QAs behavior via
  `uv run app`.

## Done when

- The PySide6 app's code is complete and imports cleanly.
- `uv run app` is wired into `pyproject.toml`.
- (Behavior is verified by the human, not by an agent.)

## Out of scope

- No tests (skip qtbot). No new persistence — use `todo_store`. Don't run it.

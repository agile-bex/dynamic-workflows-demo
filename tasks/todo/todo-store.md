# Todo store

## Goal

A small, UI-free Python module that does CRUD on a to-do list, persisted to a
single `todos.json`, and **proven by a pytest suite.** This is the data + logic
layer the app will sit on top of.

## Dependencies

Needs the **uv Python project** from `setup-python-repo` to exist. If there's no
uv project / package to add a module to, stop and flag it.

## What it needs

- A module (e.g. `todo_store`) with create / read / list / update / delete.
- A todo is simple: at least an id, a title, and a done flag.
- Persistence to a **single `todos.json`** the module owns. Save/load round-trips;
  a missing or corrupt file loads as an empty list rather than crashing.
- A **pytest suite** covering the CRUD paths and the save/reload round-trip.

## Notes for the reviewer

- This task's bar is **the tests pass** — run `uv run pytest`; green is the gate.
- Confirm the tests actually exercise CRUD and the round-trip (not hollow tests),
  and judge the module on health and whether it does what's asked.

## Constraints

- **Tests must never touch a real `todos.json`** — use a temp path (`tmp_path`), so
  running the suite can't clobber real data.
- UI-free: the module must import and work with **no PySide6 / Qt** involved.

## Done when

- `uv run pytest` is green.
- The module CRUDs todos and round-trips them through `todos.json`.

## Out of scope

- No GUI. No server / HTTP. Just the module and its tests.

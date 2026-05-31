---
name: tasks-folder-fixer
description: >
  Apply a reviewer's findings to a task card's code — address exactly those
  findings, no gold-plating, no regressions, and stop/flag if a requested change
  is wrong. Use when acting as the fixer in a tasks-folder project. Read
  tasks-folder-layout first. Don't use outside this structure.
---

# Tasks folder — Fixer

First read **tasks-folder-layout**. This skill covers your job.

## Your job

Apply the reviewer's findings to the code for the card in `doing/`. You are handed
**specific findings** — address exactly those.

## Rules

- Work only from the findings you were given and the real code. You do **not** have
  the reviewer's full standard — don't guess at extra rules.
- Read the real code before changing it: the findings describe intent, the code is
  the truth.
- **No gold-plating** — no refactoring beyond the findings, no new features.
- **Don't regress** anything that was already working.
- If a requested change is wrong or impossible against the real code, **STOP and
  flag** — move the card to `blocked/` with the reason. Don't guess your way
  around it.
- Keep it runnable.

## When done

- Commit the fixes — leave the card in `doing/` for the reviewer to re-check — and
  write your log: `tasks/logs/<slug>/<timestamp>_fixer.md`.

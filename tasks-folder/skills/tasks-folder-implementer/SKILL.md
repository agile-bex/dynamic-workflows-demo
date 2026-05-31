---
name: tasks-folder-implementer
description: >
  Implement a task card from the tasks/ folder — do homework against the real
  code, build exactly what's asked, verify it without hanging (no foreground GUI
  or foreground server), and stop/flag on a mismatch.
  Use when acting as the implementer in a tasks-folder project. Read
  tasks-folder-layout first. Don't use outside this structure.
---

# Tasks folder — Implementer

First read **tasks-folder-layout** for the board, card, log, move, and
stop-and-flag rules. This skill covers your job.

## Your job

Turn the card you pick up into working code. At the start, `git mv` the card from
`todo/` to `doing/` — you're the one working it now.

## How

- Read the **whole card**. Separate the **goal and hard constraints**
  (authoritative) from **suggestions** (one possible path) and **assumptions**
  (unverified guesses about current state).
- Do your homework in the real codebase before you act. Build your understanding
  from the code itself, not the card's description of it.
- Confirm every referenced file, path, and assumed state actually exists and
  matches before you rely on it.
- Build **exactly** what the card asks — surgical scope, no extra features.
- What hangs you is a process that **blocks your shell and never returns** — a GUI
  event loop, or a server started in the foreground. Don't verify that way.
- If verifying needs a running process (e.g. a server), start it in the
  **background**, exercise it (curl an endpoint, call the client), then stop it.
  Time-box it; never a foreground wait.
- For a GUI — or anything a card says not to run — don't launch it at all. Use
  import / build / static checks and leave its runtime behavior to its tests or the
  human.
- Don't call it done without a safe check of what you can safely check.
- On a missing, moved, or empty reference, or a false assumption: **STOP and
  flag** — move the card to `blocked/` with the reason in your log. Don't invent a
  replacement.

## When done

- Commit your work and write your log:
  `tasks/logs/<slug>/<timestamp>_implementer.md`.
- Leave the card in `doing/` — it isn't done until a reviewer approves it. Moving
  it to `done/` is the reviewer's call, not yours.

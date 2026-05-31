---
name: tasks-folder-layout
description: >
  The shared layout and rules for a repo that manages work as cards in a tasks/
  folder (todo / doing / done / blocked, plus logs/). Read this before acting in
  any tasks-folder role — implementer, reviewer, or fixer. Only applies to
  projects that use this exact tasks/ structure; ignore it for ordinary repos.
---

# Tasks folder — layout & contract

This project tracks work as **cards** — one markdown file per task — that move
through a small board of folders. Every role works inside this layout. Your
role-specific skill says *what you do*; this says *the world you do it in*.

## The board

```
tasks/
├── todo/       <task>.md      cards waiting to be picked up
├── doing/      the one card currently being worked (one at a time)
├── done/       approved cards
├── blocked/    cards that hit a wall (reason lives in the card's log)
└── logs/       <slug>/<timestamp>_<role>.md
```

## Cards

- A card is a prose task doc: the goal, plus any dependencies stated in plain
  English. It is a **starting point, not gospel** — verify it against the real
  code; what you observe wins.
- **Never edit a card's body.** It stays as written. Your output goes into code,
  commits, and your log — never back into the card.
- Don't pick up a card whose stated prerequisites aren't in `done/` yet.
- A card may include sections addressed to a role — `## Notes for the implementer`,
  `## Notes for the reviewer`, etc. Read the whole card and **honor any notes
  addressed to your role.**

## Logs

- Each role writes its **own** log file per card:
  `tasks/logs/<slug>/<timestamp>_<role>.md`, where `<slug>` is the card's
  filename without `.md`.
- Get the timestamp by running: `date +%Y-%m-%d_%H-%M-%S` (works on macOS, Linux,
  and Windows Claude Code). Example:
  `tasks/logs/fastapi-server/2026-05-31_12-42-54_reviewer.md`.
- **Always write a new file — never edit or append to an existing one.**
  Timestamps sort chronologically and name who wrote what.

## Moving cards

- Move a card with `git mv`, folded into your work commit, so its journey shows
  up in git history too.
- **Pick up:** `todo/ → doing/` (the implementer, when starting a card).
- **Approve:** `doing/ → done/` (the reviewer, on approval).
- **Bail:** `→ blocked/` (whoever hits the wall).

## The cardinal rule (every role)

- On any mismatch with reality — a referenced file is missing, an assumption is
  false, a step no longer fits — **STOP**, move the card to `blocked/`, and write
  the specific reason in your log. **Never fabricate a fix or improvise scope.**
- Stay in scope. Note an important out-of-scope discovery in one line in your log;
  don't act on it.

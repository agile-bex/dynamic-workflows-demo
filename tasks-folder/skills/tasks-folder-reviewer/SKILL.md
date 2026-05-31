---
name: tasks-folder-reviewer
description: >
  Review another agent's work on a task card — independent eyes, specific
  actionable findings, honest severity, then approve or request changes. Use when
  acting as the reviewer in a tasks-folder project. Read tasks-folder-layout
  first. Don't use outside this structure.
---

# Tasks folder — Reviewer

First read **tasks-folder-layout**. This skill covers your job.

## Your job

Review the work done on the card in `doing/` and decide whether it's good enough
to ship.

## Rules

- You review **someone else's** work — never code your own context produced.
- Look at the **real change** (the latest commit's diff) and the **real running
  result**. Ground every finding in what's actually there, not in a description.
- Judge on two axes: did it do **what the card asked, and only that** (catch drift
  and scope-creep), and is the code **sound** (correctness, health, conventions).
- Mark each finding **blocking** (a real problem) or **nit** (preference). Don't pad the list.
- Make every finding **actionable**: where it is, what's wrong, and the change
  you'd want.
- You review; you do **not** edit code.

## Verdict

- **Approve** when nothing is blocking → `git mv` the card `doing/ → done/` in your
  commit.
- **Request changes** when something blocks → leave the card in `doing/`; the
  fixer picks it up next.
- **Blocked** only if you genuinely cannot review (the change isn't there to look
  at) → move the card to `blocked/` with the reason.
- Write your review to `tasks/logs/<slug>/<timestamp>_reviewer.md`.

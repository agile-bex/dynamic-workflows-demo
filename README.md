# Demo of Claude Dynamic Workflows

A demo of **Claude Code [Dynamic Workflows](https://code.claude.com/docs/en/workflows)** — packaged as an installable plugin.

It ships one workflow that runs an **agentic kanban board**: point it at a `tasks/`
folder full of task cards and it picks the next ready card, implements it, then
loops a reviewer and a fixer until the work is approved — moving each card
`todo/ -> doing/ -> done/` (or `blocked/`) and committing as it goes.

This is the companion repo to the YouTube walkthrough. You can read the code here,
or install it as a plugin and run it yourself.

---

## What's a Dynamic Workflow?

A Dynamic Workflow is a JavaScript script that orchestrates subagents
**deterministically** — real loops, conditionals, and fan-out in code, instead of
hoping one agent remembers to do every step. Each `agent()` call spawns a subagent;
with a JSON schema it returns validated structured data you can branch on.

The whole orchestration for this demo lives in one file:
[`tasks-folder/workflows/tasks-folder-workflow.js`](tasks-folder/workflows/tasks-folder-workflow.js).
It's ~200 lines and worth a read — that's the point of the demo.

## How this demo works

Work is tracked as **cards** — one markdown file per task — that move through a
small board of folders:

```
tasks/
├── todo/       cards waiting to be picked up
├── doing/      the one card being worked right now
├── done/       approved cards
├── blocked/    cards that hit a wall
└── logs/       <slug>/<timestamp>_<role>.md   (each role writes its own log)
```

The workflow drives three roles, each defined by a skill, each with a sharp,
non-overlapping job:

| Role            | Skill                      | Does                                                                                                                                       |
| --------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Layout**      | `tasks-folder-layout`      | The shared contract every role reads first: the board, the card rules, and the cardinal *stop-and-flag on any mismatch with reality* rule. |
| **Implementer** | `tasks-folder-implementer` | Picks up a card, does homework against the real code, builds exactly what's asked, verifies without hanging the shell.                     |
| **Reviewer**    | `tasks-folder-reviewer`    | Independent eyes on the implementer's commit: did it do what the card asked, and is it sound? Approves or requests changes.                |
| **Fixer**       | `tasks-folder-fixer`       | Applies *only* the reviewer's blocking findings — no gold-plating, no regressions.                                                         |

The control flow the workflow encodes:

```
for each card (dependency-aware: only picks a card whose prereqs are in done/):
    implement
    repeat up to 3 rounds:
        review
        if approved        -> move card to done/, next card
        if changes needed  -> fix, then review again
        if blocked          -> stop and flag
```

Every handoff between roles returns a **validated structured result** (pick /
implement / review / fix each have their own schema), so the script can branch on
real data rather than parsing prose.

## Install it as a plugin

This repo is a Claude Code plugin **marketplace** hosting one plugin, `tasks-folder`.

```text
/plugin marketplace add agile-bex/dynamic-workflows-demo
/plugin install tasks-folder@agile-bex
```

That's it — the `tasks-folder` workflow and its four skills are now available in
any Claude Code session.

### Local dev (no install)

To iterate on the plugin without installing it, launch Claude Code pointed straight
at the plugin directory:

```text
claude --plugin-dir ./tasks-folder
```

## Try it

This repo includes a sample `tasks/` board with three cards in `todo/` that form a
dependency chain — scaffold a Python project, build a todo-store module, then a
PySide6 app on top of it:

1. Install the plugin (above), or run with `--plugin-dir ./tasks-folder`.
2. Ask Claude to run the **`tasks-folder-workflow`** against the `tasks/` folder.
3. Watch it go with `/workflows`, and watch the cards move across the board (and
   the commits land) as each one is implemented, reviewed, and fixed.

The cards are deliberately interesting: one verifies via a background process, one
is gated on a passing pytest suite, and the GUI card is explicitly marked
*do not launch* — so you can see the workflow respect each card's verification rules
and its dependency order.

## Repo layout

```
dynamic-workflows-demo/
├── .claude-plugin/
│   └── marketplace.json        # marketplace manifest (lists the plugin)
├── tasks-folder/               # the plugin
│   ├── .claude-plugin/
│   │   └── plugin.json         # plugin manifest
│   ├── skills/                 # the four tasks-folder role skills
│   └── workflows/
│       └── tasks-folder-workflow.js
├── tasks/                      # sample board (not part of the plugin — just demo data)
│   └── todo/
├── README.md
└── LICENSE
```

Only `tasks-folder/` is the plugin; the `tasks/` board is sample content so the
repo documents itself.

## License

Use however, no attribution required.

```
BSD Zero Clause License (SPDX: 0BSD)

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.
```

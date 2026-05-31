export const meta = {
  name: 'tasks-folder-workflow',
  description:
    'Work the cards in a tasks/ folder: pick the next ready card, implement it, then loop reviewer → fixer until approved. Drives the tasks-folder-* skills; moves cards todo → doing → done/blocked.',
  phases: [{ title: 'Select' }, { title: 'Build' }],
}

// ---- Inputs -------------------------------------------------------------
// args (optional): path to the tasks/ root. Defaults to 'tasks'.
const TASKS_DIR = typeof args === 'string' && args.trim() ? args.trim() : 'tasks'
const MAX_ROUNDS = 3 // review→fix attempts per card
const MAX_CARDS = 25 // outer-loop safety bound

// ---- Schemas ------------------------------------------------------------
const PICK_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['next', 'remaining', 'reason'],
  properties: {
    next: { type: ['string', 'null'], description: 'slug of the next ready card, or null' },
    remaining: { type: 'integer', description: 'how many cards are still in todo/' },
    reason: { type: 'string' },
  },
}

const IMPLEMENT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['status', 'summary'],
  properties: {
    status: { type: 'string', enum: ['done', 'blocked'] },
    summary: { type: 'string' },
    blocker: { type: 'string', description: 'if blocked, the specific reason' },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['verdict', 'findings'],
  properties: {
    verdict: { type: 'string', enum: ['approved', 'changes_requested', 'blocked'] },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['severity', 'location', 'issue', 'fix'],
        properties: {
          severity: { type: 'string', enum: ['blocking', 'nit'] },
          location: { type: 'string' },
          issue: { type: 'string' },
          fix: { type: 'string' },
        },
      },
    },
    blocker: { type: 'string' },
  },
}

const FIX_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['status', 'summary'],
  properties: {
    status: { type: 'string', enum: ['done', 'blocked'] },
    summary: { type: 'string' },
    blocker: { type: 'string' },
  },
}

// ---- Prompts ------------------------------------------------------------
const TS = 'date +%Y-%m-%d_%H-%M-%S' // agents run this for the log timestamp

const pickPrompt = `
Select the next task card to work, for a project using the tasks-folder layout
(see the 'tasks-folder-layout' skill).

1. List the cards in '${TASKS_DIR}/todo/' and what's already in '${TASKS_DIR}/done/'.
2. Read the todo cards. Each states its dependencies in prose. Choose the next card
   whose stated prerequisites are ALL already in '${TASKS_DIR}/done/'. If several
   qualify, prefer the most foundational (the one that unblocks the most others).
Select only — modify nothing.

Return: 'next' = the chosen card's filename without '.md' (its slug), or null if none
is ready; 'remaining' = count of cards still in '${TASKS_DIR}/todo/'; 'reason' = one line.
`.trim()

const implementPrompt = (slug) => `
You are the IMPLEMENTER. Follow your 'tasks-folder-implementer' skill and the shared
'tasks-folder-layout' skill.

Card: ${TASKS_DIR}/todo/${slug}.md   (slug: ${slug})

- git mv the card from todo/ to doing/ — you're picking it up.
- Read the card, do homework against the real code, and build EXACTLY what it asks.
- Verify without ever blocking your shell: a server can be started in the background,
  curled, then stopped; a GUI event loop must NOT be launched (obey any "do not run"
  note). Use imports / tests / static checks where you can't safely run it.
- On a real mismatch: STOP — git mv the card to blocked/, explain in your log, return blocked.
- Commit your work. Leave the card in doing/ (the reviewer decides done).
- Write your log: ${TASKS_DIR}/logs/${slug}/<timestamp>_implementer.md  (timestamp via: ${TS})

Return your structured result.
`.trim()

const reviewPrompt = (slug, round) => `
You are the REVIEWER. Follow your 'tasks-folder-reviewer' skill and 'tasks-folder-layout'.
This is review round ${round} of at most ${MAX_ROUNDS}.

Card: ${TASKS_DIR}/doing/${slug}.md   (slug: ${slug})

- Review the latest commit's change and the real running result. You did NOT write this code.
- Judge two axes: did it do what the card asked (and only that), and is it sound.
- Mark each finding 'blocking' or 'nit'; be specific and actionable; do not pad.
- Approved (nothing blocking): git mv the card doing/ → done/ in your commit.
  Changes requested: leave it in doing/. Cannot review at all: git mv to blocked/.
- Write your review: ${TASKS_DIR}/logs/${slug}/<timestamp>_reviewer.md  (timestamp via: ${TS})

Return your structured result.
`.trim()

const fixPrompt = (slug, round, blocking) => `
You are the FIXER. Follow your 'tasks-folder-fixer' skill and 'tasks-folder-layout'.

Card: ${TASKS_DIR}/doing/${slug}.md   (slug: ${slug})
You do NOT have the reviewer's full standard — address ONLY these blocking findings:
${blocking.map((f, i) => `${i + 1}. [${f.location}] ${f.issue} — wanted: ${f.fix}`).join('\n')}

- Read the real code first. No gold-plating, no new features, no regressions.
- If a finding is wrong or impossible against the real code: STOP — git mv the card to
  blocked/, explain in your log, return blocked.
- Commit the fixes. Leave the card in doing/ for re-review.
- Write your log: ${TASKS_DIR}/logs/${slug}/<timestamp>_fixer.md  (timestamp via: ${TS})

Return your structured result.
`.trim()

// ---- Orchestration ------------------------------------------------------
const cards = []

for (let worked = 0; worked < MAX_CARDS; worked++) {
  // 1) pick the next ready card
  const pick = await agent(pickPrompt, { label: 'select', phase: 'Select', schema: PICK_SCHEMA })

  if (!pick.next) {
    if (pick.remaining > 0) {
      log(`No card is ready — ${pick.remaining} still in todo/ with unmet deps. ${pick.reason}`)
      return { stopped: 'stuck', remaining: pick.remaining, reason: pick.reason, cards }
    }
    log('todo/ is empty — all cards handled.')
    break
  }

  const slug = pick.next

  // 2) implement
  const impl = await agent(implementPrompt(slug), {
    label: `implement:${slug}`,
    phase: slug,
    schema: IMPLEMENT_SCHEMA,
  })
  if (impl.status === 'blocked') {
    log(`${slug}: blocked during implementation — ${impl.blocker || 'unknown'}`)
    cards.push({ slug, outcome: 'blocked', stage: 'implement', blocker: impl.blocker })
    return { stopped: 'blocked', slug, cards }
  }

  // 3) review → fix loop
  let approved = false
  const rounds = []
  for (let round = 1; round <= MAX_ROUNDS && !approved; round++) {
    const review = await agent(reviewPrompt(slug, round), {
      label: `review:${slug}#${round}`,
      phase: slug,
      schema: REVIEW_SCHEMA,
    })

    if (review.verdict === 'blocked') {
      log(`${slug}: reviewer blocked in round ${round} — ${review.blocker || 'unknown'}`)
      cards.push({ slug, outcome: 'blocked', stage: 'review', round, rounds })
      return { stopped: 'blocked', slug, cards }
    }

    if (review.verdict === 'approved') {
      approved = true
      rounds.push({ round, review })
      break
    }

    const blocking = review.findings.filter((f) => f.severity === 'blocking')
    const fix = await agent(fixPrompt(slug, round, blocking), {
      label: `fix:${slug}#${round}`,
      phase: slug,
      schema: FIX_SCHEMA,
    })
    rounds.push({ round, review, fix })

    if (fix.status === 'blocked') {
      log(`${slug}: fixer blocked in round ${round} — ${fix.blocker || 'unknown'}`)
      cards.push({ slug, outcome: 'blocked', stage: 'fix', round, rounds })
      return { stopped: 'blocked', slug, cards }
    }
  }

  if (!approved) {
    log(`${slug}: hit the ${MAX_ROUNDS}-round cap without approval — left in doing/.`)
    cards.push({ slug, outcome: 'capped', rounds: rounds.length })
    return { stopped: 'cap', slug, cards }
  }

  log(`${slug}: approved after ${rounds.length} round(s) → done/.`)
  cards.push({ slug, outcome: 'done', rounds: rounds.length })
}

return {
  completed: cards.filter((c) => c.outcome === 'done').length,
  cards,
}

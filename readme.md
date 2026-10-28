# Crushable Wingman

An agent skill that coaches you through texting and dating conversations — context first, no manipulation.

```bash
npx skills add yxp934/crushable-wingman-skill
```

Works with coding agents that support Agent Skills (it ships with an OpenAI Codex config in `agents/openai.yaml`).

## What it does

- **Reply coaching** — one recommended reply and why it's the best tradeoff, plus 3–5 alternatives, each labeled with its tone, why it works, and when *not* to use it. Then two follow-ups: one if they respond warmly, one if they go quiet.
- **Screenshot → transcript** — reads chat screenshots, extracts only the visible text, marks anything uncertain as `[unclear]`, and asks you to confirm the transcript before giving any advice.
- **Relationship analysis** — signals grounded in what you shared, 2–3 possible interpretations instead of one confident story, and one low-risk next step.
- **Date ideas** — 2–3 concrete plans with timing, budget, an invitation you can send, and a low-effort fallback.
- **Asks before guessing** — when key context is missing, it asks 2–4 short questions and explains why.

## Memory

Context is stored locally as plain Markdown, so you don't have to repeat yourself:

- a profile for you and for the person you're talking to,
- a short long-term snapshot per person (≤ 1,200 characters),
- append-only session logs that keep summaries, not full chat transcripts.

State lives in `~/.codex/state/crushable-wingman/` (override with `CRUSHABLE_WINGMAN_STATE_DIR`). `scripts/wingman_store.py` creates, reads and validates it.

## Ground rules

- Warm and direct. No manipulation tactics.
- Never helps with harassment, coercion, stalking, doxxing, impersonation or deception.
- When consent or boundaries are unclear, it defaults to respectful, direct communication.
- Replies in your language.

## Structure

```
SKILL.md                  workflow, rules and output formats
references/               intake interview, templates, reply rubric, screenshot checklist
scripts/wingman_store.py  local profile and memory store
agents/openai.yaml        Codex agent config
```

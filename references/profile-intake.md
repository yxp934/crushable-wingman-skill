# Profile Intake (Initialization + Reuse)

Use this only when local profiles are missing or incomplete, or when the user asks to update their stored info.

Goals:
- Fully cover the Crushable onboarding questionnaires for `user profile` and `crush profile`.
- Reuse stored answers to avoid asking the same questions again.
- Ask in small batches (2-4 questions per round).

Non-negotiable:
- Initialization is multi-turn. Keep going across turns until both profiles are complete.
- Do not stop early just because you can "already give advice". If the user needs urgent help, give a minimal safe answer, then return to intake.

## 0) Setup (Once Per Session)

Commands below assume you are running from the skill folder. If not, use the installed path:
`python ~/.codex/skills/crushable-wingman/scripts/wingman_store.py ...`

1. Ensure local store exists:
```bash
python scripts/wingman_store.py init
```

2. Determine the active target:
- Read `active_handle.txt` via:
```bash
python scripts/wingman_store.py crush get-active
```
- Confirm with the user: "We are focusing on <handle> (<name>) right?"
- If no active handle, ask the user to pick/create one:
  - Ask for `handle` (hyphen-case) and display `name`.
  - Create crush folder + templates:
```bash
python scripts/wingman_store.py crush init --handle <handle> --name "<Name>"
python scripts/wingman_store.py crush set-active --handle <handle>
```

## 1) Reuse Rule (Non-Negotiable)

Before asking any intake question:
1. Load the existing profile file.
2. If the field is already filled, do NOT ask again unless:
   - The user explicitly says it changed, or
   - The user says it was wrong, or
   - The user asks to "re-do my profile".

Helpful commands:
```bash
python scripts/wingman_store.py user show-profile
python scripts/wingman_store.py crush show-profile --handle <handle>
python scripts/wingman_store.py user missing
python scripts/wingman_store.py crush missing --handle <handle>
```

Completion check:
- Keep asking until BOTH of these commands print nothing:
```bash
python scripts/wingman_store.py user missing
python scripts/wingman_store.py crush missing --handle <handle>
```

Language:
- Ask the questions in the user's language.

## 2) User Profile Intake (Full Coverage)

Source: Crushable `profile-questionnaire` fields.

Write answers into `user/profile.md` using the template:
```bash
python scripts/wingman_store.py init
python scripts/wingman_store.py user show-profile
```

If you need to reset templates (rare):
```bash
python scripts/wingman_store.py user init --force
```

### Ask In Batches (Suggested)

Batch 1 (Basics)
- `user_name`: "What should I call you?"
- `user_pronouns`: "What are your pronouns? (she/her, he/him, they/them, other, prefer not to say)"
- `sexual_orientation`: "Who are you interested in? (men/women/everyone/other/prefer not to say)"

Batch 2 (Basics + Personality)
- `age_range`: "What is your age range? (16-18 / 19-24 / 25-30 / 31-35 / 36+ / prefer not to say)"
- `relationship_status`: "Current relationship status? (single / it's complicated / just vibing / talking to someone / other)"
- `social_energy`: "Where do you get your energy? (introvert / extrovert / ambivert)"

Batch 3 (Personality + Interests)
- `planning_style`: "How do you approach plans? (planner / spontaneous / flexible)"
- `confidence_level`: "How confident do you feel around crushes? (1-10, or `unknown`)"
- `date_preferences`: "What sounds like your ideal date? (coffee & deep talks / adventure & outdoors / movies & chill / dinner & atmosphere / other)"

Batch 4 (Interests + Dating Style)
- `hobbies`: "Pick your top interests (choose multiple)."
  - Store as a JSON array, e.g. `hobbies: [\"music\", \"travel\"]`
  - If they refuse: `hobbies: [\"prefer_not_to_say\"]`
- `approach_style`: "How would you describe your approach? (shy & subtle / bold & direct / playful & flirty / thoughtful & caring / other)"
- `pace`: "What is your preferred pace? (slow burn / steady / go for it / other)"

Batch 5 (Communication)
- `comm_method`: "How do you prefer to connect? (texting / in-person / calls / mixed)"
- `response_time`: "Your typical text response time? (instant / within an hour / a few hours / whenever I see it / strategic wait / other)"
- `emoji_user`: "Are you an emoji person? (`true` / `false` / `unknown`)"

Batch 6 (Boundaries)
- `comfort_sharing`: "How comfortable are you sharing feelings? (1-10, or `unknown`)"
- `pda_comfort`: "Public displays of affection? (love it / small gestures only / private person / depends)"
- `relationship_goal`: "What are you looking for? (serious relationship / see where it goes / casual and fun / still figuring it out)"

## 3) Crush Profile Intake (Full Coverage + Confidence)

Source: Crushable `crush-profile` fields.

Write answers into `crushes/<handle>/profile.md` using the template:
```bash
python scripts/wingman_store.py crush init --handle <handle> --name "<Name>"   # if missing
python scripts/wingman_store.py crush show-profile --handle <handle>
```

### Ask In Batches (Suggested)

Batch 1 (Basic)
- `name`: "What should we call them?"
- `nickname`: "Do you have a nickname for them? (optional)"
- `how_you_know_them`: "How do you know them? (coworkers / classmates / mutual friends / online / other)"

Batch 2 (Interests + confidence)
- `interests`: "What do they clearly enjoy? (pick a few; examples welcome)"
- `interests_confidence`: "How confident are you? (sure / guess / unknown)"

Batch 3 (Communication + confidence)
- `communication_style`: "How do they like to connect/communicate? (pick a few)"
- `communication_confidence`: "Confidence: sure / guess / unknown"

Batch 4 (Availability + confidence)
- `availability_pattern`: "When are they usually most available to meet or chat?"
- `availability_confidence`: "Confidence: sure / guess / unknown"

Batch 5 (Context)
- `relationship_context`: "Relationship context: just met / friends for a while / classmates / coworkers / online connection / mutual friends / other"
- `current_status`: "Where are things right now? (just crushing / we've talked / we hang out / there's tension / unclear signals / other)"

Batch 6 (Sensitive)
- `sensitive_topics`: "Any sensitive topics to avoid for now? (pick a few, or say none)"
  - Store as a JSON array, e.g. `sensitive_topics: [\"ex relationships\", \"politics\"]`
  - If none: `sensitive_topics: [\"none\"]`

Batch 7 (History)
- `last_meaningful_moment`: "What was the last meaningful moment between you two?"
- `last_contact_date`: "When did you last talk or meet? (YYYY-MM-DD or `unknown`)"

Batch 8 (Optional, fast)
- `dislikes`: "Any clear dislikes/turn-offs? (places/topics/activities)"
  - Store as a JSON array, e.g. `dislikes: [\"loud bars\", \"small talk\"]`
  - If none: `dislikes: [\"none\"]` (or `dislikes: [\"unknown\"]`)
- `best_contact_time`: "Do you know the best time to contact them? (or `unknown`)"
- `crush_gender`: "Their gender (if known), otherwise `unknown`."
- `pronouns`: "Their pronouns (if known), otherwise `unknown`."

## 4) Writeback And Validate

After each batch:
1. Update the profile file(s) (upsert the full Markdown).
2. Validate constraints (memory snapshots especially):
```bash
python scripts/wingman_store.py validate --handle <handle>
```

If the user says "I don't know / skip":
- Prefer filling the field with a clear sentinel (`unknown` or `prefer_not_to_say`) rather than leaving it blank.

# Screenshot Transcript Extraction (No Hallucinations)

Use when the user provides chat screenshots. Extract first, coach second.

## Rules

- Extract ONLY what is visible. Do not infer missing text.
- Preserve message order as shown in the screenshot(s).
- Keep punctuation and emojis as-is.
- Mark uncertain text as `[unclear]`.
- Identify Speaker using layout cues:
  - Right-aligned / colored bubble often means `Me`
  - Left-aligned / gray bubble often means `Other`
  - If uncertain, ask the user to confirm rather than guessing

## Output Template (Markdown Table)

Return a transcript like this:

| # | Speaker | Text | Time |
|---:|:--|:--|:--|
| 1 | Other | ... | 21:54 |
| 2 | Me | ... | 21:55 |

Notes:
- If time is not visible, leave it blank.
- If there are multiple screenshots, label them and continue numbering.

## Confirmation Step (Required)

After you output the transcript, ask the user:
- "Is speaker labeling correct (Me vs Other)?"
- "Anything missing or misread?"
- "Which message are we replying to (paste the row number)?"

Only after confirmation proceed to reply coaching or analysis.

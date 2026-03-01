# Lang Tutor

This repository is a base workspace for language learning.

Each language lives in its own folder, for example `german/`.

## Folder Structure

Each language folder is expected to follow this pattern:

```text
<language>/
  grammar/
    A1/ A2/ B1/ B2/ C1/
    daily-notes-YYYY-MM-DD.md
  vocab/
    A1/ A2/ B1/ B2/ C1/
    daily-notes-YYYY-MM-DD.md
  exercise/
    A1/ A2/ B1/ B2/ C1/
    daily/
      daily-exercises-YYYY-MM-DD.md
```

Dates use ISO format: `YYYY-MM-DD`.

## How To Work With Codex

This repo includes local skills under `.codex/skills/`.
Use them while collaborating with Codex in this repository.

Recommended flow:

1. Open or move into the language folder you want to work on, such as `german/`.
2. Ask Codex to use a skill by name, or describe the task clearly.
3. Let Codex read the matching daily notes and create or update the derived files.
4. Review the generated markdown and continue your study from there.

Best practice:

- Work from inside the language folder when using the language-specific skills.
- Mention the date if you want a date other than today.
- If you want an existing generated file replaced, explicitly say `regenerate` or `overwrite`.

## Existing Skills

### `create_daily_language_notes`

Purpose:
Create the day-matched note files in `grammar/` and `vocab/`.

What it does:

- Creates `grammar/daily-notes-YYYY-MM-DD.md`
- Creates `vocab/daily-notes-YYYY-MM-DD.md`
- Uses a fixed starter template
- Does not overwrite existing files

Current implementation:

- Skill definition: `.codex/skills/create_daily_language_notes/SKILL.md`
- Script used by the skill: `scripts/create-daily-language-notes.sh`

Example requests to Codex:

- `Use create_daily_language_notes in german.`
- `Create today's daily language notes in this folder.`
- `Create daily language notes for 2026-03-02.`

### `create_daily_language_exercises`

Purpose:
Create the day-matched exercise file in `exercise/daily/` using the matching daily grammar and vocab notes.

What it does:

- Reads `grammar/daily-notes-YYYY-MM-DD.md`
- Reads `vocab/daily-notes-YYYY-MM-DD.md`
- Uses AI to generate exercises
- Writes `exercise/daily/daily-exercises-YYYY-MM-DD.md`
- Does not overwrite existing files unless you explicitly ask

Exercise rules:

- It must cover all usable grammar points found in the grammar note.
- It must cover all usable vocabulary items or vocab contexts found in the vocab note.
- Every distinct study point must appear in at least one exercise prompt.
- If one source note is empty or missing, it uses the other and states that clearly.
- If both are empty or missing, it still creates a fallback exercise file and records that no study content was available.

Expected output sections:

- `Source Summary`
- `Exercise Basis`
- `Coverage Checklist`
- `Fill in the Blank`
- `Grammar Practice`

Current implementation:

- Skill definition: `.codex/skills/create_daily_language_exercises/SKILL.md`
- This is AI-assisted. It is not driven by a bash generator script.

Example requests to Codex:

- `Use create_daily_language_exercises here.`
- `Generate today's exercises from my daily notes.`
- `Regenerate the 2026-03-01 exercises after reading today's grammar and vocab notes.`

### `create_word_tree`

Purpose:
Read the daily vocab note and expand it into CEFR-split vocab files.

What it does:

- Reads `vocab/daily-notes-YYYY-MM-DD.md`
- Extracts all usable vocab entries
- Organizes entries by part of speech
- Expands entries with relevant grammar forms
- Verifies CEFR level through web search
- Writes dated vocab files into the correct CEFR folders

Expected outputs:

- `vocab/A1/vocab-A1-YYYY-MM-DD.md`
- `vocab/A2/vocab-A2-YYYY-MM-DD.md`
- `vocab/B1/vocab-B1-YYYY-MM-DD.md`
- `vocab/B2/vocab-B2-YYYY-MM-DD.md`
- `vocab/C1/vocab-C1-YYYY-MM-DD.md`
- or other level files when supported by the verified result

Important notes:

- This skill depends on web lookup for CEFR validation.
- It should not silently drop vocab items from the daily note.
- It should not overwrite existing target files unless you explicitly ask.

Current implementation:

- Skill definition: `.codex/skills/create_word_tree/SKILL.md`

Example requests to Codex:

- `Use create_word_tree for today's vocab note.`
- `Build the CEFR vocab files from this folder's daily vocab note.`

## Collaborative Workflow

A practical daily loop:

1. Use `create_daily_language_notes`.
2. Fill in the new grammar and vocab note files during study.
3. Use `create_daily_language_exercises` to generate exercises that cover all studied items.
4. Optionally use `create_word_tree` to classify vocab into CEFR files.
5. Review, answer, and refine the generated materials with Codex.

## Current Example

The current seeded language folder is `german/`.

Today’s example files for March 1, 2026:

- `german/grammar/daily-notes-2026-03-01.md`
- `german/vocab/daily-notes-2026-03-01.md`
- `german/exercise/daily/daily-exercises-2026-03-01.md`

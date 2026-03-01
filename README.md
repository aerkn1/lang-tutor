# Lang Tutor

This repository is a base workspace for language learning.

Each language lives in its own folder, for example `german/`.

## Folder Structure

Each language folder is expected to follow this pattern:

```text
<language>/
  grammar/
    A1/ A2/ B1/ B2/ C1/
      grammar-<LEVEL>.md
      daily/
        grammar-<LEVEL>-YYYY-MM-DD.md
    daily/
      daily-notes-YYYY-MM-DD.md
  vocab/
    A1/ A2/ B1/ B2/ C1/
      vocab-<LEVEL>.md
      daily/
        vocab-<LEVEL>-YYYY-MM-DD.md
    daily/
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
- Check `CHANGELOG.md` to review the daily history of skill activity.

## Centralized Log

The repository now uses a single root log file:

- `CHANGELOG.md`

All skills should write a short activity summary there when they run.

Log format:

- Entries are grouped under a date heading like `## 2026-03-01`
- Each log line records the time, skill name, language folder, and a short summary

Shared helper:

- `scripts/append-skill-log.sh`

This helper is the standard way to append new skill activity to the centralized log.

## Existing Skills

### `create_daily_language_notes`

Purpose:
Create the day-matched note files in `grammar/daily/` and `vocab/daily/`.

What it does:

- Creates `grammar/daily/daily-notes-YYYY-MM-DD.md`
- Creates `vocab/daily/daily-notes-YYYY-MM-DD.md`
- Uses a fixed starter template
- Does not overwrite existing files
- Appends a log summary to `CHANGELOG.md`

Current implementation:

- Skill definition: `.codex/skills/create_daily_language_notes/SKILL.md`
- Script used by the skill: `scripts/create-daily-language-notes.sh`
- Shared logger used by the script: `scripts/append-skill-log.sh`

Example requests to Codex:

- `Use create_daily_language_notes in german.`
- `Create today's daily language notes in this folder.`
- `Create daily language notes for 2026-03-02.`

### `create_daily_language_exercises`

Purpose:
Create the day-matched exercise file in `exercise/daily/` using the matching daily grammar and vocab notes.

What it does:

- Reads `grammar/daily/daily-notes-YYYY-MM-DD.md`
- Reads `vocab/daily/daily-notes-YYYY-MM-DD.md`
- Uses a helper script to prepare or skip the target file
- Uses AI to generate exercises
- Writes `exercise/daily/daily-exercises-YYYY-MM-DD.md`
- Does not overwrite existing files unless you explicitly ask
- Appends a log summary to `CHANGELOG.md`

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
- Helper script: `scripts/prepare-daily-language-exercises.sh`
- Shared logger used by the helper: `scripts/append-skill-log.sh`
- This is AI-assisted for exercise content, but script-assisted for path handling, file scaffolding, and logging.

Example requests to Codex:

- `Use create_daily_language_exercises here.`
- `Generate today's exercises from my daily notes.`
- `Regenerate the 2026-03-01 exercises after reading today's grammar and vocab notes.`

### `create_word_tree`

Purpose:
Read the daily vocab note, normalize it into a structured word-tree schema, and expand it into CEFR-split vocab files.

What it does:

- Reads `vocab/daily/daily-notes-YYYY-MM-DD.md`
- Rewrites the daily vocab note into a normalized master schema while preserving the raw capture
- Extracts all usable vocab entries
- Organizes entries by part of speech
- Expands entries with relevant grammar forms
- Verifies CEFR level through web search
- Writes dated vocab files into `daily/` inside the correct CEFR folders
- Updates the cumulative vocab file for each CEFR level when new words are added
- Should append a log summary to `CHANGELOG.md`

Expected outputs:

- `vocab/A1/daily/vocab-A1-YYYY-MM-DD.md`
- `vocab/A2/daily/vocab-A2-YYYY-MM-DD.md`
- `vocab/B1/daily/vocab-B1-YYYY-MM-DD.md`
- `vocab/B2/daily/vocab-B2-YYYY-MM-DD.md`
- `vocab/C1/daily/vocab-C1-YYYY-MM-DD.md`
- `vocab/A1/vocab-A1.md`
- `vocab/A2/vocab-A2.md`
- `vocab/B1/vocab-B1.md`
- `vocab/B2/vocab-B2.md`
- `vocab/C1/vocab-C1.md`
- or other level files when supported by the verified result

Important notes:

- This skill depends on web lookup for CEFR validation.
- The daily vocab note becomes the master normalized source after the skill runs.
- It should not silently drop vocab items from the daily note.
- It should not overwrite existing target files unless you explicitly ask.

Current implementation:

- Skill definition: `.codex/skills/create_word_tree/SKILL.md`
- It should use `scripts/append-skill-log.sh` after each run.

Example requests to Codex:

- `Use create_word_tree for today's vocab note.`
- `Build the CEFR vocab files from this folder's daily vocab note.`

### `create_grammar_tree`

Purpose:
Read the daily grammar note, normalize it into a structured grammar-tree schema, and expand it into CEFR-split grammar files.

What it does:

- Reads `grammar/daily/daily-notes-YYYY-MM-DD.md`
- Rewrites the daily grammar note into a normalized master schema while preserving the raw capture
- Extracts all usable grammar topics, rules, and patterns
- Organizes entries by grammar domain
- Expands entries with relevant rule summaries, forms, and examples
- Verifies CEFR level through web search
- Writes dated grammar files into `daily/` inside the correct CEFR folders
- Updates the cumulative grammar file for each CEFR level when new topics are added
- Should append a log summary to `CHANGELOG.md`

Expected outputs:

- `grammar/A1/daily/grammar-A1-YYYY-MM-DD.md`
- `grammar/A2/daily/grammar-A2-YYYY-MM-DD.md`
- `grammar/B1/daily/grammar-B1-YYYY-MM-DD.md`
- `grammar/B2/daily/grammar-B2-YYYY-MM-DD.md`
- `grammar/C1/daily/grammar-C1-YYYY-MM-DD.md`
- `grammar/A1/grammar-A1.md`
- `grammar/A2/grammar-A2.md`
- `grammar/B1/grammar-B1.md`
- `grammar/B2/grammar-B2.md`
- `grammar/C1/grammar-C1.md`
- or other level files when supported by the verified result

Important notes:

- This skill depends on web lookup for CEFR validation.
- The daily grammar note becomes the master normalized source after the skill runs.
- It should not silently drop grammar points from the daily note.
- It should not overwrite existing dated target files unless you explicitly ask.

Current implementation:

- Skill definition: `.codex/skills/create_grammar_tree/SKILL.md`
- It should use `scripts/append-skill-log.sh` after each run.

Example requests to Codex:

- `Use create_grammar_tree for today's grammar note.`
- `Build the CEFR grammar files from this folder's daily grammar note.`

## Collaborative Workflow

A practical daily loop:

1. Use `create_daily_language_notes`.
2. Fill in the new grammar and vocab note files during study.
3. Optionally use `create_grammar_tree` to classify grammar into CEFR files.
4. Optionally use `create_word_tree` to classify vocab into CEFR files.
5. Use `create_daily_language_exercises` to generate exercises that cover all studied items.
6. Review, answer, and refine the generated materials with Codex.

## Current Example

The current seeded language folder is `german/`.

Today’s example files for March 1, 2026:

- `german/grammar/daily/daily-notes-2026-03-01.md`
- `german/vocab/daily/daily-notes-2026-03-01.md`
- `german/exercise/daily/daily-exercises-2026-03-01.md`

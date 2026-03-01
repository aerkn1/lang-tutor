---
name: create_daily_language_exercises
description: Generate a dated exercise markdown file in exercise/daily for the current language folder by reading the matching daily grammar and vocab notes. Use this when the user wants AI-generated fill-in-the-blank and grammar exercises based on grammar/daily/daily-notes-YYYY-MM-DD.md and vocab/daily/daily-notes-YYYY-MM-DD.md while working inside a language folder such as german.
---

# Create Daily Language Exercises

Use this skill when the current working directory is a language folder such as `german`.

## Workflow

1. Determine the target date.
   Default to today using `date +%F` unless the user names a specific date.
2. Run the helper script from the language folder:
   `../scripts/prepare-daily-language-exercises.sh [--force] [YYYY-MM-DD]`
3. Read the script output. It reports:
   - action: `create`, `regenerate`, or `skip`
   - source file paths
   - source file status for grammar and vocab
   - target exercise path
4. If the action is `skip`, do not overwrite the existing file unless the user explicitly asked to regenerate it.
5. If the action is `create` or `regenerate`, read:
   `grammar/daily/daily-notes-YYYY-MM-DD.md`
   `vocab/daily/daily-notes-YYYY-MM-DD.md`
6. Replace the scaffolded placeholders in `exercise/daily/daily-exercises-YYYY-MM-DD.md` with the final AI-generated exercise content.
7. The helper script already appends the centralized log entry to `../CHANGELOG.md`.

## Coverage Rules

- Cover all usable grammar points from the grammar note.
- Cover all usable vocabulary items or vocab contexts from the vocab note.
- Every distinct study point found in the daily notes must appear in at least one exercise prompt.
- If both notes have content, use both. Do not ignore one source.
- If one note is empty or missing, generate the exercises from the other note and explicitly state which source was empty or missing and which study file was used.
- If both notes are empty or missing, still create the exercise file with fallback prompts and a clear note that no study content was available.

## Output Structure

The exercise file must include:

- `Source Summary`
- `Exercise Basis`
- `Coverage Checklist`
- `Fill in the Blank`
- `Grammar Practice`

## Generation Rules

- Write exercises that are specific to the study material; do not just copy the notes verbatim.
- Prefer 4 to 6 fill-in-the-blank items and 4 to 6 grammar prompts when the note content is modest.
- If there are more study points than that, expand the exercise count so every point is covered.
- Keep the output practical and learner-focused.
- If the note content is sparse, infer simple exercises from the available material rather than failing.
- The helper script logs the target date, action, target path, and source note statuses automatically.

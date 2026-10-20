---
name: create-lesson
description: Start a language lesson with linked raw notes, study notes, exercises, and review. Replaces create_daily_language_notes; supports multiple sessions on the same date.
---

# Create a lesson

Work from the repository root. Use `--language` for the selected language, defaulting to `german`. Read `docs/workflow.md` for the lesson layout.

- Use the user's date, topic, level, and duration where supplied. Otherwise use today, a short topic inferred from their request, `UNKNOWN`, and 15 minutes.
- Run `python3 scripts/tutor.py --language german create-lesson --topic "..."`. Optional flags: `--date YYYY-MM-DD --level A2 --minutes 15`.
- Keep the returned lesson ID throughout the session. A new command creates a new session; use `--id` with the same settings to retry a specific creation safely.
- Put the user's supplied words, questions, and notes into this lesson's `raw-notes.md`, preserving their wording. Generated explanations belong in entry records and exercises.
- Show the lesson folder and raw-notes link. Do not claim exercises or learning outcomes exist merely because the files were scaffolded.

If continuing an existing lesson, use its ID and existing files. Do not create a new lesson just because the date changed.

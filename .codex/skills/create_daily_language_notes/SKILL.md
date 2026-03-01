---
name: create_daily_language_notes
description: Create a new dated markdown note in both grammar/daily and vocab/daily for the current language folder. Use this when the user wants daily note files like grammar/daily/daily-notes-YYYY-MM-DD.md and vocab/daily/daily-notes-YYYY-MM-DD.md.
---

# Create Daily Language Notes

Use this skill when the current working directory is a language folder such as `german`.

## Workflow

1. Confirm the current directory contains `grammar/` and `vocab/`.
2. Run `../scripts/create-daily-language-notes.sh`.
3. Report which files were created and which already existed.
4. The script appends a centralized log entry to `../CHANGELOG.md` automatically.

## Notes

- Pass an optional `YYYY-MM-DD` argument when the user asks for a specific date.
- The script creates `grammar/daily/` and `vocab/daily/` if they do not exist yet.
- If a dated note file already exists, the script leaves it unchanged.
- Every run logs the outcome to the root `CHANGELOG.md`.

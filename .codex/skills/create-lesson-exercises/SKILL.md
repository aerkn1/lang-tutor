---
name: create-lesson-exercises
description: Generate bounded, scenario-based German practice for a lesson using its vocabulary, grammar, and prior mistakes. Replaces create_daily_language_exercises.
---

# Generate lesson exercises

Read `docs/workflow.md` and the exercise payload contract in `docs/data-contract.md`.

1. Resolve the lesson ID. Read `lesson.md`, `raw-notes.md`, `study-notes.md`, and existing `exercises.md`. Read relevant review history. If no structured material exists, extract the useful vocabulary/grammar first using the repository's extraction skills.
2. Choose one practical objective and a small set of entries that fit the lesson's duration. For a 15-minute session, 5–8 vocabulary entries is a starting point. Mix recent captures and review needs where useful. `tutor.py select --limit 8` suggests candidates; topic/CEFR filters are optional and strict. Inspect each selected entry.
3. Build a coherent sequence: short contextual example or dialogue, retrieval prompts, a speaking/writing task, then corrections. Match the learner's level; target CEFR is a teaching constraint, while individual words can span levels.
4. Include a coverage list naming selected IDs and their exercises. List deferred captured items for a later session. Provide an answer key in a collapsed `<details>` section, allowing alternatives where appropriate. Check prompts and answers for consistency and natural German.
5. Prepare JSON with `lesson_id`, `vocabulary_ids`, `grammar_ids`, and Markdown `content`. Run `tutor.py publish-exercises --file ... --expected-revision <current revision>`. Existing nonempty exercises should be regenerated only when the user requests revision/regeneration or the current task authorizes it; do not overwrite work incidentally during extraction.
6. Run `validate` and `rebuild --check`. Report the scenario, estimated duration, selected items, and deferred items.

Put answers and feedback in review events, never in a generated exercise file. Do not mark any item learned because it appeared in a prompt. Imported historical exercises are references and may need corrections before reuse.

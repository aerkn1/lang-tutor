# Working in Lang Tutor

This repository stores language lessons and canonical vocabulary/grammar as Markdown.
Use the repository skills in `.agents/skills/`; their commands run from this root.

- Read `docs/workflow.md` for the study loop and `docs/data-contract.md` for mutations.
- Raw lesson notes are user-authored source evidence. Extraction preserves them.
- Use `scripts/tutor.py` for entry upserts, exercise publishing, and review events.
  These operations validate identities, revisions, references, and source quotes.
- `study-notes.md`, `review.md`, and `indexes/` are generated views; rebuild them.
- Entries remain in `vocabulary/` or `grammar/` when CEFR metadata changes.
- Existing `german/vocab/`, `german/exercise/`, and nested CEFR/daily files under
  `german/grammar/` are historical sources, not current write targets.
- Never infer practice or mastery from generated content. Evidence status is
  separate from CEFR level; imported claims are not current verification.
- For code changes run `python3 -m unittest discover -s tests -v`,
  `python3 scripts/tutor.py validate`, and `python3 scripts/tutor.py rebuild --check`.
- For content-only changes run the last two commands. Linguistic correctness
  still requires reviewing the relevant language content and its sources.
- Git workflow: pull before a session; validate, commit, and push afterward when
  requested or authorized. Do not resolve conflicting raw notes or answers by
  discarding one side. See `docs/workflow.md` for generated-file conflicts.

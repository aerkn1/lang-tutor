# Lesson workflow

Use Cursor or VS Code to open this repository. No extra notes application is needed.

```text
german/
  lessons/
    lesson-YYYY-MM-DD-<unique-suffix>/
      lesson.md         Objective, topic, target CEFR, duration
      raw-notes.md      Your original session notes
      study-notes.md    Generated links to vocabulary and grammar
      exercises.md      Generated exercises and selected entry IDs
      review.md         Generated view of actual practice
      reviews/
        <event-id>.json Persistent answers and feedback
  vocabulary/
    v-<uuid>.md         Reusable word meaning or expression
  grammar/
    g-<uuid>.md         Reusable grammar explanation
  indexes/
    cefr/               Generated A1–C2 and UNKNOWN views
    topics/index.md     Generated topic view
```

## A session

1. Pull the repository before starting on either Mac.
2. Use `create-lesson` or continue an existing lesson ID.
3. Write rough notes, new words, questions, and examples in `raw-notes.md`.
   Apple Notes content can be pasted into any appropriate lesson at any time.
4. Use `extract-vocabulary` and `extract-grammar` as relevant. They preserve captures,
   find existing records, attach source quotes, and update structured material.
5. Use `create-lesson-exercises` for one practical scenario within the time budget.
   A large capture can supply several sessions; defer unselected items explicitly.
6. Attempt the exercises or a real conversation. Use `review-lesson` to record
   actual answers and corrections, optionally with a chosen next review date.
7. Validate, commit, and push before switching Macs.

Example requests:

- "Start a 15-minute A2 lesson about making a doctor's appointment."
- "Extract vocabulary from lesson-2026-10-20-01 and keep my raw notes."
- "I saw this expression again; add this lesson as another encounter."
- "Prepare five new expressions and three review expressions for this lesson."
- "Check my answer and save the correction under this lesson."

Grammar and vocabulary entry bodies carry reusable explanations, examples,
uncertainties, and citations. Study notes link to them rather than maintaining
editable copies. The lesson's raw notes preserve its own context. A word can occur
in many lessons and CEFR changes do not change its ID.

The teaching loop is encounter → understand → retrieve → reuse. Choose practical
situations, as in the companion `deutsch-in-motion` learning framework. This
repository implements the records and tools; the skills guide teaching decisions.

## Two Macs

Clone this repository outside cloud-synced folders on each Mac. Open the same
working branch on both. Git sync is explicit; local uncommitted changes do not
appear on the other machine.

At the beginning:

```sh
git status
git pull --ff-only
```

At the end, inspect the diff and stage the intended files:

```sh
python3 scripts/tutor.py validate
python3 scripts/tutor.py rebuild --check
git diff
git add german/
git commit -m "Study: appointment lesson and review"
git push
```

If both Macs have diverged, `--ff-only` stops instead of choosing a merge strategy
for you. Fetch and reconcile both sets of changes. Preserve both raw captures and
review events. For conflicting entry edits, reconcile meanings, forms, evidence,
and source lists, then increment the entry revision. Independently created duplicate
entries require choosing one ID and updating references before removing the duplicate.

Generated CEFR/topic indexes, `study-notes.md`, and `review.md` can be rebuilt after
canonical conflicts are resolved. They do not carry unique user input.
Run `validate` and `rebuild` after reconciliation. Do not force-push to bypass conflicts.

## Existing March 1 material

The old daily notes and CEFR glossaries remain at their original paths as historical
sources. `scripts/migrate_legacy.py` imports their original capture sections into
`lessons/lesson-2026-03-01-01/`, with 45 vocabulary drafts and six grammar drafts.
The historical exercise set is preserved, and no practice outcomes are invented.

`migration.json` records the original source hashes and counts. The migration can
be rerun safely after completion: it checks source hashes and validates existing
data, but does not replay old content over subsequent edits.

The old normalized source sometimes grouped several meanings. Those combinations
are retained and explicitly marked for sense/language review rather than silently
splitting them based on missing context. Likewise, inherited CEFR claims have
`estimated` status until precise evidence is checked and recorded.

Old generation skills and shell scaffolding have been replaced:

| Previous skill | Current skill |
| --- | --- |
| `create_daily_language_notes` | `create-lesson` |
| `create_word_tree` | `extract-vocabulary` |
| `create_grammar_tree` | `extract-grammar` |
| `create_daily_language_exercises` | `create-lesson-exercises` |
| — | `review-lesson` |

`CHANGELOG.md` preserves the old generation history. Current changes are tracked
in Git; practice is tracked in lesson review events. Skill runs do not fabricate
entries in the practice history.

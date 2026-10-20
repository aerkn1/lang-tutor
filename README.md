# Lang Tutor

A lesson workspace for learning German with an LLM, edited in Cursor or VS Code
and synchronized between Macs with Git.

**One lesson ID connects raw notes, structured vocabulary and grammar, exercises,
and actual practice.** Vocabulary and grammar records are reusable across lessons.
CEFR and topic glossaries are generated views of those records.

## Start a lesson

Python 3.9 or later is sufficient; no packages or external service are required
for the local commands. The assistant supplies teaching content and uses the web
when checking external language/CEFR evidence.

```sh
python3 scripts/tutor.py create-lesson --topic "Making an appointment" --level A2 --minutes 15
```

Open the returned lesson folder. Write freely in `raw-notes.md`, then ask the
assistant to extract vocabulary and prepare a short practical lesson.

Repository skills:

| Skill | Purpose |
| --- | --- |
| `create-lesson` | Start or continue a session with a stable lesson ID |
| `extract-vocabulary` | Turn raw captures into sourced vocabulary records |
| `extract-grammar` | Turn grammar questions into reusable explanations |
| `create-lesson-exercises` | Select a bounded set and generate practical exercises |
| `review-lesson` | Save actual answers, feedback, and review needs |

See [the study workflow and two-Mac setup](docs/workflow.md) and
[the data and tool contract](docs/data-contract.md).

## Browse

- [Migrated March 1 lesson](german/lessons/lesson-2026-03-01-01/lesson.md)
- [Its original notes](german/lessons/lesson-2026-03-01-01/raw-notes.md)
- [Its structured study notes](german/lessons/lesson-2026-03-01-01/study-notes.md)
- CEFR: [A1](german/indexes/cefr/A1.md) · [A2](german/indexes/cefr/A2.md) ·
  [B1](german/indexes/cefr/B1.md) · [B2](german/indexes/cefr/B2.md) ·
  [C1](german/indexes/cefr/C1.md) · [C2](german/indexes/cefr/C2.md) ·
  [Unknown](german/indexes/cefr/UNKNOWN.md)
- [Topics](german/indexes/topics/index.md)

The migrated entries are drafts from the old generated material. Their CEFR labels
are estimates pending precise evidence; their linguistic content has not been
revalidated by the migration.

## Local tools

```sh
python3 scripts/tutor.py search anrufen
python3 scripts/tutor.py select --limit 8
python3 scripts/tutor.py validate
python3 scripts/tutor.py rebuild --check
python3 -m unittest discover -s tests -v
```

The CLI also exposes `get`, `upsert`, `publish-exercises`, and `record-review` as
structured JSON operations. An MCP adapter can call the same operations later;
no MCP server or automatic review scheduler is currently included.

Generated material is not evidence of completed learning. The skills guide the
assistant; the commands enforce record and update rules, not linguistic truth.

# Data and command contract

All commands run from the repository root with Python 3.9+ and no external packages.
They accept `--language german` before the command and return JSON on stdout
(errors on stderr with nonzero exit status). `--root` selects an isolated repository
for tests. This is a local tool interface; an MCP server is not included.

Markdown records use a JSON object between `---` delimiters. JSON is valid YAML,
but these tools deliberately accept only JSON frontmatter. Rich text follows
the closing delimiter. Cursor and VS Code can read these files directly.
Use the commands for canonical mutations so validation and revision checks run.

## Entry identity and updates

Vocabulary identity: `(lemma, part_of_speech, sense)`, normalized to Unicode NFC,
case-folded, with whitespace collapsed. Grammar identity: `(topic, domain)`.
IDs are opaque `v-<uuid hex>` or `g-<uuid hex>` and never depend on CEFR or filename labels.

Search first, then get the matching record. An upsert without an ID matches an
exact identity or creates a new ID. Existing lemmas/aliases with different meanings
require inspecting candidates and explicitly using `--allow-new-sense`. This flag
does not allow duplicate identities. Matching is deterministic; semantic equivalence
and genuine polysemy still require the assistant's judgment.

```sh
python3 scripts/tutor.py search anrufen --kind vocabulary
python3 scripts/tutor.py get v-0123456789abcdef0123456789abcdef
python3 scripts/tutor.py upsert --file /tmp/entry.json
python3 scripts/tutor.py upsert --file /tmp/update.json --expected-revision 1
```

IDs below are illustrative; use actual returned IDs. Example creation payload:

```json
{
  "kind": "vocabulary",
  "lemma": "anrufen",
  "part_of_speech": "verb",
  "sense": "to phone someone",
  "forms": {"present": "ruft an", "past": "rief an", "perfect": "hat angerufen"},
  "aliases": ["rufe an"],
  "topics": ["appointments"],
  "cefr": {"level": "UNKNOWN", "status": "unknown", "note": "Not assessed yet."},
  "sources": [
    {"lesson_id": "lesson-2026-10-20-01", "quote": "Ich rufe morgen beim Arzt an."}
  ],
  "content": "# anrufen\n\n## Example\n\nIch rufe morgen beim Arzt an.\n"
}
```

The lesson and exact quote must already exist in its `raw-notes.md`. Sources are
encounter evidence; a source quote does not certify a generated translation or rule.
Every entry requires at least one source. Entry `content` holds explanations,
examples, uncertainties, and reference links.

Updates need `kind`, `id`, and changed fields. `aliases`, `topics`, and `sources`
merge without duplicates. `forms` merges by key; supplied keys replace old values.
`cefr` and `content` replace their previous values when supplied, so read them first.
Other omitted fields are preserved. An identical retry is a no-op. A real change
requires the current revision; stale revisions fail without overwriting the entry.
Commands serialize access locally with a file lock and replace individual files
atomically. Multi-file updates are not distributed transactions. If interrupted,
validate canonical records and run `rebuild`; Git conflicts still need resolving.
Unsupported payload fields are rejected rather than silently ignored.

`created_at`, `updated_at`, and `revision` are tool-managed. Review history lives
outside entry records. List removal/merging entries is intentionally not automated;
reconcile such changes explicitly, preserve source references, and validate afterward.

Grammar payloads use `kind: grammar`, `topic`, and `domain` instead of `lemma`,
`part_of_speech`, and `sense`. Shared fields have the same meaning:

```json
{
  "kind": "grammar",
  "topic": "Dative after helfen",
  "domain": "cases",
  "topics": ["helping"],
  "sources": [{"lesson_id": "lesson-2026-10-20-01", "quote": "helfen + Dativ?"}],
  "content": "# Dative after helfen\n\nIch helfe meinem Freund.\n"
}
```

## CEFR evidence

Allowed levels: A1, A2, B1, B2, C1, C2, UNKNOWN.

- `unknown`: requires level UNKNOWN.
- `estimated`: retained for legacy assignments and grammar estimates; explain it in `note`. The vocabulary skill does not create new estimates.
- `verified`: known level plus `source_url`, `locator`, and `checked_at` (ISO date).

The tools validate the presence/format of evidence, not whether a web source
actually supports the claim. The extracting assistant must inspect it.
Assign evidence to the relevant meaning; a source that lists a word does not
necessarily support every meaning. Reuse valid stored evidence rather than
performing the same search on every encounter.

The [vocabulary skill](../.agents/skills/extract-vocabulary/SKILL.md#trusted-cefr-sources)
uses the official Goethe A1/A2/B1 word lists as its approved CEFR source set.
It checks the relevant meaning, records the actual PDF URL/page/entry/check date,
and leaves unsupported new assignments UNKNOWN. An unlisted word is not evidence
of B2/C1/C2. Verification means inclusion in the cited exam list; it does not prove
that this is the word's universal minimum level. Existing migrated estimates remain
historical until rechecked. This source policy is enforced by skill instructions;
the CLI validates metadata structure and does not fetch or authenticate web evidence.

## Lessons and exercise publishing

```sh
python3 scripts/tutor.py create-lesson --topic "Making an appointment" --level A2 --minutes 15
python3 scripts/tutor.py create-lesson --date 2026-10-20 --id lesson-2026-10-20-01 --topic "Making an appointment"
python3 scripts/tutor.py select --topic appointments --limit 8
```

An explicit existing ID with the same settings returns unchanged; different settings
fail. Multiple sessions per day are supported. `lesson.md` contains metadata and the
learner's objective. `raw-notes.md` is free-form; append new material rather than
rewriting already-cited passages. Source validation will flag removed quotations.

Selection returns up to the requested limit. Filters are strict: fewer matches
yield fewer items. Due reviews and unscheduled difficulties come first, then unseen
entries, then reuse. An explicit future `next_review` defers an entry. `--level A2`
means exactly A2. Selection is a simple queue, not a spaced repetition scheduler.

Publish generated exercises using this JSON shape:

```json
{
  "lesson_id": "lesson-2026-10-20-01",
  "vocabulary_ids": ["v-0123456789abcdef0123456789abcdef"],
  "grammar_ids": [],
  "content": "# Making an appointment\n\n## Retrieval\n\n...\n\n<details>\n<summary>Answer key</summary>\n\n...\n</details>\n"
}
```

```sh
python3 scripts/tutor.py publish-exercises --file /tmp/exercises.json --expected-revision 0
```

The initial scaffold has revision 0. Read `exercises.md` before changing an existing
set; use its current revision. References must exist and have the correct kind.
Existing vocabulary from other lessons can be selected without inventing new
raw-note quotations. It appears in the current lesson's generated study notes.
Only `exercises.md` and generated views change; raw notes, objectives, and answers
are preserved. Generated exercises remain draft language content requiring review.

## Practice records

Create a UUID hex event ID once (for example, `python3 -c 'import uuid; print(uuid.uuid4().hex)'`)
and reuse it on retry. Record the learner's actual attempt:

```json
{
  "event_id": "abcdef0123456789abcdef0123456789",
  "lesson_id": "lesson-2026-10-20-01",
  "entry_id": "v-0123456789abcdef0123456789abcdef",
  "result": "hard",
  "answer": "Ich anrufe den Arzt.",
  "feedback": "Use the separable verb: Ich rufe den Arzt an.",
  "next_review": "2026-10-22"
}
```

```sh
python3 scripts/tutor.py record-review --file /tmp/review.json
```

Results: `again`, `hard`, `good`, `easy`. `next_review` is optional and explicit.
Events are stored under the lesson's `reviews/<event_id>.json`; identical retries
do not duplicate them. Reusing an ID for different content or another lesson fails.
`review.md` is rebuilt from these events. Amend an assessment with a new event
explaining the correction; never silently replace the original answer.

## Validation and recovery

```sh
python3 scripts/tutor.py validate
python3 scripts/tutor.py rebuild
python3 scripts/tutor.py rebuild --check
python3 -m unittest discover -s tests -v
```

Validation checks record shapes, identities, source quotations, references, and
review IDs. It does not establish linguistic correctness, verify external CEFR
sources, or prove the learner knows a word. Rebuild writes only generated indexes,
study notes, and review summaries. The `--check` variant fails if those views are stale.

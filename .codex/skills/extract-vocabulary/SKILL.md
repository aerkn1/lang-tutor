---
name: extract-vocabulary
description: Extract German vocabulary and expressions from a lesson's raw notes, update reusable vocabulary entries with source quotes, and rebuild CEFR indexes. Replaces create_word_tree.
---

# Extract vocabulary from a lesson

Read `docs/workflow.md` and `docs/data-contract.md`. Use the explicit lesson ID or the lesson established in this session; if neither identifies a lesson, ask which lesson to use.

1. Read `lessons/<lesson-id>/raw-notes.md` in the selected language. Extract each usable word or expression, keeping source quotes verbatim. Skip headings, template guidance, and administrative text. Identify ambiguous notes or questions instead of inventing meanings.
2. Search existing records using `python3 scripts/tutor.py search "..." --kind vocabulary`. Read possible matches with `get <id>`. Match lemma, part of speech, and meaning together; check aliases and original captures. A repeated encounter adds a source to an existing entry. Preserve distinct meanings.
3. Prepare a JSON upsert payload using the contract. Use a noun's lemma without its article and put the article/plural in `forms`; retain real German characters. Include helpful grammar forms and short, natural examples in `content`. Mark uncertain language details in prose; do not fabricate forms.
4. For CEFR, use a source that explicitly supports the relevant word or meaning. Record URL, location/evidence, and check date for `verified`. Use `estimated` for a teaching estimate and `UNKNOWN` / `unknown` if no defensible estimate is available. Do not upgrade imported legacy claims without checking evidence. Keep cached supported evidence unless the meaning or evidence changes.
5. Upsert each entry with `--file <payload.json>`. For a change to an existing record, include its ID and the revision returned by `get` via `--expected-revision`. On conflict, reread and reconcile. Use `--allow-new-sense` only after inspecting the reported candidates and deciding the meaning is distinct.
6. Run `validate` and `rebuild --check`. Report entries created, updated, unchanged, and notes requiring clarification. Account for all usable vocabulary captures even if some remain unresolved.

The command validates quotes and updates generated study notes and indexes. Never rewrite raw notes during extraction, hand-edit generated indexes, or replace practice results. Do not force every new capture into the day's exercise set.

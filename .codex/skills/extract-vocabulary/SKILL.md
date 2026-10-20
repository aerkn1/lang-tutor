---
name: extract-vocabulary
description: Extract German vocabulary and expressions from a lesson's raw notes, update reusable vocabulary entries with source quotes, and check CEFR against official Goethe word lists. Replaces create_word_tree.
---

# Extract vocabulary from a lesson

Read `docs/workflow.md` and `docs/data-contract.md`. Use the explicit lesson ID or the lesson established in this session; if neither identifies a lesson, ask which lesson to use.

1. Read `lessons/<lesson-id>/raw-notes.md` in the selected language. Extract each usable word or expression, keeping source quotes verbatim. Skip headings, template guidance, and administrative text. Identify ambiguous notes or questions instead of inventing meanings.
2. Search existing records using `python3 scripts/tutor.py search "..." --kind vocabulary`. Read possible matches with `get <id>`. Match lemma, part of speech, and meaning together; check aliases and original captures. A repeated encounter adds a source to an existing entry. Preserve distinct meanings.
3. Prepare a JSON upsert payload using the contract. Use a noun's lemma without its article and put the article/plural in `forms`; retain real German characters. Include helpful grammar forms and short, natural examples in `content`. Mark uncertain language details in prose; do not fabricate forms.
4. Check CEFR using the official Goethe sources and matching rules below. A supported match is `verified`; an unsupported new assignment is `UNKNOWN` / `unknown`. Do not generate new teaching estimates for vocabulary. Existing migrated estimates require an actual lookup before being upgraded; preserve an old estimate in the note if a completed recheck leaves the level unknown.
5. Upsert each entry with `--file <payload.json>`. For a change to an existing record, include its ID and the revision returned by `get` via `--expected-revision`. On conflict, reread and reconcile. Use `--allow-new-sense` only after inspecting the reported candidates and deciding the meaning is distinct.
6. Run `validate` and `rebuild --check`. Report entries created, updated, unchanged, and notes requiring clarification. Account for all usable vocabulary captures even if some remain unresolved.

The command validates quotes and updates generated study notes and indexes. Never rewrite raw notes during extraction, hand-edit generated indexes, or replace practice results. Do not force every new capture into the day's exercise set.


## Trusted CEFR sources

Use Goethe-Institut's official exam vocabulary lists as the approved source set for German vocabulary. Links checked on 2026-10-20:

| Level | Official word list | Publisher page for finding an updated link |
| --- | --- | --- |
| A1 | [Start Deutsch 1 word list](https://www.goethe.de/pro/relaunch/prf/de/A1_SD1_Wortliste_02.pdf) | [A1 exam preparation](https://www.goethe.de/de/spr/prf/ueb/pa1.html) |
| A2 | [Goethe-Zertifikat A2 word list](https://www.goethe.de/pro/relaunch/prf/de/Goethe-Zertifikat_A2_Wortliste.pdf) | [A2 exam preparation](https://www.goethe.de/de/spr/prf/ueb/pa2.html) |
| B1 | [Goethe-Zertifikat B1 word list](https://www.goethe.de/pro/relaunch/prf/de/Goethe-Zertifikat_B1_Wortliste.pdf) | [B1 exam preparation](https://www.goethe.de/de/spr/prf/ueb/pb1.html) |

### Lookup and evidence rules

- Open the actual official document and inspect the entry and its context. Search snippets, mirrors, memory, generated glossaries, and an incidental occurrence in an example are insufficient evidence. Check both thematic word groups and the alphabetical entries.
- Normalize inflected captures to the lemma while retaining their original form. Match the relevant meaning, separability/reflexivity, and expression. Do not assign every meaning of a word the level of one supported use. An absent compound or idiom cannot inherit its components' level automatically.
- Check A1, then A2, then B1; stop at the first supported match for that meaning. Interpret the stored level as the lowest supported match in this checked source set, not a universal minimum CEFR level. If a lower list could not be checked, record that limitation and do not claim it was absent there.
- For `verified`, store the actual PDF URL in `cefr.source_url`, the PDF page number (1-based), headword or thematic group, and a short description of the matched use in `cefr.locator`, and the actual inspection date in `cefr.checked_at`. Use `cefr.note` to identify the document title/edition where available and explain that the evidence establishes inclusion in that exam list. Paraphrase evidence and write original teaching examples.
- If no relevant entry supports the meaning, set `level: UNKNOWN`, `status: unknown`, and describe which lists were checked in `note`. Do not infer B2/C1/C2 from absence, rarity, complexity, or a general dictionary definition. This approved source set covers A1–B1; higher-level assignments require an explicitly approved additional CEFR source.
- If a PDF moves, follow its publisher page. If access fails, report the lookup as unavailable rather than claiming the word is absent. New entries remain unknown; retain existing evidenced values and explain the failed refresh.
- Reuse an existing Goethe citation only when it identifies the matching use and meets these evidence requirements. Keep its original check date unless the source is actually reopened. Never upgrade a legacy mention of Goethe without locating its evidence.
- Other dictionary sources may support spelling, meanings, and grammatical forms when needed; cite them in the entry body. They do not replace the approved CEFR source set. Grammar-topic classification follows the separate grammar skill.

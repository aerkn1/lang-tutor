---
name: create_word_tree
description: Build CEFR-split word tree markdown files from the dated daily vocab note in the current language folder. Use this when the user wants to read `vocab/daily/daily-notes-YYYY-MM-DD.md`, organize every vocab item by part of speech, expand each item with usable grammar details, verify CEFR level through web search, rewrite the daily vocab note into the normalized word-tree schema, write dated `vocab-CEFR-YYYY-MM-DD.md` files inside per-level `daily/` folders, and update the cumulative CEFR vocab files.
---

# Create Word Tree

Use this skill when the current working directory is a language folder such as `german`.

## Workflow

1. Determine the target date.
   Default to today using `date +%F` unless the user names a specific date.
2. Confirm the current directory contains `vocab/`.
3. Read the source note:
   `vocab/daily/daily-notes-YYYY-MM-DD.md`
4. Treat the source as empty when it is missing or when it only contains headings, blank lines, or placeholder lines such as `-`.
5. Extract every usable vocab item from the file. Treat each non-empty study line, bullet, numbered item, inline comma-separated item, or short phrase as a candidate entry.
6. Normalize each entry into a readable lemma:
   keep the original German form, remove list markers, and preserve short fixed phrases when the source note uses a phrase instead of a single word.
7. Classify each entry into the best-fit part of speech:
   noun, verb, adjective, adverb, pronoun, conjunction, preposition, article, phrase, or other.
8. Add the correct article first whenever the entry is a noun and the article can be stated or reliably inferred.
9. Expand each entry with grammar details that actually exist for that type:
   verbs: `ich`, `du`, `er/sie/es`, `wir`, `ihr`, `sie/Sie`, plus simple past and past participle (`v2-v3` style forms)
   nouns and noun phrases: singular and plural when available, plus nominative, accusative, and dative article or declension forms when applicable
   adjectives or similar inflected words: nominative, accusative, and dative forms only when they are genuinely useful and reliable
   non-inflected items: do not invent conjugations or declensions
10. Prefer accuracy over completeness. If a form is uncertain, omit it and note that it was not confidently derived.
11. Verify the CEFR level for each entry with web search before assigning a level.
12. Normalize CEFR levels to `A1`, `A2`, `B1`, `B2`, `C1`, or `C2`.
13. If no source clearly provides a CEFR level, place the item in `UNKNOWN` and state that the level could not be verified.
14. Rewrite the source note at `vocab/daily/daily-notes-YYYY-MM-DD.md` into the normalized master schema after analysis.
15. The rewritten daily note must preserve the original captured items in a `Raw Capture` section, then add a `Normalized Word Tree` section that groups every normalized entry by part of speech.
16. In the rewritten daily note, each entry should include:
   - normalized lemma or phrase
   - original source form when normalization changed it
   - meaning
   - grammar forms that apply
   - provisional or verified CEFR level
   - daily CEFR file path
   - cumulative CEFR file path
17. Group entries by CEFR level and create one dated file per level at:
   `vocab/<CEFR>/daily/vocab-<CEFR>-YYYY-MM-DD.md`
18. Update the cumulative CEFR file for each level at:
   `vocab/<CEFR>/vocab-<CEFR>.md`
19. If a dated target file already exists, do not overwrite it unless the user explicitly asks to regenerate it.
20. When updating the cumulative CEFR file, add only new words for that level. Do not duplicate entries that are already present.
21. After creating, regenerating, or skipping output files, append a summary entry to `../CHANGELOG.md` by running:
   `../scripts/append-skill-log.sh "create_word_tree" "<language>" "<summary>"`

## CEFR Lookup Rules

- Use web search for each entry because CEFR labels are source-dependent and can change across dictionaries.
- Prefer dictionary or language-learning sources that explicitly publish CEFR labels.
- If multiple sources disagree, choose the level supported by the strongest explicit source and briefly note the ambiguity.
- Make it clear when a CEFR level is inferred from partial evidence rather than directly labeled by the source.

## Output Structure

Each generated dated CEFR file must include:

- A title with the CEFR level and date
- `Source Note`
- `Level Summary`
- One section per part of speech present in that file

Each cumulative CEFR file must include:

- A title with the CEFR level
- `Level Summary`
- `Source Files`
- One section per part of speech present in that level

Each vocab entry should be rendered as a compact, readable block that includes:

- the main word or phrase
- article first, if applicable
- part of speech
- the grammar forms that apply
- a short CEFR note with the source or confidence

The rewritten daily note must include:

- the original title with the date
- `Raw Capture`
- `Normalized Word Tree`
- one section per part of speech present in the source

## Generation Rules

- Cover every usable vocab item from the source note. Do not silently drop entries.
- Cover every usable vocab item in both the rewritten daily note and the CEFR-split files.
- Keep the per-day CEFR files under `vocab/<CEFR>/daily/`.
- Keep the cumulative CEFR files at `vocab/<CEFR>/vocab-<CEFR>.md`.
- When a new item belongs to a level, update both the per-day file and the cumulative file for that level.
- Keep entries grouped by part of speech inside each CEFR file.
- Keep entries grouped by part of speech inside the rewritten daily note as well.
- Preserve the original source wording when the note contains a phrase, but still classify it as precisely as possible.
- Do not fabricate forms that are not valid for the entry type.
- When the source note is empty or missing, report that clearly and do not create misleading vocab files or a misleading normalized rewrite.
- The changelog summary should include the target date, the source note path, whether the daily note was rewritten, and which CEFR files were created, regenerated, or skipped.

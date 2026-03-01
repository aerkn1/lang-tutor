---
name: create_word_tree
description: Build CEFR-split word tree markdown files from the dated daily vocab note in the current language folder. Use this when the user wants to read `vocab/daily-notes-YYYY-MM-DD.md`, organize every vocab item by part of speech, expand each item with usable grammar details, verify CEFR level through web search, and write `vocab-CEFR-YYYY-MM-DD.md` files inside per-level vocab folders.
---

# Create Word Tree

Use this skill when the current working directory is a language folder such as `german`.

## Workflow

1. Determine the target date.
   Default to today using `date +%F` unless the user names a specific date.
2. Confirm the current directory contains `vocab/`.
3. Read the source note:
   `vocab/daily-notes-YYYY-MM-DD.md`
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
14. Group entries by CEFR level and create one file per level at:
   `vocab/<CEFR>/vocab-<CEFR>-YYYY-MM-DD.md`
15. If a target file already exists, do not overwrite it unless the user explicitly asks to regenerate it.

## CEFR Lookup Rules

- Use web search for each entry because CEFR labels are source-dependent and can change across dictionaries.
- Prefer dictionary or language-learning sources that explicitly publish CEFR labels.
- If multiple sources disagree, choose the level supported by the strongest explicit source and briefly note the ambiguity.
- Make it clear when a CEFR level is inferred from partial evidence rather than directly labeled by the source.

## Output Structure

Each generated CEFR file must include:

- A title with the CEFR level and date
- `Source Note`
- `Level Summary`
- One section per part of speech present in that file

Each vocab entry should be rendered as a compact, readable block that includes:

- the main word or phrase
- article first, if applicable
- part of speech
- the grammar forms that apply
- a short CEFR note with the source or confidence

## Generation Rules

- Cover every usable vocab item from the source note. Do not silently drop entries.
- Keep entries grouped by part of speech inside each CEFR file.
- Preserve the original source wording when the note contains a phrase, but still classify it as precisely as possible.
- Do not fabricate forms that are not valid for the entry type.
- When the source note is empty or missing, report that clearly and do not create misleading vocab files.

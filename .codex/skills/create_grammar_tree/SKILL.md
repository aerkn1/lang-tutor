---
name: create_grammar_tree
description: Build CEFR-split grammar tree markdown files from the dated daily grammar note in the current language folder. Use this when the user wants to read `grammar/daily/daily-notes-YYYY-MM-DD.md`, reorganize the covered grammar topics into normalized rule entries, verify CEFR level through web search, rewrite the daily grammar note into the normalized grammar-tree schema, write dated `grammar-CEFR-YYYY-MM-DD.md` files inside per-level `daily/` folders, and update the cumulative CEFR grammar files.
---

# Create Grammar Tree

Use this skill when the current working directory is a language folder such as `german`.

## Workflow

1. Determine the target date.
   Default to today using `date +%F` unless the user names a specific date.
2. Confirm the current directory contains `grammar/`.
3. Read the source note:
   `grammar/daily/daily-notes-YYYY-MM-DD.md`
4. Treat the source as empty when it is missing or when it only contains headings, blank lines, or placeholder lines such as `-`.
5. Extract every usable grammar topic, rule, pattern, example, or explicit question from the file. Treat each non-empty study line, bullet, numbered item, heading item, or short rule statement as a candidate entry.
6. Normalize each entry into a concise grammar topic label:
   preserve the original study intent, remove list markers, and keep short fixed grammar labels when the source note already uses them.
7. Classify each entry into the best-fit grammar domain:
   word order, verb tense, verb forms, modal verbs, separable verbs, cases, articles, prepositions, pronouns, adjective endings, negation, conjunctions, clauses, question forms, or other.
8. Expand each entry with learning details that are genuinely supported by the source or by reliable inference:
   a short rule summary, core pattern or form, one short example, and a common pitfall only when it is clearly useful and reliable.
9. Prefer accuracy over completeness. If a rule detail is uncertain, omit it and note that it was not confidently derived.
10. Verify the CEFR level for each entry with web search before assigning a level.
11. Normalize CEFR levels to `A1`, `A2`, `B1`, `B2`, `C1`, or `C2`.
12. If no source clearly supports a CEFR level, place the item in `UNKNOWN` and state that the level could not be verified.
13. Rewrite the source note at `grammar/daily/daily-notes-YYYY-MM-DD.md` into the normalized master schema after analysis.
14. The rewritten daily note must preserve the original captured material in a `Raw Capture` section, then add a `Normalized Grammar Tree` section that groups every normalized entry by grammar domain.
15. In the rewritten daily note, each entry should include:
   - normalized topic label
   - original source form when normalization changed it
   - rule summary
   - core pattern, form, or trigger words when applicable
   - example when available
   - provisional or verified CEFR level
   - daily CEFR file path
   - cumulative CEFR file path
16. Group entries by CEFR level and create one dated file per level at:
   `grammar/<CEFR>/daily/grammar-<CEFR>-YYYY-MM-DD.md`
17. Update the cumulative CEFR file for each level at:
   `grammar/<CEFR>/grammar-<CEFR>.md`
18. If a dated target file already exists, do not overwrite it unless the user explicitly asks to regenerate it.
19. When updating the cumulative CEFR file, add only new normalized topics for that level. Do not duplicate entries that are already present.
20. After creating, regenerating, or skipping output files, append a summary entry to `../CHANGELOG.md` by running:
   `../scripts/append-skill-log.sh "create_grammar_tree" "<language>" "<summary>"`

## CEFR Lookup Rules

- Use web search for each grammar topic because level labels are source-dependent and can vary across teaching frameworks.
- Prefer grammar syllabi, curriculum guides, or language-learning sources that explicitly publish CEFR-tagged grammar coverage.
- If multiple sources disagree, choose the level supported by the strongest explicit source and briefly note the ambiguity.
- Make it clear when a CEFR level is inferred from partial evidence rather than directly labeled by the source.

## Output Structure

Each generated dated CEFR file must include:

- A title with the CEFR level and date
- `Source Note`
- `Level Summary`
- One section per grammar domain present in that file

Each cumulative CEFR file must include:

- A title with the CEFR level
- `Level Summary`
- `Source Files`
- One section per grammar domain present in that level

Each grammar entry should be rendered as a compact, readable block that includes:

- the topic label
- the grammar domain
- a short rule summary
- the relevant pattern or forms
- a short example when useful
- a short CEFR note with the source or confidence

The rewritten daily note must include:

- the original title with the date
- `Raw Capture`
- `Normalized Grammar Tree`
- one section per grammar domain present in the source

## Generation Rules

- Cover every usable grammar point from the source note. Do not silently drop entries.
- Cover every usable grammar point in both the rewritten daily note and the CEFR-split files.
- Keep the per-day CEFR files under `grammar/<CEFR>/daily/`.
- Keep the cumulative CEFR files at `grammar/<CEFR>/grammar-<CEFR>.md`.
- When a new topic belongs to a level, update both the per-day file and the cumulative file for that level.
- Keep entries grouped by grammar domain inside each CEFR file.
- Keep entries grouped by grammar domain inside the rewritten daily note as well.
- Preserve the original source wording when the note contains a named grammar topic, but still normalize it into a clean topic label.
- Do not fabricate rule details or examples that are not valid for the topic.
- When the source note is empty or missing, report that clearly and do not create misleading grammar files or a misleading normalized rewrite.
- The changelog summary should include the target date, the source note path, whether the daily note was rewritten, and which CEFR files were created, regenerated, updated, or skipped.

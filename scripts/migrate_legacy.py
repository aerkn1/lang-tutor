#!/usr/bin/env python3
"""Import the repository's 2026-03-01 example without altering the source files."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid

from tutor import ROOT, Store, atomic_write, document, normalized, require

LESSON = "lesson-2026-03-01-01"
NAMESPACE = uuid.UUID("01f793b9-1e45-47d7-ab0e-153f241973d3")


def raw_section(source):
    return source.split("## Raw Capture\n", 1)[1].split("\n## Normalized", 1)[0].strip("\n")


def blocks(source):
    group = None
    title = None
    fields = {}
    for line in (source + "\n### END").splitlines():
        if line.startswith("### "):
            if title:
                yield group, title, fields
            group, title, fields = line[4:], None, {}
        elif line.startswith("#### "):
            if title:
                yield group, title, fields
            title, fields = line[5:], {}
        elif title and line.startswith("- ") and ": " in line:
            key, value = line[2:].split(": ", 1)
            fields[key] = value


def entry_id(kind, title):
    return ("v-" if kind == "vocabulary" else "g-") + uuid.uuid5(NAMESPACE, kind + ":" + title).hex


def migrate(root):
    store = Store(root, "german")
    base = store.base
    originals = {
        "vocab": base / "vocab/daily/daily-notes-2026-03-01.md",
        "grammar": base / "grammar/daily/daily-notes-2026-03-01.md",
        "exercises": base / "exercise/daily/daily-exercises-2026-03-01.md",
    }
    sources = {k: p.read_text(encoding="utf-8") for k, p in originals.items()}
    hashes = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest() for p in originals.values()}
    manifest = store.lesson_dir(LESSON) / "migration.json"
    if manifest.exists():
        previous = json.loads(manifest.read_text(encoding="utf-8"))
        require(previous["source_sha256"] == hashes, "Legacy sources changed; review before remigration")
        # Never replay old values over edits to an already migrated lesson.
        store.validate()
        store.rebuild(check=True)
        return {"action": "already_migrated", **previous}
    require(not store.lesson_dir(LESSON).exists(), "Migration lesson already exists without a completed manifest")
    vocab_raw = raw_section(sources["vocab"])
    grammar_raw = raw_section(sources["grammar"])
    vocab_blocks = list(blocks(sources["vocab"]))
    grammar_blocks = list(blocks(sources["grammar"]))
    raw_words = [line[2:] for line in vocab_raw.splitlines() if line.startswith("- ")]
    raw_lookup = {normalized(w): w for w in raw_words}
    source_alias = {"schluessel": "schlüssel"}
    pos = {"Nouns": "noun", "Verbs": "verb", "Adjectives": "adjective", "Adverbs": "adverb",
           "Prepositions": "preposition", "Phrases": "phrase", "Conjunctions": "conjunction"}
    require(all(group in pos for group, _, _ in vocab_blocks), "Unknown legacy part of speech")
    vocab_payloads = []
    used = set()
    for group, title, fields in vocab_blocks:
        captured = fields["Source form"].strip("`")
        captured = source_alias.get(captured, captured)
        quote = raw_lookup[normalized(captured)]
        used.add(quote)
        lemma = re.sub(r"^(der|die|das) ", "", title) if group == "Nouns" else title
        lemma = {"Schluessel": "Schlüssel", "ausserdem": "außerdem"}.get(lemma, lemma)
        reserved = {"Source form", "Meaning", "CEFR", "CEFR note", "Daily target file", "Cumulative target file"}
        vocab_payloads.append({
            "id": entry_id("vocabulary", title), "kind": "vocabulary",
            "lemma": lemma, "part_of_speech": pos[group], "sense": fields["Meaning"],
            "aliases": list(dict.fromkeys([quote, title])),
            "forms": {k: v for k, v in fields.items() if k not in reserved},
            "topics": ["legacy-march-2026"],
            "cefr": {"level": fields["CEFR"], "status": "estimated",
                     "note": "Imported legacy assignment; no precise source citation was saved. " + fields.get("CEFR note", "")},
            "sources": [{"lesson_id": LESSON, "quote": quote}],
            "content": f"# {lemma}\n\nImported draft from the March 1 lesson. Forms and combined meanings are preserved from the legacy source and need language/sense review before being treated as checked. Distinct uses can be separated deliberately after reviewing context.\n\n## Original source\n\n[Legacy normalized note](../vocab/daily/daily-notes-2026-03-01.md)\n",
        })
    require(used == set(raw_words), "Migration would omit raw vocabulary")
    # These map the six legacy explanations to the original raw blocks, not to
    # the occasionally rewritten 'Source form' values in the normalized note.
    grammar_chunks = re.split(r"\n(?=- )", grammar_raw)
    require(len(grammar_chunks) == len(grammar_blocks), "Unexpected grammar capture structure")
    grammar_payloads = []
    for (domain, title, fields), quote in zip(grammar_blocks, grammar_chunks):
        grammar_payloads.append({
            "id": entry_id("grammar", title), "kind": "grammar", "topic": title, "domain": domain,
            "topics": ["legacy-march-2026"], "forms": {"pattern": fields["Core pattern"]},
            "cefr": {"level": fields["CEFR"], "status": "estimated",
                     "note": "Imported legacy assignment; no precise source citation was saved. " + fields.get("CEFR note", "")},
            "sources": [{"lesson_id": LESSON, "quote": quote}],
            "content": f"# {title}\n\nImported draft; linguistic and CEFR claims have not been reverified during migration.\n\n{fields['Rule summary']}\n\n## Pattern\n\n{fields['Core pattern']}\n\n## Example\n\n{fields.get('Example', '')}\n\n[Legacy normalized note](../grammar/daily/daily-notes-2026-03-01.md)\n",
        })
    with store.lock():
        store.validate()
        store.create_lesson("2026-03-01", "Travel, everyday vocabulary, and destinations", "UNKNOWN", 15, LESSON)
        folder = store.lesson_dir(LESSON)
        atomic_write(folder / "raw-notes.md",
                     f"# Raw notes — {LESSON}\n\nImported original capture sections, with wording preserved.\n\n## Vocabulary\n\n{vocab_raw}\n\n## Grammar\n\n{grammar_raw}\n")
        metadata, _ = store.lesson(LESSON)
        atomic_write(folder / "lesson.md", document(metadata,
                     "# March 1 historical lesson\n\nThe original notes, grammar explanations, and exercises were imported together. Target CEFR and actual lesson duration were not recorded; UNKNOWN and 15 minutes are planning defaults, not historical measurements.\n\n[Study notes](study-notes.md) · [Raw notes](raw-notes.md) · [Exercises](exercises.md) · [Review](review.md)\n\nThe legacy files remain available at their original paths. Imported vocabulary may bundle meanings; inspect context before splitting these drafts. CEFR assignments are estimates until supported by a precise source.\n"))
        for payload in vocab_payloads + grammar_payloads:
            store.upsert(payload, allow_new_sense=True)
        store.publish_exercises({
            "lesson_id": LESSON, "vocabulary_ids": [p["id"] for p in vocab_payloads],
            "grammar_ids": [p["id"] for p in grammar_payloads],
            "content": "# Historical exercise set\n\nPreserved from the previous workflow for reference; not newly generated or linguistically revalidated. This set covers the whole capture and is longer than a new 15-minute lesson should be. No completed practice is inferred.\n\n" + sources["exercises"],
        }, 0)
        require(all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p.relative_to(base))] for p in originals.values()), "Legacy source changed during migration")
        report = {"lesson_id": LESSON, "vocabulary_entries": len(vocab_payloads),
                  "grammar_entries": len(grammar_payloads), "raw_vocabulary_items": len(raw_words),
                  "source_sha256": hashes}
        atomic_write(manifest, json.dumps(report, indent=2) + "\n")
        store.rebuild(check=True)
        return {"action": "migrated", **report}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(migrate(args.root), ensure_ascii=False, indent=2))

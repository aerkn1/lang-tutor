#!/usr/bin/env python3
"""Lesson and vocabulary tools. Python 3.9+, standard library only."""
import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
import uuid

ROOT = Path(__file__).resolve().parents[1]
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2", "UNKNOWN")
RESULTS = ("again", "hard", "good", "easy")
KINDS = ("vocabulary", "grammar")
ID_PATTERN = re.compile(r"^[vg]-[0-9a-f]{32}$")
LESSON_PATTERN = re.compile(r"^lesson-\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{0,63}$")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be non-empty text")
    return value


def date(value):
    require(isinstance(value, str), "Date must be YYYY-MM-DD")
    require(dt.date.fromisoformat(value).isoformat() == value, "Date must be YYYY-MM-DD")
    return value


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".tutor-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def document(metadata, body):
    # JSON is valid YAML. Restricting frontmatter to JSON avoids a YAML dependency.
    return "---\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n---\n\n" + body.rstrip() + "\n"


def read_document(path):
    raw = path.read_text(encoding="utf-8")
    require(raw.startswith("---\n") and "\n---\n" in raw[4:], f"Invalid frontmatter: {path}")
    header, body = raw[4:].split("\n---\n", 1)
    metadata = json.loads(header)
    require(isinstance(metadata, dict), f"Expected metadata object: {path}")
    return metadata, body.lstrip("\n")


def unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def md(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("[", "\\[").replace("]", "\\]")


def read_json(path):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    require(isinstance(value, dict), "Input must be a JSON object")
    return value


class Store:
    def __init__(self, root, language):
        require(re.fullmatch(r"[a-z][a-z0-9-]*", language), "Invalid language folder")
        self.root = Path(root).resolve()
        self.base = self.root / language
        require(self.base.is_dir(), f"Language folder does not exist: {self.base}")

    @contextlib.contextmanager
    def lock(self):
        with (self.base / ".tutor.lock").open("a") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            yield

    def lesson_dir(self, lesson_id):
        require(isinstance(lesson_id, str) and LESSON_PATTERN.fullmatch(lesson_id), "Invalid lesson ID")
        date(lesson_id[7:17])
        return self.base / "lessons" / lesson_id

    def lesson(self, lesson_id):
        folder = self.lesson_dir(lesson_id)
        metadata, body = read_document(folder / "lesson.md")
        require(metadata.get("id") == lesson_id, f"Lesson ID mismatch: {lesson_id}")
        require(metadata.get("date") == lesson_id[7:17], f"Lesson date mismatch: {lesson_id}")
        require(metadata.get("target_cefr") in LEVELS, "Invalid lesson CEFR")
        require(type(metadata.get("minutes")) is int and metadata["minutes"] > 0, "Invalid lesson duration")
        text(metadata.get("topic"), "Lesson topic")
        require((folder / "raw-notes.md").is_file(), f"Missing raw notes: {lesson_id}")
        return metadata, body

    def lessons(self):
        result = []
        for folder in sorted((self.base / "lessons").glob("*")):
            if folder.is_dir():
                result.append(self.lesson(folder.name)[0])
        return result

    def create_lesson(self, lesson_date, topic, level="UNKNOWN", minutes=15, lesson_id=None):
        date(lesson_date)
        text(topic, "Topic")
        require(level in LEVELS and type(minutes) is int and minutes > 0, "Invalid level or duration")
        lesson_id = lesson_id or f"lesson-{lesson_date}-{uuid.uuid4().hex[:12]}"
        require(lesson_id[7:17] == lesson_date, "Lesson ID must contain the lesson date")
        folder = self.lesson_dir(lesson_id)
        if folder.exists():
            existing, _ = self.lesson(lesson_id)
            require(
                (existing["topic"], existing["target_cefr"], existing["minutes"]) == (topic, level, minutes),
                "Lesson already exists with different settings",
            )
            return {"action": "unchanged", "lesson_id": lesson_id}
        folder.mkdir(parents=True)
        metadata = {"id": lesson_id, "date": lesson_date, "topic": topic, "target_cefr": level, "minutes": minutes}
        atomic_write(folder / "lesson.md", document(metadata, f"# {topic}\n\n## Objective\n\nDescribe what you want to be able to do in German.\n"))
        atomic_write(folder / "raw-notes.md", f"# Raw notes — {lesson_id}\n\nWrite freely here. Keep your original words, questions, and examples.\n")
        atomic_write(folder / "exercises.md", document(
            {"lesson_id": lesson_id, "revision": 0, "vocabulary_ids": [], "grammar_ids": []},
            "# Exercises\n\nNo exercises have been generated for this lesson yet.",
        ))
        self.rebuild()
        return {"action": "created", "lesson_id": lesson_id, "path": str(folder)}

    def entry_path(self, entry_id):
        require(isinstance(entry_id, str) and ID_PATTERN.fullmatch(entry_id), "Invalid entry ID")
        kind = "vocabulary" if entry_id.startswith("v-") else "grammar"
        return self.base / kind / (entry_id + ".md")

    def entries(self):
        result = []
        for kind in KINDS:
            for path in sorted((self.base / kind).glob("*.md")):
                metadata, content = read_document(path)
                require(path == self.entry_path(metadata.get("id")), f"Entry filename mismatch: {path}")
                require(metadata.get("kind") == kind, f"Entry kind mismatch: {path}")
                self.validate_entry(metadata)
                result.append({**metadata, "content": content})
        return result

    def get(self, entry_id):
        metadata, content = read_document(self.entry_path(entry_id))
        require(metadata.get("id") == entry_id, "Entry ID mismatch")
        self.validate_entry(metadata)
        return {**metadata, "content": content}

    def identity(self, entry):
        keys = ("lemma", "part_of_speech", "sense") if entry["kind"] == "vocabulary" else ("topic", "domain")
        return (entry["kind"],) + tuple(normalized(entry[key]) for key in keys)

    def validate_entry(self, entry):
        require(entry.get("kind") in KINDS, "Invalid entry kind")
        expected = "v-" if entry["kind"] == "vocabulary" else "g-"
        require(ID_PATTERN.fullmatch(entry.get("id", "")) and entry["id"].startswith(expected), "ID and kind mismatch")
        require(type(entry.get("revision")) is int and entry["revision"] >= 1, "Invalid revision")
        fields = ("lemma", "part_of_speech", "sense") if entry["kind"] == "vocabulary" else ("topic", "domain")
        for field in fields:
            text(entry.get(field), field)
        require(isinstance(entry.get("forms"), dict), "forms must be an object")
        require(all(isinstance(k, str) and isinstance(v, str) for k, v in entry["forms"].items()), "forms must contain text values")
        for field in ("aliases", "topics"):
            require(isinstance(entry.get(field), list), f"{field} must be an array")
            for item in entry[field]:
                text(item, field)
        cefr = entry.get("cefr")
        require(isinstance(cefr, dict), "cefr must be an object")
        require(set(cefr) <= {"level", "status", "source_url", "locator", "checked_at", "note"}, "Unknown CEFR field")
        require(cefr.get("level") in LEVELS, "Invalid CEFR level")
        require(cefr.get("status") in ("unknown", "estimated", "verified"), "Invalid CEFR evidence status")
        require((cefr["level"] == "UNKNOWN") == (cefr["status"] == "unknown"), "UNKNOWN requires unknown status; known levels require estimated or verified")
        for key, value in cefr.items():
            require(isinstance(value, str), f"CEFR {key} must be text")
        if cefr["status"] == "verified":
            require(re.match(r"^https?://[^/\s]+", cefr.get("source_url", "")), "Verified CEFR requires source_url")
            text(cefr.get("locator"), "Source locator / evidence")
            date(cefr.get("checked_at"))
        sources = entry.get("sources")
        require(isinstance(sources, list) and sources, "At least one raw-note source is required")
        for source in sources:
            require(isinstance(source, dict) and set(source) == {"lesson_id", "quote"}, "Source requires lesson_id and quote")
            self.lesson(source["lesson_id"])
            quote = text(source["quote"], "Source quote")
            raw = (self.lesson_dir(source["lesson_id"]) / "raw-notes.md").read_text(encoding="utf-8")
            require(quote in raw, f"Source quote is absent from {source['lesson_id']}: {quote!r}")
        for field in ("created_at", "updated_at"):
            dt.datetime.fromisoformat(text(entry.get(field), field))

    def upsert(self, patch, expected_revision=None, allow_new_sense=False):
        allowed = {"id", "kind", "lemma", "part_of_speech", "sense", "topic", "domain",
                   "forms", "aliases", "topics", "cefr", "sources", "content"}
        require(set(patch) <= allowed, f"Unknown entry fields: {set(patch) - allowed}")
        require(patch.get("kind") in KINDS, "kind is required")
        all_entries = self.entries()
        existing = None
        if patch.get("id"):
            path = self.entry_path(patch["id"])
            existing = self.get(patch["id"]) if path.exists() else None
        else:
            keys = ("lemma", "part_of_speech", "sense") if patch["kind"] == "vocabulary" else ("topic", "domain")
            for key in keys:
                text(patch.get(key), key)
            matches = [e for e in all_entries if self.identity(e) == self.identity(patch)]
            require(len(matches) <= 1, "Duplicate identities exist; resolve them before upserting")
            existing = matches[0] if matches else None
        timestamp = now()
        if existing:
            require(existing["kind"] == patch["kind"], "Cannot change entry kind")
            merged = {**existing, **patch, "id": existing["id"]}
        else:
            require(expected_revision in (None, 0), "Expected revision supplied for an absent entry")
            prefix = "v-" if patch["kind"] == "vocabulary" else "g-"
            merged = {
                "id": prefix + uuid.uuid4().hex, "revision": 1, "forms": {}, "aliases": [], "topics": [],
                "cefr": {"level": "UNKNOWN", "status": "unknown"}, "sources": [], "content": "",
                "created_at": timestamp, "updated_at": timestamp, **patch,
            }
        for field in ("sources", "aliases", "topics"):
            if field in patch:
                require(isinstance(patch[field], list), f"{field} must be an array")
                merged[field] = unique((existing or {}).get(field, []) + patch[field])
        if "forms" in patch:
            require(isinstance(patch["forms"], dict), "forms must be an object")
            merged["forms"] = {**(existing or {}).get("forms", {}), **patch["forms"]}
        require(isinstance(merged["content"], str), "content must be text")
        merged["content"] = merged["content"].strip()
        if merged["content"]:
            merged["content"] += "\n"
        self.validate_entry(merged)
        identity = self.identity(merged)
        others = [e for e in all_entries if e["id"] != merged["id"]]
        require(not any(self.identity(e) == identity for e in others), "Another entry already has this identity")
        if not existing and merged["kind"] == "vocabulary":
            names = {normalized(merged["lemma"]), *(normalized(x) for x in merged["aliases"])}
            candidates = [e["id"] for e in others if e["kind"] == "vocabulary" and
                          names.intersection({normalized(e["lemma"]), *(normalized(x) for x in e["aliases"])})]
            require(not candidates or allow_new_sense, f"Possible existing meanings: {candidates}. Inspect them, then use --allow-new-sense for a distinct meaning.")
        if existing:
            if merged == existing:
                return {"action": "unchanged", "entry_id": existing["id"], "revision": existing["revision"]}
            require(expected_revision == existing["revision"], f"Revision conflict: read {existing['id']} and supply --expected-revision {existing['revision']}")
            merged["revision"] += 1
            merged["updated_at"] = timestamp
        content = merged.pop("content")
        atomic_write(self.entry_path(merged["id"]), document(merged, content))
        self.rebuild()
        return {"action": "updated" if existing else "created", "entry_id": merged["id"], "revision": merged["revision"]}

    def events(self):
        result = []
        for path in sorted((self.base / "lessons").glob("*/reviews/*.json")):
            event = read_json(path)
            require(path.stem == event.get("event_id") and re.fullmatch(r"[0-9a-f]{32}", path.stem), "Review event filename mismatch")
            require(event.get("lesson_id") == path.parent.parent.name, "Review lesson mismatch")
            self.lesson(event["lesson_id"])
            self.get(event["entry_id"])
            require(event.get("result") in RESULTS, "Invalid review result")
            text(event.get("answer"), "Review answer")
            text(event.get("feedback"), "Review feedback")
            dt.datetime.fromisoformat(event["recorded_at"])
            if event.get("next_review"):
                date(event["next_review"])
            result.append(event)
        return sorted(result, key=lambda e: (e["recorded_at"], e["event_id"]))

    def record_review(self, event):
        require(set(event) <= {"event_id", "lesson_id", "entry_id", "result", "answer", "feedback", "next_review"}, "Unknown review fields")
        require(re.fullmatch(r"[0-9a-f]{32}", event.get("event_id", "")), "Provide a stable UUID hex event_id for retry safety")
        self.lesson(event.get("lesson_id"))
        self.get(event.get("entry_id"))
        require(event.get("result") in RESULTS, "Result must be again, hard, good, or easy")
        text(event.get("answer"), "Actual answer or account of the attempt")
        text(event.get("feedback"), "Feedback")
        if event.get("next_review"):
            date(event["next_review"])
        path = self.lesson_dir(event["lesson_id"]) / "reviews" / (event["event_id"] + ".json")
        # An event ID cannot be reused in another lesson.
        matches = list((self.base / "lessons").glob(f"*/reviews/{event['event_id']}.json"))
        if matches:
            old = read_json(matches[0])
            require(len(matches) == 1 and matches[0] == path and
                    {k: v for k, v in old.items() if k != "recorded_at"} == event,
                    "Review event ID already exists with different content")
            return {"action": "unchanged", "event_id": event["event_id"]}
        atomic_write(path, json.dumps({**event, "recorded_at": now()}, ensure_ascii=False, indent=2) + "\n")
        self.rebuild()
        return {"action": "created", "event_id": event["event_id"]}

    def exercise(self, lesson_id):
        metadata, body = read_document(self.lesson_dir(lesson_id) / "exercises.md")
        require(metadata.get("lesson_id") == lesson_id, "Exercise lesson mismatch")
        require(type(metadata.get("revision")) is int and metadata["revision"] >= 0, "Invalid exercise revision")
        for kind, field in (("vocabulary", "vocabulary_ids"), ("grammar", "grammar_ids")):
            require(isinstance(metadata.get(field), list), f"{field} must be an array")
            for entry_id in metadata[field]:
                require(self.get(entry_id)["kind"] == kind, f"Wrong kind in {field}")
        return metadata, body

    def publish_exercises(self, payload, expected_revision):
        require(set(payload) == {"lesson_id", "vocabulary_ids", "grammar_ids", "content"}, "Exercise payload requires lesson_id, vocabulary_ids, grammar_ids, content")
        self.lesson(payload["lesson_id"])
        old, old_body = self.exercise(payload["lesson_id"])
        for kind, field in (("vocabulary", "vocabulary_ids"), ("grammar", "grammar_ids")):
            require(isinstance(payload[field], list), f"{field} must be an array")
            for entry_id in payload[field]:
                require(self.get(entry_id)["kind"] == kind, f"Wrong entry kind: {entry_id}")
        require(payload["vocabulary_ids"] or payload["grammar_ids"], "An exercise must reference study material")
        body = text(payload["content"], "Exercises").rstrip() + "\n"
        metadata = {k: v for k, v in payload.items() if k != "content"}
        metadata["revision"] = old["revision"]
        if metadata == old and body == old_body:
            return {"action": "unchanged", "revision": old["revision"]}
        require(expected_revision == old["revision"], f"Exercise revision conflict; expected {old['revision']}")
        metadata["revision"] += 1
        atomic_write(self.lesson_dir(payload["lesson_id"]) / "exercises.md", document(metadata, body))
        self.rebuild()
        return {"action": "published", "revision": metadata["revision"]}

    def search(self, query="", level=None, topic=None, kind=None):
        result = []
        for entry in self.entries():
            if kind and entry["kind"] != kind:
                continue
            if level and entry["cefr"]["level"] != level:
                continue
            if topic and not any(normalized(topic) in normalized(t) for t in entry["topics"]):
                continue
            if normalized(query) not in normalized(json.dumps(entry, ensure_ascii=False)):
                continue
            result.append(entry)
        return result

    def select(self, limit=8, topic=None, level=None, as_of=None):
        require(limit > 0, "limit must be positive")
        as_of = date(as_of or dt.date.today().isoformat())
        latest = {e["entry_id"]: e for e in self.events()}
        candidates = self.search(topic=topic, level=level, kind="vocabulary")
        def priority(entry):
            event = latest.get(entry["id"])
            if event and event.get("next_review"):
                return 0 if event["next_review"] <= as_of else 3
            if event and event["result"] in ("again", "hard"):
                return 0
            return 1 if not event else 2
        candidates = [e for e in candidates if priority(e) != 3]
        candidates.sort(key=lambda e: (priority(e), latest.get(e["id"], {}).get("recorded_at", ""), e["id"]))
        return [{"entry_id": e["id"], "lemma": e["lemma"], "sense": e["sense"],
                 "reason": "review" if priority(e) == 0 else "new" if priority(e) == 1 else "reuse"}
                for e in candidates[:limit]]

    def validate(self):
        entries = self.entries()
        identities = [self.identity(e) for e in entries]
        require(len(identities) == len(set(identities)), "Duplicate entry identities")
        lessons = self.lessons()
        for lesson in lessons:
            self.exercise(lesson["id"])
        events = self.events()
        require(len({e["event_id"] for e in events}) == len(events), "Duplicate review event IDs")
        return {"lessons": len(lessons), "vocabulary": sum(e["kind"] == "vocabulary" for e in entries),
                "grammar": sum(e["kind"] == "grammar" for e in entries), "review_events": len(events)}

    def generated(self):
        """All generated files, calculated before writing anything."""
        self.validate()
        entries = self.entries()
        events = self.events()
        files = {}
        latest = {e["entry_id"]: e for e in events}
        def label(e):
            return e.get("lemma", e.get("topic"))
        def table(items):
            lines = ["| Entry | Meaning / domain | CEFR | Evidence | Last result |",
                     "| --- | --- | --- | --- | --- |"]
            for e in sorted(items, key=lambda e: (normalized(label(e)), e["id"])):
                link = f"../../{e['kind']}/{e['id']}.md"
                lines.append(f"| [{md(label(e))}]({link}) | {md(e.get('sense', e.get('domain')))} | {e['cefr']['level']} | {e['cefr']['status']} | {latest.get(e['id'], {}).get('result', 'not practised')} |")
            return "\n".join(lines) + "\n"
        for level in LEVELS:
            files[self.base / "indexes" / "cefr" / f"{level}.md"] = f"# {level}\n\nGenerated by `tutor.py rebuild`; edit entry records.\n\n" + table([e for e in entries if e["cefr"]["level"] == level])
        topics = sorted({t for e in entries for t in e["topics"]})
        topic_lines = ["# Topics", "", "Generated by `tutor.py rebuild`; edit entry records.", ""]
        for topic in topics:
            topic_lines.extend([f"## {md(topic)}", "", table([e for e in entries if topic in e["topics"]]), ""])
        files[self.base / "indexes" / "topics" / "index.md"] = "\n".join(topic_lines)
        for lesson in self.lessons():
            lesson_id = lesson["id"]
            folder = self.lesson_dir(lesson_id)
            exercise, _ = self.exercise(lesson_id)
            selected = exercise["vocabulary_ids"] + exercise["grammar_ids"]
            associated = [e for e in entries if e["id"] in selected or any(s["lesson_id"] == lesson_id for s in e["sources"])]
            associated.sort(key=lambda e: (e["kind"] != "vocabulary", normalized(label(e)), e["id"]))
            lines = [f"# Study notes — {lesson_id}", "",
                     "Generated from entry records and exercise references. Add explanations to the linked records; write personal notes in raw-notes.md.", "",
                     "[Raw notes](raw-notes.md) · [Exercises](exercises.md) · [Review](review.md)", ""]
            for e in associated:
                lines += [f"## [{md(label(e))}](../../{e['kind']}/{e['id']}.md)", "",
                          e.get("sense", e.get("domain")), "",
                          f"CEFR: {e['cefr']['level']} ({e['cefr']['status']}).", ""]
                for source in e["sources"]:
                    if source["lesson_id"] == lesson_id:
                        lines += ["Original note:", "", *["> " + line for line in source["quote"].splitlines()], ""]
                if e["id"] in selected:
                    lines += ["Selected for this lesson's exercises.", ""]
            if not associated:
                lines += ["No vocabulary or grammar entries have been linked yet.", ""]
            files[folder / "study-notes.md"] = "\n".join(lines)
            lines = [f"# Review — {lesson_id}", "", "Generated from immutable JSON events in `reviews/`. Record attempts using `record-review`.", ""]
            lesson_events = [e for e in events if e["lesson_id"] == lesson_id]
            for e in lesson_events:
                entry = self.get(e["entry_id"])
                lines += [f"## {e['recorded_at']} — [{md(label(entry))}](../../{entry['kind']}/{entry['id']}.md)",
                          "", f"Result: **{e['result']}**", "", "### Your attempt", "", e["answer"],
                          "", "### Feedback", "", e["feedback"], "",
                          f"Next review: {e.get('next_review') or 'not scheduled'}", "",
                          f"Event: `{e['event_id']}`", ""]
            if not lesson_events:
                lines += ["No attempts recorded. Generated exercises do not imply practice or mastery.", ""]
            files[folder / "review.md"] = "\n".join(lines)
        return {path: content.rstrip() + "\n" for path, content in files.items()}

    def rebuild(self, check=False):
        stale = []
        for path, content in self.generated().items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(self.base)))
                if not check:
                    atomic_write(path, content)
        require(not check or not stale, f"Generated views are stale: {stale}; run rebuild")
        return {"updated": stale}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT, help="Repository root; useful for isolated tests")
    p.add_argument("--language", default="german")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create-lesson")
    c.add_argument("--date", default=dt.date.today().isoformat())
    c.add_argument("--topic", required=True)
    c.add_argument("--level", choices=LEVELS, default="UNKNOWN")
    c.add_argument("--minutes", type=int, default=15)
    c.add_argument("--id", help="Optional stable lesson ID for retrying the same creation")
    c = sub.add_parser("get")
    c.add_argument("id")
    c = sub.add_parser("search")
    c.add_argument("query", nargs="?", default="")
    c.add_argument("--level", choices=LEVELS)
    c.add_argument("--topic")
    c.add_argument("--kind", choices=KINDS)
    c = sub.add_parser("upsert")
    c.add_argument("--file", required=True)
    c.add_argument("--expected-revision", type=int)
    c.add_argument("--allow-new-sense", action="store_true")
    c = sub.add_parser("record-review")
    c.add_argument("--file", required=True)
    c = sub.add_parser("publish-exercises")
    c.add_argument("--file", required=True)
    c.add_argument("--expected-revision", type=int, required=True)
    c = sub.add_parser("select")
    c.add_argument("--limit", type=int, default=8)
    c.add_argument("--topic")
    c.add_argument("--level", choices=LEVELS)
    c.add_argument("--as-of")
    sub.add_parser("validate")
    c = sub.add_parser("rebuild")
    c.add_argument("--check", action="store_true")
    return p


def main():
    args = parser().parse_args()
    try:
        store = Store(args.root, args.language)
        with store.lock():
            # Fail before mutations if existing canonical data is inconsistent.
            store.validate()
            if args.command == "create-lesson":
                result = store.create_lesson(args.date, args.topic, args.level, args.minutes, args.id)
            elif args.command == "get":
                result = store.get(args.id)
            elif args.command == "search":
                result = store.search(args.query, args.level, args.topic, args.kind)
            elif args.command == "upsert":
                result = store.upsert(read_json(args.file), args.expected_revision, args.allow_new_sense)
            elif args.command == "record-review":
                result = store.record_review(read_json(args.file))
            elif args.command == "publish-exercises":
                result = store.publish_exercises(read_json(args.file), args.expected_revision)
            elif args.command == "select":
                result = store.select(args.limit, args.topic, args.level, args.as_of)
            elif args.command == "validate":
                result = store.validate()
            else:
                result = store.rebuild(args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

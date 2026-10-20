import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tutor import ROOT, Store, read_document
from migrate_legacy import migrate


class TutorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "german").mkdir()
        self.store = Store(self.root, "german")
        self.lesson = self.store.create_lesson(
            "2026-10-20", "Appointments", "A2", 15, "lesson-2026-10-20-01"
        )["lesson_id"]
        self.raw = self.store.lesson_dir(self.lesson) / "raw-notes.md"
        self.raw.write_text("Ich rufe beim Arzt an.\nSchlüssel\nhelfen + Dativ?\n", encoding="utf-8")
        self.payload = {
            "kind": "vocabulary", "lemma": "anrufen", "part_of_speech": "verb",
            "sense": "to phone someone", "aliases": ["rufe an"], "topics": ["appointments"],
            "sources": [{"lesson_id": self.lesson, "quote": "Ich rufe beim Arzt an."}],
            "forms": {"perfect": "hat angerufen"}, "content": "# anrufen\n\nExample.\n",
        }

    def add(self):
        return self.store.upsert(copy.deepcopy(self.payload))["entry_id"]

    def event(self, entry, **changes):
        return {"event_id": uuid.uuid4().hex, "lesson_id": self.lesson, "entry_id": entry,
                "result": "hard", "answer": "Ich anrufe den Arzt.",
                "feedback": "Ich rufe den Arzt an.", **changes}

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_repeated_import_and_second_lesson_share_one_entry(self):
        entry = self.add()
        before = self.snapshot()
        self.assertEqual(self.store.upsert(self.payload)["action"], "unchanged")
        self.assertEqual(before, self.snapshot())
        second = self.store.create_lesson("2026-10-20", "Second lesson")["lesson_id"]
        self.assertNotEqual(second, self.lesson)
        raw = self.store.lesson_dir(second) / "raw-notes.md"
        raw.write_text("anrufen again", encoding="utf-8")
        update = {"kind": "vocabulary", "id": entry,
                  "sources": [{"lesson_id": second, "quote": "anrufen again"}]}
        self.store.upsert(update, expected_revision=1)
        self.assertEqual(len(self.store.entries()), 1)
        self.assertEqual(len(self.store.get(entry)["sources"]), 2)
        self.assertEqual(self.store.get(entry)["forms"], {"perfect": "hat angerufen"})
        self.assertIn(entry, (raw.parent / "study-notes.md").read_text())
        self.assertEqual(self.raw.read_text(), "Ich rufe beim Arzt an.\nSchlüssel\nhelfen + Dativ?\n")

    def test_stale_updates_and_invalid_sources_do_not_write(self):
        entry = self.add()
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Revision conflict"):
            self.store.upsert({"id": entry, "kind": "vocabulary", "content": "Changed"}, 0)
        self.assertEqual(before, self.snapshot())
        with self.assertRaisesRegex(ValueError, "absent"):
            self.store.upsert({"id": entry, "kind": "vocabulary",
                               "sources": [{"lesson_id": self.lesson, "quote": "invented quote"}]}, 1)
        self.assertEqual(before, self.snapshot())
        with self.assertRaises(ValueError):
            self.store.upsert({"id": entry, "kind": "vocabulary", "mastery": "learned"}, 1)
        self.assertEqual(before, self.snapshot())

    def test_cefr_reclassification_moves_index_without_changing_identity(self):
        entry = self.add()
        with self.assertRaisesRegex(ValueError, "source_url"):
            self.store.upsert({"kind": "vocabulary", "id": entry,
                               "cefr": {"level": "A2", "status": "verified"}}, 1)
        self.store.upsert({"kind": "vocabulary", "id": entry,
                           "cefr": {"level": "A2", "status": "estimated", "note": "Teaching estimate"}}, 1)
        self.assertIn(entry, (self.store.base / "indexes/cefr/A2.md").read_text())
        self.assertNotIn(entry, (self.store.base / "indexes/cefr/UNKNOWN.md").read_text())
        self.assertEqual(self.store.search(level="A2")[0]["id"], entry)
        self.assertEqual(self.store.rebuild(check=True)["updated"], [])

    def test_polysemy_requires_deliberate_new_sense(self):
        self.add()
        other = {**self.payload, "sense": "to invoke a deity"}
        with self.assertRaisesRegex(ValueError, "Possible existing meanings"):
            self.store.upsert(other)
        self.store.upsert(other, allow_new_sense=True)
        self.assertEqual(len(self.store.entries()), 2)
        duplicate = {**self.payload, "id": "v-" + uuid.uuid4().hex}
        with self.assertRaisesRegex(ValueError, "already has this identity"):
            self.store.upsert(duplicate, allow_new_sense=True)

    def test_unicode_equivalent_identity_does_not_duplicate(self):
        payload = {**self.payload, "lemma": "Schlüssel", "part_of_speech": "noun",
                   "sense": "key", "aliases": [],
                   "sources": [{"lesson_id": self.lesson, "quote": "Schlüssel"}]}
        entry = self.store.upsert(payload)["entry_id"]
        decomposed = {**payload, "lemma": "Schlu\u0308ssel"}
        self.assertEqual(self.store.upsert(decomposed, 1)["entry_id"], entry)
        self.assertEqual(len(self.store.entries()), 1)

    def test_review_retry_and_exercise_regeneration_preserve_answers(self):
        entry = self.add()
        event = self.event(entry)
        self.store.record_review(event)
        event_path = self.store.lesson_dir(self.lesson) / "reviews" / (event["event_id"] + ".json")
        original = event_path.read_bytes()
        self.assertEqual(self.store.record_review(event)["action"], "unchanged")
        with self.assertRaisesRegex(ValueError, "different content"):
            self.store.record_review({**event, "answer": "different answer"})
        exercises = {"lesson_id": self.lesson, "vocabulary_ids": [entry],
                     "grammar_ids": [], "content": "# Retrieval\n\nSay you will phone the doctor."}
        raw_before = self.raw.read_bytes()
        self.store.publish_exercises(exercises, 0)
        self.assertEqual(self.store.publish_exercises(exercises, 0)["action"], "unchanged")
        with self.assertRaisesRegex(ValueError, "revision conflict"):
            self.store.publish_exercises({**exercises, "content": "Changed"}, 0)
        self.store.publish_exercises({**exercises, "content": "Changed exercise"}, 1)
        self.assertEqual(original, event_path.read_bytes())
        self.assertEqual(raw_before, self.raw.read_bytes())
        self.assertIn(event["answer"], (self.raw.parent / "review.md").read_text())
        self.assertEqual(len(self.store.events()), 1)

    def test_reuse_in_new_lesson_does_not_invent_capture(self):
        entry = self.add()
        second = self.store.create_lesson("2026-10-21", "Reuse")["lesson_id"]
        self.store.publish_exercises({"lesson_id": second, "vocabulary_ids": [entry],
                                      "grammar_ids": [], "content": "Practise anrufen."}, 0)
        self.assertEqual(len(self.store.get(entry)["sources"]), 1)
        self.assertIn(entry, (self.store.lesson_dir(second) / "study-notes.md").read_text())
        self.assertEqual(self.store.events(), [])

    def test_review_queue_respects_due_dates_and_strict_filters(self):
        entry = self.add()
        self.store.record_review(self.event(entry, next_review="2026-10-22"))
        self.assertEqual(self.store.select(as_of="2026-10-21"), [])
        self.assertEqual(self.store.select(as_of="2026-10-22")[0]["reason"], "review")
        self.assertEqual(self.store.select(topic="unrelated", as_of="2026-10-22"), [])
        self.assertEqual(self.store.select(level="C1", as_of="2026-10-22"), [])

    def test_grammar_and_vocabulary_are_referenced_by_correct_kind(self):
        grammar = self.store.upsert({
            "kind": "grammar", "topic": "Dative after helfen", "domain": "cases",
            "sources": [{"lesson_id": self.lesson, "quote": "helfen + Dativ?"}],
            "content": "Ich helfe meinem Freund.",
        })["entry_id"]
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "Wrong entry kind"):
            self.store.publish_exercises({"lesson_id": self.lesson, "vocabulary_ids": [grammar],
                                          "grammar_ids": [], "content": "Practice."}, 0)
        self.assertEqual(before, self.snapshot())
        self.store.publish_exercises({"lesson_id": self.lesson, "vocabulary_ids": [],
                                      "grammar_ids": [grammar], "content": "Practice."}, 0)
        self.assertEqual(self.store.validate()["grammar"], 1)

    def test_generated_view_repair_and_source_drift_detection(self):
        self.add()
        path = self.raw.parent / "study-notes.md"
        path.write_text("Accidentally edited", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.store.rebuild(check=True)
        self.store.rebuild()
        self.assertIn("anrufen", path.read_text())
        self.raw.write_text("Removed source", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "absent"):
            self.store.validate()

    def test_lesson_retry_and_invalid_identifiers(self):
        before = self.snapshot()
        self.assertEqual(self.store.create_lesson("2026-10-20", "Appointments", "A2", 15, self.lesson)["action"], "unchanged")
        self.assertEqual(before, self.snapshot())
        for bad in ("../escape", "lesson-2026-99-99-01", "lesson-2026-10-20-../x"):
            with self.assertRaises(ValueError):
                self.store.lesson_dir(bad)
        with self.assertRaises(ValueError):
            self.store.create_lesson("2026-10-20", "Different", "A2", 15, self.lesson)
        self.assertEqual(before, self.snapshot())

    def test_cli_end_to_end_and_concurrent_retry(self):
        payload = self.root / "entry.json"
        payload.write_text(json.dumps(self.payload), encoding="utf-8")
        cmd = [sys.executable, str(ROOT / "scripts/tutor.py"), "--root", str(self.root)]
        processes = [subprocess.Popen(cmd + ["upsert", "--file", str(payload)],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        results = []
        for process in processes:
            out, err = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, err)
            results.append(json.loads(out))
        self.assertEqual({r["action"] for r in results}, {"created", "unchanged"})
        self.assertEqual(len({r["entry_id"] for r in results}), 1)
        for args in (["get", results[0]["entry_id"]], ["search", "anrufen"], ["select", "--limit", "1"],
                     ["validate"], ["rebuild", "--check"]):
            result = subprocess.run(cmd + args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            json.loads(result.stdout)
        failed = subprocess.run(cmd + ["get", "../escape"], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1)
        self.assertIn("error", json.loads(failed.stderr))


class MigrationTests(unittest.TestCase):
    def test_migration_preserves_all_legacy_files_and_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for source in (ROOT / "german").glob("*"):
                if source.name in ("vocab", "exercise", "grammar"):
                    shutil.copytree(source, root / "german" / source.name)
            # Only original nested grammar files belong in the legacy fixture.
            for path in (root / "german/grammar").glob("g-*.md"):
                path.unlink()
            original = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in root.rglob("*") if p.is_file()}
            result = migrate(root)
            self.assertEqual((result["raw_vocabulary_items"], result["vocabulary_entries"], result["grammar_entries"]), (45, 45, 6))
            for name, digest in original.items():
                self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), digest)
            store = Store(root, "german")
            entry = store.entries()[0]
            store.upsert({"kind": entry["kind"], "id": entry["id"], "content": "A subsequent correction."}, 1)
            self.assertEqual(migrate(root)["action"], "already_migrated")
            self.assertEqual(store.get(entry["id"])["content"], "A subsequent correction.\n")
            self.assertTrue(all(e["cefr"]["status"] == "estimated" for e in store.entries()))
            self.assertEqual(store.events(), [])


if __name__ == "__main__":
    unittest.main()

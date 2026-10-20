---
name: review-lesson
description: Give feedback on actual German practice and save lesson-linked answers, corrections, and review results without changing raw notes or generated exercises.
---

# Review a lesson

Read the review contract in `docs/data-contract.md`. Resolve the lesson ID and the relevant vocabulary or grammar IDs.

- Evaluate the user's actual answer or described attempt. Explain corrections briefly and give a reusable example.
- Record `again` for an unsuccessful attempt, `hard` for an attempt needing help, `good` for a successful attempt, or `easy` when the user reports effortless retrieval. Let the user's own assessment take priority when provided.
- Use one review event per assessed entry. Do not infer successful recall merely because the entry appeared in a dialogue or the user read an explanation.
- Generate a UUID hex `event_id` once, then prepare the JSON with `lesson_id`, `entry_id`, `result`, the user's `answer`, and `feedback`. The answer may describe spoken practice when the user supplies that account.
- Include `next_review` only when a date has been chosen with the learner or under an agreed scheduling rule. The repository has no automatic spaced-repetition algorithm.
- Run `tutor.py record-review --file ...`. Retry with the same ID and payload; changed content under an existing event ID is rejected. If a saved assessment was wrong, record a new event explaining the correction.
- Run `validate` and `rebuild --check`; show what was recorded.

Review JSON events are the persistent record. `review.md` is a generated view. Extraction and exercise regeneration must preserve these events and the user's answers.

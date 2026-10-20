---
name: extract-grammar
description: Extract grammar questions and patterns from lesson raw notes into reusable, sourced grammar entries and linked lesson study notes. Replaces create_grammar_tree.
---

# Extract grammar from a lesson

Read `docs/workflow.md` and `docs/data-contract.md`. Resolve the lesson ID from the request or active session.

- Read the lesson's raw notes and identify rules, questions, and constructions. Preserve the user's wording; a mistaken raw rule is evidence of the question, not an authoritative explanation.
- Search existing grammar entries by topic/domain with `tutor.py search --kind grammar`, then inspect candidates with `get`.
- Create or update a `kind: grammar` payload containing the topic, domain, source quote, topics, CEFR evidence, and explanation in `content`. Include a correct pattern, short examples, relevant exceptions, and a common mistake when useful.
- Prefer accuracy over expansion. Check uncertain rules against suitable sources. Label unresolved issues and pedagogical estimates. For `verified` CEFR supply an explicit source URL, locator, and date as described in the contract.
- Write through `tutor.py upsert --file ...`, using the ID and expected revision for existing entries. Repeated questions add source links; they should not duplicate the same topic.
- Run `validate` and `rebuild --check`; summarize changes and unresolved questions.

Source notes remain verbatim. Generated lesson study notes link to the canonical explanation. Do not update the historical per-level grammar files.

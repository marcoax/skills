---
name: add-recap
description: 'Add a recap lesson: a fixed random sample plus a dedicated section for words and expressions to distinguish, copied from existing lessons. Argument: the title, e.g. "Ripasso di Natale".'
disable-model-invocation: true
argument-hint: "<titolo del riepilogo>"
---

# Add a recap lesson

`docs/recap-lessons.md` is the single source of truth for the format, the sampling rules and deployment. Read it first and follow it; this skill only adds how to talk to the teacher.

Title: `$ARGUMENTS`. If it is empty, ask for it.

## Steps

1. **Survey the lessons.** Read every `data/*.js`. A lesson is **covered** when an existing recap lists it, in its `Ripasso di:` comment or in an old-style `recap: [...]`. Read the examples and usage register in `docs/which-word.md`, reconcile the register with existing recap quizzes as described there, and look for comparison pairs or groups in the lesson items, gaps and notes, including ones not listed in the dictionary. Distractors alone do not establish that a term has an exercise. Done when every data file is classified and candidate groups have source lessons, complete/incomplete status and new/already-used status.

2. **Ask, in one round** (the question tool where available, otherwise a numbered list):
   - which lessons to include (multi-select): uncovered lessons first, each with its date and quiz titles, then the covered ones with the recap that includes them;
   - the recap date (`YYYY-MM-DD`; it must not clash with an existing file);
   - pairs or groups for the dedicated “Which word?” section, e.g. “big/great, how much/how many, this/that/these/those”; propose unused groups following the register rules, with their lesson dates and complete/incomplete status, and collect any other must-include topics (optional). If the teacher selects lessons in the same reply, recheck availability against that selection before sampling;
   - the totals: 30 words and 10 gap sentences unless the teacher changes them.

   Done when there is at least one lesson, a date, the totals and the chosen comparison groups (or none).

3. **Sample** following `docs/recap-lessons.md` step 2. Draw with a throwaway `node` script using `Math.random`, not by hand. Reserve complete comparison groups first, then draw the remaining entries. Report missing or incomplete groups in the chosen lessons; never invent exercises to complete them.

4. **Write the recap** following the doc, steps 3–4: keep comparison entries in their dedicated quiz with `roundSize: 5`, add the short Italian explanations described there, and keep the agreed totals across both quizzes.

5. **Check.** Run `node scripts/check-data.js` and `node scripts/check-progress.js`. Done when both pass. If one fails, report the output in full.

6. **Record usage.** Update the register in `docs/which-word.md` for the comparisons actually included, following its recording rules. Done when every included comparison has a row linking to the checked recap.

7. **Report** the lessons included, how many items came from each, the comparison groups and explanations, any missing topics, the check results and the files to upload, in the order given in the doc.

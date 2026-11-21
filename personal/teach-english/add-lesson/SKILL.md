---
name: add-lesson
description: Turn a lesson's .docx/.md notes into a quiz file, or add words to an existing lesson.
disable-model-invocation: true
---

# Add a lesson to the English review app

The app (index.html, app.js, style.css, data/) is a static quiz published at magutti.com/corso-inglese/. Learners are Italian, aged 60–70. Each lesson is one file `data/AAAAMMGG.js`; its header comment in `data/20260924.js` documents the schema — read it and use that file as the reference for tone, length and structure.

## Steps

1. **Read the sources.** Convert every docx in `lessons/AAAAMMGG/` with `textutil -convert txt -stdout <file>`; read `.md` files as they are. Other formats (pdf, images): tell the user they were not read. The date comes from the folder name.

2. **Propose how to split the lesson.** One quiz per coherent topic (e.g. "Words & phrases", "Phrasal verbs: GET"), each of one type:
   - **word quiz** (`items` + `gaps`): the default, for vocabulary, phrases and sentences;
   - **text quiz** (`type: "text"`): a short story with blanks. At most one per lesson, and only when the material has a clear theme (a train journey, a day in town); otherwise don't propose it. It adds to the word quizzes, never replaces them.

   Material that fits neither (e.g. a dialogue to transform) is not forced into a quiz: say so and skip it. Show the user the split (quiz titles, type, what goes in each) and wait for approval before writing any content. A lesson holds at most 80 items (`check-data.js` enforces it): when the sources exceed that, propose which sections to drop or to leave for a later lesson. Done when every source section is assigned to a quiz or reported as skipped, and the item total fits.

3. **Clean the list.** The notes are taken live during class:
   - ignore bare numbers;
   - fix typos and write the correct form (bare → bear);
   - merge duplicates and near-duplicates into one item;
   - drop fragments with no meaning on their own ("I", "Live");
   - keep personal sentences as they are — they are the most useful to review;
   - British English is the rule (spelling, grammar, "my family live"); add a `note` when the US form differs;
   - complete sentences left unfinished in the notes ("We moved … in …") with a plausible detail, or turn them into a gap;
   - a list of the teacher's corrections ("✅ I missed the train ❌ I lost the train") is not a set of items: the wrong forms become `wrongEn` options and `note`s on the matching item;
   - in question-and-answer exercises, the questions are the items; the short answers ("I phoned Andrew") are better used as gap sentences than as items of their own.

   Anything doubtful (a strange number, an ambiguous phrase): ask the user, one question at a time.

4. **Check earlier lessons.** Write the draft's English items one per line and run `node scripts/find-repeats.js < file`. Review each `simile` match yourself: it is a repeat only if it teaches the same thing. Drop every repeat from the draft; keep one only when it teaches something the earlier lesson did not (a new meaning, a verb form, a use in a sentence) and say what in the approval table. Done when every item is marked new, dropped as already in a lesson (with its date), or kept with the reason.

5. **Write the content.** For every item: Italian meaning, 2 plausible wrong Italian options (`wrong`) and 2 plausible wrong English options (`wrongEn`) — typical learner mistakes and false friends, never absurd ones. For sets where items are distractors of each other (like phrasal verbs), `wrong`/`wrongEn` can be omitted. Use `noReverse` and `group` when two items share the same Italian meaning, so no question has two right answers. Add gap-fill sentences (`gaps`) for items where usage matters (verbs, prepositions, structures); simple nouns don't need one. Each gap has exactly one correct option among the three, and an Italian translation of the whole sentence (`it`), written as natural Italian rather than word for word.

   Before preparing the approval table, read [Lesson language checks](../../../docs/lesson-language.md) and apply them to every item, gap and text blank. Check both EN→IT and IT→EN, including automatically generated distractors. Done when each enabled direction has exactly one valid answer in the context the learner sees, every meaning distractor is natural British English that matches its Italian twin, and every Italian translation reads naturally. Record reusable language findings in that shared document, which is used by both the Codex and Claude versions of this skill.

   For a text quiz, write a new story of 5–8 sentences with 4–6 blanks, built on the lesson's words and rules (prepositions, question words, past simple…). Reuse the lesson's own sentences word for word where they fit. Each blank has one right answer and 2 plausible wrong options; the rest of the story must make only one of them correct. Add the Italian translation (`it`). Keep the facts plausible (Lisbon to Paris by train takes about a day, not an hour) and list any word the story adds that is not in the lesson ("ticket inspector"), so the user can approve it.

   **Review.** Dispatch a subagent with a fresh context. Give it the draft content and `docs/lesson-language.md`, and ask it to check every item, gap, blank and distractor against those checks, reporting each finding with its correction. For every gap and blank, have it read each option as a complete sentence with the Italian translation hidden: an option that is grammatical there is a finding. Without subagents, do the same as a separate reread pass. Apply the fixes, then show the approval table. Done when the reviewer reports no findings or every finding is resolved.

6. **Get approval.** Show the user the final list as a compact table (EN | IT | wrong options) plus the gap sentences with their translations and, for a text quiz, the story with blanks marked, its options and the translation, listing what you dropped or corrected and why. List the items dropped as already present in earlier lessons ("già nella lezione del 24 settembre") and the repeats kept, each with its reason; the user may reinstate any dropped item. Write files only after they approve.

7. **Write the files.** Create `data/AAAAMMGG.js` following the schema, and add `<script src="data/AAAAMMGG.js?v=N"></script>` in index.html next to the other lessons. When adding words to an existing lesson, edit its file instead. Either way, bump the shared `?v=` by one on every asset in index.html (they all carry the same number), so browsers and the installed app fetch the new copy. `lesson.id`, `quiz.id`, item `en` and gap `text` are `localStorage` keys: changing one resets learners' progress, so change them only to fix a mistake.

8. **Verify.** Run `node scripts/check-data.js` and fix every error it reports until it prints `OK`. Then use the `run` skill to open http://teach-english.test and open each new or changed quiz in the browser: it must load, show its items and gaps, and let you answer one question. Report what you saw; the user checks it too. Remind the user which files to upload to magutti.com (the new/changed `data/` file and index.html, which changes every time).

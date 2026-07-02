---
name: teach-lesson
description: Menu launcher for this repo's Laravel 12→13 lessons. A thin wrapper around /teach — it lists the lessons in lessons/, proposes the first not-yet-done one, and on the learner's choice hands off to /teach for that lesson. Read-only on progress (never marks completion). Use whenever the learner wants to start or continue the course, or asks "do lesson 3", "facciamo la lezione 3", "what's the next lesson", "qual è la prossima lezione", "resume", "riprendiamo", "continue", "show me the lessons", "mostrami le lezioni", "teach-lesson" — even without naming a specific lesson file.
argument-hint: "(optional) lesson number or slug, e.g. 3 or queue-fail-on-exception"
---

A **thin wrapper around `/teach`**. Its only job is to pick *which* lesson to run, then
delegate the whole teaching session to `/teach`.

## Non-negotiable principles

1. **Read-only on progress.** Never write completion state. Marking a lesson done belongs to
   the lesson lifecycle (`CLAUDE.md` → *Lesson lifecycle*: `progress.json` + learning record).
2. **One final action: hand off to `/teach`.** Build the menu, resolve the lesson, then
   execute `/teach` for it **in-session** — never ask the learner to type a command. Nothing else.
3. **Lessons are whatever is on disk**, never a hardcoded list.

## Flow

### 1. Collect lessons

Two families live side by side in `lessons/`, and both belong in the menu:

```bash
ls lessons/[0-9][0-9]-*.md 2>/dev/null | sort            # main sequence: NN-<slug>.md
ls lessons/[0-9]*.[0-9]*.[0-9]*.md 2>/dev/null | sort -V  # extra: version-pure, from /lesson-update
```

Exclude `_template.md`, `README.md`, and the rendered `.html` from both. Order the main sequence
by numeric prefix; order the version-pure files by semantic version. If `lessons/` is missing or
both globs are empty, stop and say so — you are probably not at the repo root.

### 2. Read progress (read-only)

Completion lives in **`progress.json`** at the repo root (git-ignored). Shape:
`{ "progress": { "<id>": { "status", "note" } } }`.

- **Main-sequence lessons** are keyed by numeric lesson id, where **id N ↔ the `NN-` lesson**
  (id `1` → `01-*.md`).
- **Version-pure lessons** are keyed by their version string (e.g. `"13.17.0"`), read from the
  file's `version:` frontmatter. This key is very likely absent today — that just means "to do",
  not an error.

A lesson is **done** when its entry has `"status": "done"`.

```bash
cat progress.json 2>/dev/null
```

**Fallback:** if `progress.json` is absent or unparseable → treat all lessons as to-do (first
not-done is `01`). Don't block, don't ask. Never write to `progress.json`.

### 3. First not-done

The first lesson, in numeric order, whose id is not `done`, **from the main sequence only**. This
is the menu default. Version-pure lessons never displace it as the recommended default — they're
surfaced as extra options, not the spine of the course.

### 4. Show the menu

**One flat list, no main-vs-extra split.** The first not-done main-sequence lesson goes on top
as the recommended default; below it, every lesson appears in a single sequence — main-sequence
first in numeric order, then version-pure lessons appended in version order. Same row shape for
both families: `id · title (version) · status`.

- **Display id, continuous across both families.** Main-sequence lessons keep their existing
  `01`…`12`. Version-pure lessons get the **next integers in sequence** — `13`, `14`, `15`… —
  assigned purely by their position in the version-ordered list at render time (not stored, not
  file-derived: the *n*-th version-pure file in ascending version order is always `12 + n`, no
  matter how many exist that day). This is a **display-only index for the menu**, distinct from
  the underlying filename — it does **not** rename files and does **not** replace the version
  string as the lesson's real identity in `progress.json` (ADR-0006: version-pure files stay
  version-named on disk precisely so an upstream collision by version is visible; renumbering
  them would erase that signal). Recompute it fresh every time the menu renders — a new
  version-pure lesson accepted mid-course simply appends one more integer.
- **Version**, for every row: read it from the `> Version:` line in the lesson's frontmatter/prose
  (e.g. `12.x, through 12.19` → show as `12.x–12.19`; a single version stays as-is). This is what
  lets the learner see the Laravel release(s) a lesson maps to at a glance, main-sequence or extra.
- **Title**, for version-pure lessons: read the `title:` frontmatter field (a kebab-case slug,
  written once at generation time by `/lesson-update` — see its step 5). Never re-derive it by
  parsing the `# Lesson X.Y — <title>` heading here; the frontmatter is the single source of
  truth. Never show a bare version number as the row label.

Use the learner's `language.chat` from `learning-config.md` (default English) for the menu text.

```
Lessons — Laravel 12 → 13

▶ NEXT   10 · ai-sdk (13.0)                                    🟡 in progress ← resume

  01 · eloquent-casts (12.x–12.19)                             ✅ done
  02 · query-builder-pipelines (12.4)                          ✅ done
  03 · queue-fail-on-exception (12.19)                         ✅ done
  04 · duration-and-http-helpers (12.40–12.41)                 ✅ done
  05 · array-collection-gate-helpers (12.45–12.46)             ✅ done
  06 · php-83-upgrade (13.0)                                   ✅ done
  07 · php-attributes (13.0–13.8)                              ✅ done
  08 · csrf-prevent-request-forgery (13.0)                     ✅ done
  09 · queue-route-interruptible-cache (13.0–13.7)             ✅ done
  10 · ai-sdk (13.0)                                           🟡 in progress ← next
  11 · vector-search (13.0)                                    ⬜ to do
  12 · json-api-resources (13.0)                                ⬜ to do
  13 · html-password-rules (13.9.0)                             ⬜ to do
  14 · scheduler-metadata-opt-out-listener-discovery (13.12.0)  ⬜ to do
  15 · bulk-job-dispatch (13.13.0)                              ⬜ to do
  16 · typed-translation-accessors (13.15.0)                    ⬜ to do
  17 · first-class-route-metadata (13.17.0)                     ⬜ to do

Which lesson? (default: next, 10)
```

Prefer tappable options when available (first option = next/default). Otherwise accept a
number, a slug, a version string, or "next"/Enter for the default.

### 5. Hand off to /teach

Resolve the exact path, then **run `/teach` in-session — do not ask the learner to type it.**
`/teach` carries `disable-model-invocation`, so the Skill tool can't auto-call it; instead
**read `~/.agents/skills/teach/SKILL.md` and execute its flow** for the resolved lesson file
(main-sequence `lessons/<NN-slug>.md` or version-pure `lessons/<x.y.z>.md`), treating this repo
as the teaching workspace. From there `/teach` owns the session (practice mode, scaffolding,
`TODO(human)`, quiz).

## Optional argument

- **No argument** → menu above.
- **Number ≤ 12, or slug** (`3`, `03`, `queue-fail-on-exception`) → skip the menu, resolve the
  lesson by its `NN-` prefix or slug, hand off directly.
  - The number is the **file prefix**, not a list position: `3` and `03` both resolve to
    `lessons/03-*.md`.
  - If that lesson is already `done`, warn once (`⚠️ Lesson 03 is already done — re-running.`)
    then hand off anyway. No extra confirmation.
- **Number > 12** (`13`, `14`…) → this is the **display id**, not a filename: recompute the
  version-ordered list of version-pure lessons (step 1/4) and take the `(number - 12)`-th entry.
  `13` is always the earliest not-yet-superseded version-pure lesson, `14` the next, etc. — never
  assume it maps to a file literally named `13-*.md` (it doesn't; those don't exist).
- **Version string** (`13.17`, `13.17.0`) → resolve to the matching `lessons/<x.y.z>.md` by
  prefix match on the version (`13.17` matches `13.17.0.md`), hand off directly.
  - Both paths above share the **same already-done warn-then-proceed rule**: warn once, then
    hand off anyway. No extra confirmation.
  - No match → fall back to the menu.

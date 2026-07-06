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
   execute `/teach` for it **in-session** — never ask the learner to type a command. The
   course-page warm-up (step 5) is a best-effort side step; the hand-off stays the final act.
3. **Lessons are whatever is on disk**, never a hardcoded list.
4. **The active path is baseline-filtered.** Read `course_baseline_major` from
   `learning-config.md` (default `12`) and filter learner-facing lesson selection from
   each lesson's `> Version:` metadata, never from file order or numeric prefix.

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

For every candidate lesson, read the first `> Version:` line from the `.md` file and parse the
Laravel major version from that metadata. Examples: `Laravel 12.x, through 12.19`, `12.4`, and
`12.45 · 12.46` are major `12`; `13.0`, `13.0 → 13.8`, and `13.17.0` are major `13`.

Read `course_baseline_major` from `learning-config.md`. If the file is absent, malformed, or the
field is absent, default to `12`. Supported choices are static: `12` and `13`. Before computing
defaults, rendering a menu, or resolving direct requests, keep only lessons whose parsed major is
greater than or equal to the baseline. This hides 12.x lessons for baseline `13` without deleting
files or touching `progress.json`.

If a direct argument resolves to a lesson outside the active baseline, stop with a short message
that the requested lesson is outside the active course path. Do **not** print the hidden lesson's
title, path, contents, or run `/teach` for it.

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

The first active lesson, in numeric order, whose id is not `done`, **from the baseline-filtered
main sequence only**. This is the menu default. Version-pure lessons never displace it as the
recommended default — they're surfaced as extra options, not the spine of the course.

### 4. Show the menu

**One flat list, no main-vs-extra split.** The first not-done active main-sequence lesson goes on
top as the recommended default; below it, every active lesson appears in a single sequence —
main-sequence first in numeric order, then version-pure lessons appended in version order. Same row
shape for both families: `id · title (version) · status`.

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
- **Title**, for version-pure lessons: show a human-readable title, matching the course page.
  Prefer the `LESSONS` entry in `index.html` for that version; if absent, read the title from
  the `# Lesson X.Y — <title>` heading. Do not show the kebab-case frontmatter slug as the
  learner-facing label; it remains metadata for generation/state, not the menu title.

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

### 5. Start the course page (best-effort, never blocking)

Once the lesson is resolved, warm up the course page (`index.html`, the single served
page — ADR-0013/0015) so the learner follows the lesson in the browser while `/teach`
works. **Fail-soft at every step: if anything is missing or fails, skip silently and
proceed to the hand-off — the page is a companion, never a prerequisite.**

1. **Already serving?** Probe once: `curl -s -o /dev/null -w '%{http_code}' -m 1
   http://localhost:8000/`. A `200` means a server is already up — skip to 3.
2. **Start a server** from the repo root, in the background, with whatever is on this
   machine — check availability first (`command -v`), don't assume:
   - `php -S localhost:8000 scripts/progress-server.php` (first choice: a Laravel
     learner has PHP; the router enables the page's manual status marking — ADR-0018), else
   - `python3 -m http.server 8000` (or `python` on systems without `python3`).
   - Neither available, or the port is taken by something that isn't serving this repo →
     skip the page entirely, mention it in one line, move on.
3. **Check the lesson HTML exists** before opening anything: `lessons/<slug>.html` (the
   same basename used in the URL fragment). Two cases:
   - **Exists** → open the browser at `http://localhost:8000/#<slug>` now, using the
     platform's opener: `open` (macOS), `xdg-open` (Linux), `start` (Windows). No opener →
     just print the URL for the learner to click. This is the common case for a
     re-run/already-done lesson (its `.html` was written in a prior session).
   - **Missing** → **do not open the browser yet.** The page would just poll an empty
     hash and look broken. Instead print the URL as plain text
     (`http://localhost:8000/#<slug>`) so the learner can open it by hand whenever they
     want, and note that it'll be opened automatically the moment the lesson HTML exists.
     Remember this pending state for step 6 — open exactly once, the first time the file
     appears.

### 6. Hand off to /teach

Resolve the exact path, then **run `/teach` in-session — do not ask the learner to type it.**
`/teach` carries `disable-model-invocation`, so the Skill tool can't auto-call it; instead
**read `~/.agents/skills/teach/SKILL.md` and execute its flow** for the resolved lesson file
(main-sequence `lessons/<NN-slug>.md` or version-pure `lessons/<x.y.z>.md`), treating this repo
as the teaching workspace. From there `/teach` owns the session (practice mode, scaffolding,
`TODO(human)`, quiz).

**The session stays on the current git branch regardless of `auto_branch`** — that flag is
consulted only by `/lesson-update`; a teaching session's output is all git-ignored, so a
per-lesson branch would be guaranteed empty (ADR-0017). Never cut a branch at lesson start.
If a tracked file needs touching mid-session (a drift fix in a brief, an asset edit), propose
a branch for that change at that moment — manually, not via `auto_branch`.

**If step 5 deferred the browser open** (the lesson `.html` didn't exist yet), keep
following `/teach`'s flow as normal; the moment `/teach` writes `lessons/<slug>.html` for
the first time (its usual generation step), open the browser then — same opener logic as
step 5, fire once. If the file is still missing when the session ends (e.g. the learner
stops before generation), leave it deferred; nothing to clean up, the learner already has
the URL from step 5.

## Optional argument

- **No argument** → menu above.
- **Number ≤ 12, or slug** (`3`, `03`, `queue-fail-on-exception`) → skip the menu, resolve the
  lesson by its `NN-` prefix or slug, then apply the baseline filter. If the resolved lesson is
  hidden by `course_baseline_major`, stop as outside the active course path and do not hand off.
  - The number is the **file prefix**, not a list position: `3` and `03` both resolve to
    `lessons/03-*.md`.
  - If that lesson is already `done`, warn once (`⚠️ Lesson 03 is already done — re-running.`)
    then hand off anyway. No extra confirmation.
- **Number > 12** (`13`, `14`…) → this is the **display id**, not a filename: recompute the
  baseline-filtered, version-ordered list of version-pure lessons (step 1/4) and take the
  `(number - 12)`-th entry.
  `13` is always the earliest not-yet-superseded version-pure lesson, `14` the next, etc. — never
  assume it maps to a file literally named `13-*.md` (it doesn't; those don't exist).
- **Version string** (`13.17`, `13.17.0`) → resolve to the matching active
  `lessons/<x.y.z>.md` by prefix match on the version (`13.17` matches `13.17.0.md`), hand off
  directly. If a version string matches only a hidden lesson, stop as outside the active course
  path.
  - Both paths above share the **same already-done warn-then-proceed rule**: warn once, then
    hand off anyway. No extra confirmation.
  - No match → fall back to the menu.

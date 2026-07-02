---
name: lesson-update
description: Discover new Laravel releases from the editorial sources in learning-config.md (Laravel News, Laravel Daily), propose one lesson per new version, and — on the learner's accept — generate it into lessons/ ready for a PR. Use when the learner wants to check for new Laravel versions / lessons, asks "are there new lessons?", "controlla nuove versioni", "update the lessons", "any Laravel releases I'm missing?", or runs /lesson-update. Also the discovery engine the lesson-completion auto-check (ADR-0007) runs in the background.
argument-hint: "(no arguments — it scans, proposes, and on accept generates)"
---

Discover Laravel releases newer than the existing lessons cover, propose **one lesson per new
version**, and on the learner's accept write it into `lessons/`. Grounded in **ADR-0005 / 0006 /
0007 / 0010 / 0011** — read them if a decision here is unclear; they are the source of truth, this
file is the procedure.

## The one principle everything rests on

**The unit of discovery, state, and output is the Laravel release version — never a feature
name** (ADR-0005). Feature names drift across sources; a version number (`13.17.0`) is stable.
So *every* comparison — "is this new?", "already skipped?", "collides with upstream?" — is by
version string, never by topic similarity.

## Config — the single source of truth

Read these fields from `learning-config.md` at the repo root (authoritative per `CLAUDE.md` →
*Config binding*). If the file is absent, suggest `/lesson-init` and stop.

| field | role |
|-------|------|
| `lesson_sources` | **the** source list — single source of truth for *which* sources, *what* URLs, *what* order. Structured entries (`name`/`transport`/`feed`/`fallback_url?`): one `transport` per source; `fallback_url` is a field of that handler, not a second transport (ADR-0010/0011). The skill iterates this list — **it hardcodes no URLs.** |
| `lesson_changelog` | Laravel framework repo — **cross-check only**, never discovers alone |
| `laravel_version_scanned` | high-water cursor: highest version already examined. "New = > scanned". **Not derivable.** |
| `laravel_version_covered` | highest version turned into a lesson. **Mirror** of `origin: local` files; kept explicit for the README. Advance only on real generation. |
| `lessons_skipped` | versions the learner saw and declined — never re-proposed. **Not derivable.** |
| `auto_check_new_lessons` | `on`/`off` — gates the auto-trigger (ADR-0007). Manual `/lesson-update` ignores it. |
| `last_checked` | date of the last discovery run. |

## Two entry points, one hard boundary

- **Manual `/lesson-update`** (this skill, foreground): runs the full flow below, including
  generation. Always available regardless of `auto_check_new_lessons`.
- **Auto background discovery** (ADR-0007): the lesson lifecycle gate (ADR-0004), when
  `auto_check_new_lessons: on`, spawns a **read-only** sub-agent that runs **steps 1–3 only** and
  reports "N candidates → view now or later?". 

**Hard boundary (ADR-0007): background discovers and proposes; it never generates.** The
background path may advance `laravel_version_scanned` / `last_checked`, and **must not** write
lessons, advance `covered`, touch `lessons_skipped`, or pre-generate drafts. Steps 4–6 (decide +
generate) are always foreground, always gated by the human accept/skip.

## Flow

### 1. Read state
Load the fields above. `laravel_version_scanned` is the floor: only versions above it are candidates.

### 2. Discover by iterating `lesson_sources`
Config owns *which* sources and URLs; this step owns *how* to read each `transport`. **Do not
hardcode source names or URLs here** — they live in `lesson_sources` (ADR-0011).

**Union, not fallback chain (ADR-0011, resolving ADR-0005).** Query **every** entry in
`lesson_sources` and **union** the versions they yield — a release counts if *any* source wrote
about it. Never stop at the first source that yields candidates: a release only the second source
mentions must still surface. Each post yields a `(version, date)` taken **from the post**, not
guessed.

Dispatch on each entry's `transport`:

- **`telegram`** — read `feed` as a firehose: the channel republishes *all* posts (articles,
  packages, tutorials), not just releases. Treat a post as a release announcement when **its
  article link matches `…/laravel-<major>-<minor>-0` OR its title matches `Laravel X.Y`**
  (link-OR-title); ignore the rest. **Walk back bounded:** paginate `?before=<id>` until a post is
  **older than `last_checked`**, capped at **~5 pages** — whichever first; on the first run
  `last_checked` is `null`, so the page cap is the only stop. If `feed` is unreachable, probe
  `fallback_url` (interpolate `{minor}`), **tolerating 404 gaps** (`13-11-0` 404s while `13-12-0`
  exists). `fallback_url` is this handler's backstop, **not** a separate transport.
- **`web`** — fetch `feed` and scan the page's anchor links + headings with the **same
  link-OR-title matcher** (`/laravel-<major>-<minor>-0` or `Laravel X.Y`); take version + date from
  the matched post. **Best-effort:** a `web` source that yields nothing contributes nothing — that
  is not an error.
- **unknown `transport`** — skip with a notice and continue (same fail-soft rule below).

Use `lesson_changelog` only to cross-check version numbers / patch level and ordering. **An
unreachable source is skipped with a notice; execution continues** with the rest.

### 3. Filter to the genuinely new
Keep versions that are (a) `> laravel_version_scanned` and (b) not in `lessons_skipped`. A version
**no editorial source wrote about is skipped silently — the gap *is* the filter** (accepted
limitation, ADR-0005). This is where the background path stops and reports candidates.

### 4. Propose, one at a time
For each candidate version, show a lesson draft (what changed, why it might matter, what to try,
relevance questions) and ask **accept** or **skip**. The human absorbs the residual noise here —
two blogs naming one change differently, a thin release. One version → one proposal.

### 5. Generate the accepted ones
Write each accepted lesson into `lessons/` from `lessons/_template.md`:
- **Filename: version-pure**, full patch level, e.g. `13.17-….md`. **No topic slug** (a release
  aggregates many changes — picking one would be arbitrary). The version prefix deliberately breaks
  the `01/02/03…` sequence; that makes an upstream collision *visible and expected*.
- **YAML frontmatter (generated lessons only):** `version: <x.y.z>`, `origin: local`, and
  `title: <slug>` — a **concise** kebab-case slug capturing the concept, not a full transcription
  of the `# Lesson X.Y — <title>` heading: drop prepositions/filler ("from", "with", "your") and
  parenthetical technical detail (a method name, a class), keep it to **2–4 words**. E.g. "HTML
  password rules from your validation rules" → `html-password-rules`, "Bulk job dispatch with
  Bus::bulk()" → `bulk-job-dispatch` (the `Bus::bulk()` detail belongs in the lesson body, not
  the menu row). Write it **once, here, at generation time** — it is the single source of truth
  for how the lesson's title is displayed everywhere downstream (the `teach-lesson` menu reads
  this field rather than re-deriving it from the heading). Do **not** retrofit the 12 existing
  lessons (ADR-0006).
- **Brief in the `language.docs` language (English).** HTML render stays a later `/teach` step.
- **Generate in default mode, never Learn by Doing (ADR-0009).** Lesson generation is *content
  authoring*, not co-writing code on a design decision — so the `Learning` output style does **not**
  apply here. Emit **complete** briefs: never a `TODO(human)` block or placeholder line.

### 6. Update state (only for what actually happened)
- Advance `laravel_version_scanned` to the highest version examined.
- Advance `laravel_version_covered` **only** for versions actually generated.
- Append declined versions to `lessons_skipped`.
- Set `last_checked` to today.

## Collision with upstream

The clash is **semantic, not same-file**: upstream lessons are progressively named (`01…12`),
generated ones are version-named, so a `git`-level conflict is unlikely. The real collision is "the
same *version* is now covered by both a local and an upstream lesson."

- **Detect by `version:`**, not filename: compare the `version:` frontmatter of `origin: local`
  files against upstream lessons' version, parsing their prose **`> Version:` line** (e.g.
  `> Version: Laravel 12.x, through 12.19 · Type: new`) as a best-effort fallback.
- On a duplicate version, **flag it and offer the choice — default: keep both** (non-destructive,
  always safe). **Merge** (combine into one file) is **explicit opt-in only** — auto-combining
  content is the riskiest move in the flow.

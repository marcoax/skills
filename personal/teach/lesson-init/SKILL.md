---
name: lesson-init
description: One-shot setup for this Laravel 12→13 workspace — interviews you, then writes learning-config.md. Run once per fork.
disable-model-invocation: true
argument-hint: "(no arguments — it interviews you)"
---

`/lesson-init` is a one-shot bootstrap, run once per fork, distinct from `/teach` (which runs
the lessons). Interview the learner, then write one file:

**`learning-config.md`** at the repo root — the per-user, git-ignored config every later
session treats as authoritative (see `CLAUDE.md` → *Config binding*, ADR-0001/0003).
The `output_style` recorded there is applied by `lesson`/`/teach` during lesson
sessions only (ADR-0020) — no settings file is written for it.

First read `learning-config.example.md` (the tracked schema) and `CONTEXT.md`, so your output
matches the canonical field names and the repo's vocabulary.

## Step 1 — Detect first-run vs re-run

Before asking anything, check whether `learning-config.md` already exists at the repo root.

- **Absent** → first run. You will create it from `learning-config.example.md`.
- **Present** → re-run / update. Read it and parse the current YAML values; use them as the
  pre-filled defaults in the interview. See *Re-running* below for the reconciliation rule.

## Step 2 — Interview, one question at a time

Ask **one question per turn** with `AskUserQuestion`. Each question's **first option is the
recommended default, labelled "(recommended)"**, so the learner can accept the whole setup
quickly. Ask `language` (#1) **first** — it sets the language for the rest of the interview;
phrase every later question in the learner's chosen `chat` language, but keep the YAML field
names in English. On a re-run, each recommended default is the learner's *current* value, not
the template default.

| # | Field | Recommended default | Notes / options |
|---|-------|---------------------|-----------------|
| 1 | `language` | `chat: en`, `docs: en` | Ask first. `chat` = conversation + HTML lessons (learner-facing); `docs` = project Markdown. Offer for `chat`: **English (recommended)**, Italian, French, German, Spanish. `docs` defaults to English. |
| 2 | `output_style` | `Learning` | **Learning** = Learn by Doing (scaffold + `TODO(human)`, recommended). Other choices: `Explanatory` (teaches while writing — full code plus didactic notes) or `default` (concise, no pedagogy). Written to `learning-config.md`; `lesson`/`/teach` apply it for the duration of a lesson session (ADR-0020). Never written to settings files. |
| 3 | `reference_project` | *(no default — ask)* | Absolute path to the real codebase assessed each lesson. If they have none, store a placeholder and steer `practice_default` to `concepts-only`. **Never suggest, guess, or illustrate this with a real absolute path** (yours, the learner's, or one seen earlier in the session/repo) — if an example is useful, use only the generic placeholder from `learning-config.example.md`: `/absolute/path/to/your/project`. |
| 4 | `model` | *(the model running this session)* | **Advisory only** — a file can't force the CLI model. Recommend **the model powering the current session** as the default, and other models of **its own family** as alternatives; do not sniff the environment or map agents to models — self-reference only (ADR-0021). If your environment has relevant execution modes (e.g. fast / extended), mention them in the suggestion. Just record the choice. |
| 5 | `course_baseline_major` | `12` | Static choices only: `12` \| `13`. `12` preserves the full authored Laravel 12 -> 13 path; `13` starts the active learner-facing path at Laravel 13 and hides 12.x material. This is not a generic `from_major -> to_major` engine. |
| 6 | `practice_default` | `concepts-only` | `concepts-only` \| `throwaway-app` \| `reference-project`. |
| 7 | `quiz_format` | `recall` | `recall` (open question → accordion answer) \| `multiple-choice`. |
| 8 | `deep_dive` | `on` | Offer the optional "want to go deeper?" invite at lesson end. `on` \| `off`. |
| 9 | `branch_convention` | `one branch per generated brief, e.g. lesson-<x.y.z>-<slug>` | Free text; the **branch-name pattern**. Consulted only by `/lesson-update`, when `auto_branch` is `on` (ADR-0017). |
| 10 | `auto_branch` | `on` (base `main`) | Ask whether `/lesson-update` should open a branch **from `main`** for each generated brief. `on` \| `off`. When `on`, the branch name follows `branch_convention` (the learner may override the pattern); when `off`, briefs land on the current branch. Consulted **only by `/lesson-update`** — teaching sessions never cut branches (their output is all git-ignored, ADR-0017). `/lesson-init` only **records** the choice — it never creates the branch. |
| 11 | `auto_check_new_lessons` | `on` | Ask whether to auto-check for newer Laravel releases **in the background at lesson completion** (ADR-0007). `on` \| `off`. When `on`, finishing a lesson fires a read-only discovery sub-agent that proposes new lessons (never generates them); when `off`, nothing fires and `/lesson-update` stays manually invocable. Fail-soft: a failed check is skipped silently. |

## Step 3 — Write `learning-config.md`

Render the answers into the YAML block, preserving the structure and the explanatory
comments from `learning-config.example.md` (the file is documentation outside the block,
YAML inside). Keep the `# --- Essentials ---` / `# --- Pedagogy ---` sections. Persist
`course_baseline_major` next to the language block in Essentials. Persist `auto_branch`
(with its base branch) next to `branch_convention` in the pedagogy section.

Also write the `# --- Lesson updates (/lesson-update) ---` section. Only
`auto_check_new_lessons` comes from the interview (question #11); the rest is **seeded
state**, not preferences — copy the defaults verbatim from `learning-config.example.md`:

- `lesson_sources` — the **structured** source list, one `transport` per source (+ optional
  `fallback_url`); copy the full shape verbatim (ADR-0010/0011).
- `lesson_changelog` — `laravel/framework` (cross-check only).
- `laravel_version_scanned` / `laravel_version_covered` — both seed to the version the 12
  existing lessons reach (currently `"13.8"`).
- `lessons_skipped` — `[]`.
- `last_checked` — `null` (never run yet).

Never prompt for these seeded fields. A fresh config starts from the values above; on a re-run
they are preserved per the *Re-running* rule (only `auto_check_new_lessons` is re-asked).

## Step 4 — Do not touch settings files (ADR-0020)

`output_style` lives in `learning-config.md` only; `lesson`/`/teach` apply it during
lesson sessions. Do **not** write `outputStyle` to `.claude/settings.json` (it stays neutral,
`{}`) or to `.claude/settings.local.json` — the latter is the learner's personal,
general-work preference and is none of this skill's business. If the learner has a stale
`outputStyle` there from an older setup, mention it once; changing it is their call.

## Re-running (update mode)

When `learning-config.md` already exists, you must reconcile the new answers with the
existing learner state rather than blindly overwriting it (acceptance criterion in issue #4,
ADR-0002):

1. **Pre-fill, don't reset.** Parse the current `learning-config.md` YAML and use each
   stored value as that question's recommended default (first option, "(recommended)").
   The learner re-confirms or overrides each field; accepting the default is a no-op.
2. **Write back the full file, but only with confirmed values.** Every field keeps its
   existing value unless the learner explicitly changes it — no field is dropped or blanked
   just because it wasn't touched.
3. **Respect hand-edits.** If a stored value differs from the template default, assume it
   was set deliberately (by `/lesson-init` or by hand) and preserve it; never silently
   replace a non-default value with the template default.
4. **Surface conflicts, don't guess.** If `learning-config.md` is malformed or a value is
   unparseable, show the learner what you found and ask before overwriting that field.
5. **`model` on re-run.** The stored `model` stays the recommended first option (rule 1); the
   model running the current session is offered as a clearly *labelled* alternative (e.g.
   "the model running now") — it never silently replaces a stored value (ADR-0021).

## Step 5 — Confirm and hand off

Summarise the written config back to the learner (in their chosen `chat` language), note that
the chosen `output_style` will apply during lesson sessions (ADR-0020), and point them to
`/lesson` to start the course. Never surface bare `/teach` to the learner — it is the
internal engine; `lesson` is the learner-facing launcher. Do **not** run a lesson
here — `/lesson-init` only bootstraps.

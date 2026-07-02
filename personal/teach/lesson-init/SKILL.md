---
name: lesson-init
description: One-shot setup for this Laravel 12→13 workspace — interviews you, then writes learning-config.md and the local output-style override. Run once per fork.
disable-model-invocation: true
argument-hint: "(no arguments — it interviews you)"
---

`/lesson-init` is a one-shot bootstrap, run once per fork, distinct from `/teach` (which runs
the lessons). Interview the learner, then write two files:

1. **`learning-config.md`** at the repo root — the per-user, git-ignored config every later
   session treats as authoritative (see `CLAUDE.md` → *Config binding*, ADR-0001/0003).
2. **`.claude/settings.local.json`** — the git-ignored, higher-precedence file that *enforces*
   the chosen output style.

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
| 2 | `output_style` | `Learning` | **Learning** = Learn by Doing (scaffold + `TODO(human)`, recommended). Other choices: `Explanatory` (teaches while writing — full code plus didactic notes) or `default` (concise, no pedagogy). Written to `settings.local.json`, **not** to `learning-config.md`, as the enforcement point. |
| 3 | `reference_project` | *(no default — ask)* | Absolute path to the real codebase assessed each lesson. If they have none, store a placeholder and steer `practice_default` to `concepts-only`. |
| 4 | `model` | `claude-opus-4-8` (+ Fast mode) | **Advisory only** — a file can't force the CLI model. Just record it. |
| 5 | `practice_default` | `concepts-only` | `concepts-only` \| `throwaway-app` \| `reference-project`. |
| 6 | `quiz_format` | `recall` | `recall` (open question → accordion answer) \| `multiple-choice`. |
| 7 | `deep_dive` | `on` | Offer the optional "want to go deeper?" invite at lesson end. `on` \| `off`. |
| 8 | `branch_convention` | `one branch per lesson, e.g. lesson-NN-<slug>` | Free text; the **branch-name pattern**. Consulted only when `auto_branch` is `on`. |
| 9 | `auto_branch` | `on` (base `main`) | Ask whether each lesson should open a branch **from `main`**. `on` \| `off`. When `on`, the branch name follows `branch_convention` (the learner may override the pattern); when `off`, work stays on the current branch. `/lesson-init` only **records** the choice — it never creates the branch; `/teach` cuts it at lesson start. |
| 10 | `auto_check_new_lessons` | `on` | Ask whether to auto-check for newer Laravel releases **in the background at lesson completion** (ADR-0007). `on` \| `off`. When `on`, finishing a lesson fires a read-only discovery sub-agent that proposes new lessons (never generates them); when `off`, nothing fires and `/lesson-update` stays manually invocable. Fail-soft: a failed check is skipped silently. |

## Step 3 — Write `learning-config.md`

Render the answers into the YAML block, preserving the structure and the explanatory
comments from `learning-config.example.md` (the file is documentation outside the block,
YAML inside). Keep the `# --- Essentials ---` / `# --- Pedagogy ---` sections. Persist
`auto_branch` (with its base branch) next to `branch_convention` in the pedagogy section.

Also write the `# --- Lesson updates (/lesson-update) ---` section. Only
`auto_check_new_lessons` comes from the interview (question #10); the rest is **seeded
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

## Step 4 — Write the output style to `.claude/settings.local.json`

This file is git-ignored and already exists with a `permissions` block. You **must merge**,
never overwrite: read the current JSON, set the top-level `"outputStyle"` key to the chosen
value, and preserve every other key (especially `permissions`). The tracked
`.claude/settings.json` stays neutral (`{}`) — do not write the style there.

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

## Step 5 — Confirm and hand off

Summarise the written config back to the learner (in their chosen `chat` language), confirm the output style is
active via `settings.local.json`, and point them to `/teach` to start lesson 01. Do **not**
run a lesson here — `/lesson-init` only bootstraps.

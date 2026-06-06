---
name: goal-spec-review
description: Pre-flight audit of a /goal spec: verifies that objectives are clear and fixed, and that completion criteria are explicit and checkable BEFORE coding begins. Use when the user invokes /goal with a spec file or inline plan. If objectives are vague or success criteria are missing or unverifiable, stop and ask — do not start coding until the user has defined how "done" will be measured. Safety checks are mandatory and cannot be skipped. For deeper stress-testing of objectives and criteria, escalate to grill-with-docs.
---

# Goal Spec Review

A 30-second audit prevents silent wrong decisions during implementation.

Skip only if the user says "skip review" or "just implement it".
**Safety checks (§ Safety) are never skippable.**

## Procedure

Invocation: `/goal implement path/to/plan.md`

1. Read the spec end-to-end. No codebase exploration yet.
2. Verify concrete claims (paths, IDs, symbols) with one quick pass.
3. **Objective gate** — objectives must be clear and fixed. If vague → stop and ask.
4. **Completion-criteria gate** — every objective needs a concrete, checkable signal of
   done (a command that passes, an observable output, a file/state that exists). If
   missing or unverifiable → stop and ask, or escalate to `grill-with-docs`. Never
   proceed on an unmeasurable goal.
5. **Safety check** (§ Safety) — block on destructive actions, sensitive-data exposure,
   or security bypasses.
6. Output the unclear points and **wait** for answers. If clean, say so and proceed.

## Safety

Stop and require explicit approval — do not infer intent — if the spec involves:

- **Destructive actions** (delete, drop, overwrite, reset) without confirmation.
- **Sensitive-data exposure** (credentials, PII, secrets) in logs, output, or files.
- **Security violations** (bypassing auth, disabling checks, unauthorized paths).

## Language

Write the review in the same language as the spec.

## What to flag

**Rule: only flag points that change _what_ gets built, not _how_.**

- **Objectives without checkable criteria** — no definition of done, or "works correctly" / "verify manually" when an automated check is feasible.
- **Spec/code contradictions** — e.g. spec says id 56 is a time field, code shows Date.
- **Lists/mappings that don't add up** — counts, ranges, items in the wrong bucket.
- **Open questions** — anything "to decide", or two conflicting instructions in one bullet.
- **Scope edges with no decision** — e.g. "patch related files too?" needs a yes/no.
- **Dangling references** — files/IDs/symbols that don't exist in the current branch.
- **Complex transforms without a worked example** — wire↔UI, encode/decode, format conversions need an input→output example per direction.

**Don't flag:** style/naming taste, hypotheticals not in the spec, details left to your judgment, or anything one grep/read resolves — just resolve it silently.

## Output format

    ## Spec review — <plan name>

    Found <N> point(s) to clarify before I start:

    1. **<short title>** — <one-line ambiguity>.
       Why it matters: <one-line impact>.

    Please confirm each before I proceed.

If clean: `## Spec review — <plan name>` then `No ambiguities. Starting implementation.`

Keep each point to 2 lines. **Hard cap: 7 points** — if you'd list more, recommend
`grill-with-docs`; the spec needs rework, not clarification.

## Escalation

Suggest `grill-with-docs` when completion criteria are too vague to measure, or when
there are more than 3 structural ambiguities (points that change _what_ gets built):

> The spec has several structural gaps. Want to run `grill-with-docs` for a deeper
> stress-test before I start?

Don't suggest this for cosmetic ambiguities.

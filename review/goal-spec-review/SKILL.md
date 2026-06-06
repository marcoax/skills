---
name: goal-spec-review
description: Pre-flight audit of a /goal spec: verifies that objectives are clear and fixed, and that completion criteria are explicit and checkable BEFORE coding begins. Use when the user invokes /goal with a spec file or inline plan. If objectives are vague or success criteria are missing or unverifiable, stop and ask — do not start coding until the user has defined how "done" will be measured. Safety checks are mandatory and cannot be skipped. For deeper stress-testing of objectives and criteria, escalate to grill-with-docs.
---

# Goal Spec Review

A 30-second audit prevents silent wrong decisions during implementation.

Skip only if the user explicitly says "skip review" or "just implement it".
**Safety checks (§ Safety) are never skippable.**

## Quick start

User invokes: `/goal implement path/to/plan.md`

1. Read the spec end-to-end.
2. **Verify objectives are clear and fixed** — if not, ask before proceeding.
3. **Verify completion criteria are explicit and checkable** — if missing, ask or escalate to `grill-with-docs`.
4. **Run safety check** — block and ask if the plan involves destructive actions, sensitive data exposure, or security bypasses.
5. Return the review block or `No ambiguities. Starting implementation.`

## Language

Write the review in the same language as the spec.
Italian spec → Italian review. English spec → English review.

## Safety

Before any implementation, verify the spec does not require:

- **Destructive actions** (delete, drop, overwrite, reset) without explicit user confirmation.
- **Exposure of sensitive data** (credentials, PII, secrets) in logs, output, or intermediate files.
- **Security violations** (bypassing auth, disabling checks, writing to unauthorized paths).

If any of these are present or implied: stop immediately and ask the user to confirm
exactly what they want. Do not infer intent — require explicit approval.

## Procedure

1. Read the spec end-to-end. No codebase exploration yet.
2. Verify concrete claims (paths, IDs, symbols) with one quick pass — not a full exploration.
3. Produce a short numbered list of unclear points: one line for the ambiguity, one line for why it matters.
4. Stop and wait for the user to answer before implementing.
5. If clean, say so in one sentence and proceed.

## What counts as an "unclear point"

- **Objectives without completion criteria** — "implement X" with no definition of what X completed means. Ask: how will we verify the goal is reached?
- **Contradictions between spec and code** — spec says id 56 is a time field, code shows Date. Ask which is the source of truth.
- **Lists or mappings that don't add up** — counts, ranges, or items in the wrong bucket.
- **Open questions left by the author** — anything marked "to decide" or two conflicting instructions in the same bullet.
- **Scope edges with no decision** — e.g. "patch related files too?" needs a yes/no.
- **Verification criteria that aren't checkable** — "verify manually" when an automated check is feasible.
- **References to files/IDs/symbols that don't exist** in the current branch.
- **Complex transformations without a worked example** — any wire↔UI, encode/decode, or format conversion needs an input→output example per direction.

## What NOT to flag

- Style preferences, naming taste, hypothetical edge cases not in the spec.
- Implementation details the spec deliberately left to your judgment.
- Anything you can resolve with one grep or file read — just resolve it.

## Output format

    ## Spec review — <plan name>

    Found <N> point(s) to clarify before I start:

    1. **<short title>** — <one-line ambiguity>.
       Why it matters: <one-line impact>.

    2. ...

    Please confirm each before I proceed.

If clean:

    ## Spec review — <plan name>
    No ambiguities. Starting implementation.

Keep each point to 2 lines. **Hard cap: 7 points.** If you'd list more, recommend
`grill-with-docs` instead — the spec needs rework, not clarification.

## Escalation

If completion criteria are missing or too vague to measure → suggest `grill-with-docs`
to interview the user and establish them before proceeding.

If more than 3 structural ambiguities (points that change *what* gets built, not *how*):

> The spec has several structural gaps. Want to run `grill-with-docs` for a deeper stress-test before I start?

Don't suggest this for cosmetic ambiguities.

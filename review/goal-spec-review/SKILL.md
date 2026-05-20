---
name: goal-spec-review
description: Pre-flight review of an implementation spec/plan for unclear, contradictory, or missing points BEFORE starting a /goal execution. Triggers specifically when the user invokes /goal with a path to a spec file (e.g. `/goal implement path/to/plan.html|md`). Always run this skill first in that case — do not start coding until the user has resolved the listed ambiguities. For deeper interactive stress-testing, escalate to grill-me or grill-with-docs (domain-model).
---

# Goal Spec Review

Before executing a plan, audit it for ambiguity. A 30-second review prevents silent wrong decisions during implementation.

Skip only if the user explicitly says "skip review" or "just implement it".

## Procedure

1. Read the spec end-to-end. No codebase exploration yet.
2. Verify concrete claims (paths, IDs, symbols) with one quick pass — not a full exploration.
3. Produce a short numbered list of unclear points: one line for the ambiguity, one line for why it matters.
4. Stop and wait for the user to answer before implementing.
5. If clean, say so in one sentence and proceed.

**Language:** write the review in the same language as the spec (Italian spec → Italian review).

## What counts as an "unclear point"

- **Contradictions between spec and code** — spec says id 56 is a time field, code shows Date. Ask which is the source of truth.
- **Lists or mappings that don't add up** — counts, ranges, or items in the wrong bucket.
- **Open questions left by the author** — anything marked "to decide" or two conflicting instructions in the same bullet.
- **Scope edges with no decision** — e.g. "patch related files too?" needs a yes/no.
- **Verification criteria that aren't checkable** — "verify manually" when an automated check is feasible.
- **References to files/IDs/symbols that don't exist** in the current branch.
- **Data transformations without a worked example** — any wire↔UI, encode/decode, or format conversion needs an input→output example per direction (e.g. `36000 → "10:00"` AND `"08:30" → 30600`).

## What NOT to flag

- Style preferences, naming taste, hypothetical edge cases not in the spec.
- Implementation details the spec deliberately left to your judgment.
- Anything you can resolve with one grep or file read — just resolve it.

## Output format

```
## Spec review — <plan name>

Found <N> point(s) to clarify before I start:

1. **<short title>** — <one-line ambiguity>.
   Why it matters: <one-line impact>.

2. ...

Please confirm each before I proceed.
```

If clean: `## Spec review — <plan name>\nNo ambiguities. Starting implementation.`

Keep each point to 2 lines. **Hard cap: 7 points.** If you'd list more, stop and recommend `grill-with-docs` instead — the spec needs rework, not clarification.

## Escalation

If the list contains **more than 3 structural ambiguities** (points that change *what* gets built, not *how*), append:

> The spec has several structural gaps. Want to run `grill-with-docs` for a deeper stress-test before I start?

Don't suggest this for cosmetic ambiguities.

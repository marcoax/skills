# Severity rubric and verdict rules

One rubric. Assign the **first** matching severity, top-down — they never overlap.

| Severity | Blocking | Assign when |
|---|---|---|
| `BLOCKER` | yes | A spec requirement is not met; data loss or corruption is possible; a security defect at a trust boundary (injection, missing auth/authz, exposed secret, unvalidated external input); a required check produced failure evidence; a test that covers a spec requirement is skipped, disabled, or non-representative; work outside the spec was added or deleted (scope creep / gold-plating). |
| `HIGH` | yes | A probable bug in the reviewed scope, an unhandled case the spec names, a plausible regression in existing behaviour, or a performance risk you can point to in the diff. |
| `MEDIUM` | no | An in-scope robustness, error-handling or type-safety weakness that does not break the spec. |
| `LOW` | no | An in-scope minor issue: naming, duplication, small conventions. |
| observation | never | Anything outside the spec and reviewed scope: style preference, refactor idea, speculative abstraction, missing feature nobody asked for. Lives in the non-blocking section, excluded from every count that drives the verdict. |

Scope creep is `BLOCKER`, not a compliment: over-delivery hides bugs in untested surface and is a
defect against the spec. Three similar lines beat a premature abstraction.

## Evidence classes

| Class | Meaning |
|---|---|
| `VERIFIED` | You observed it — read the line, ran the command, saw the output. Requires a `file:line` (or command) citation. |
| `INFERRED` | Your reasoning from what you read, not directly observed. Say so. |
| `UNVERIFIED` | You could not check it. State what was missing. Never upgrade to VERIFIED by assumption. |

A developer's statement ("all tests pass", "it works", "no need for tests") is never evidence at any
class. Quote it as a claim, then verify it or mark it `UNVERIFIED`.

## Verdict rules

Deterministic, evaluated top-down; the renderer enforces them and exits non-zero on a violation.

1. **`FAIL`** — at least one `BLOCKER` finding, or any verification entry with `status: fail`.
2. **`PARTIAL`** — no `BLOCKER` and no failed check, but at least one `HIGH` finding, or at least one
   verification entry with `status: not_run`. Must list explicitly which checks passed with evidence
   and which failed or could not be run.
3. **`PASS`** — no `BLOCKER`, no `HIGH`, every verification entry `status: pass`, and at least one
   verification entry exists.

Consequences that are not negotiable:

- No verification performed at all ⇒ never `PASS`. The absence of runnable checks is recorded as a
  `not_run` entry, which forces `PARTIAL` at best.
- `PARTIAL` is never a hedge for unease. Without failure evidence or an unrun check, you do not have a
  `PARTIAL` — you have a `PASS` with `MEDIUM`/`LOW` findings.
- `MEDIUM`, `LOW` and observations never change the verdict.
- A confirmed `PASS` is stated plainly. No "but you might want to…".
- Strengths, remediation and applied fixes never re-open or improve a frozen verdict. A re-review after
  fixes is a new review with new evidence and its own `review.json`.

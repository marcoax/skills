# Severity rubric and verdict rules

Assign the first matching severity, top-down. Field names below apply to exported records; inline
reports convey the same evidence without requiring a JSON structure.

| Severity | Blocking | Assign when |
|---|---|---|
| `BLOCKER` | yes | A spec requirement is not met; data loss or corruption is possible; a security defect at a trust boundary (injection, missing auth/authz, exposed secret, unvalidated external input); a required check produced failure evidence; a test that covers a spec requirement is skipped, disabled, or non-representative; work outside the spec was added or deleted (scope creep / gold-plating). |
| `HIGH` | yes | A probable bug in the reviewed scope, an unhandled case the spec names, a plausible regression in existing behaviour, or a performance risk you can point to in the diff. |
| `MEDIUM` | no | An in-scope robustness, error-handling or type-safety weakness that does not break the spec. |
| `LOW` | no | An in-scope minor issue: naming, duplication, small conventions. |
| observation | never | Anything outside the spec and reviewed scope: style preference, refactor idea, speculative abstraction, missing feature nobody asked for. Lives in the non-blocking section, excluded from every count that drives the verdict. |

Scope creep means a demonstrated addition or deletion outside the requested behavior, not every
helper or file absent from the ticket. Necessary supporting changes belong to the implementation;
use inspection or a focused experiment when necessity is disputed. Non-functional incidental changes
are `LOW` when worth reporting, with separation suggested only when useful.

A spec requirement with **no test at all** is `MEDIUM` when another check you ran verifies that
behaviour anyway, and `HIGH` when nothing does. Record it in `test_audit` as `missing` **and** as a
finding with `basis: test_coverage` — a gap that cannot change anything is a gap nobody will look for.

A defect copied into new code is in scope; classify its actual impact using the rubric. An untouched
pre-existing defect is a baseline observation unless the change makes it newly reachable or worse.

## Evidence classes

| Class | Meaning |
|---|---|
| `VERIFIED` | You observed it — read the line, ran the command, saw the output. Requires a `file:line` (or command) citation. |
| `INFERRED` | Your reasoning from what you read, not directly observed. Say so. |
| `UNVERIFIED` | You could not check it. State what was missing. Never upgrade to VERIFIED by assumption. |

A developer's statement ("all tests pass", "it works", "no need for tests") is never evidence at any
class. Quote it as a claim, then verify it or mark it `UNVERIFIED`.

This applies to every claim in the record, not only to findings: an observation or a strength that
points at a `file:line` carries its evidence class too. The strongest sentences in a review are often
the ones nobody asked to justify.

## The law a blocking finding invokes

Every `BLOCKER` and `HIGH` declares its `basis`. When that basis is a spec criterion or a documented
standard, the criterion must appear **verbatim** in `criteria[]`, or the rule in `standards[]` with the
`file:line` of the document that states it. A claimed spec or standards violation needs that source;
a concrete defect can instead use one of the independent bases below.

Only three bases need no written rule, because they are defects regardless of what anyone documented:
`defect` (bug, data loss, security at a trust boundary), `scope_creep`, `test_coverage`.

An applicable mandatory rule **written** in the repo's docs and broken by the diff blocks, and cites
the document. Distinguish mandatory rules from recommendations. A
convention that is widespread in the code but written nowhere does not block: it is an observation.

Quoting is not enough: **provenance decides what a sentence is.** Every criterion declares `kind` —
`acceptance` for what the spec asks for, `context` for what it explains, motivates or describes — and
`from`, the heading it was taken from. A blocking finding may only cite an `acceptance` criterion. A
clause lifted verbatim from the rationale is at most `LOW`, and when it pulls against something the
spec actually asks for, it is a decision to hand over, not a verdict to issue.

Two criteria that contradict each other on the same behaviour are not yours to resolve. Record both
with their real status, and hand the decision over instead of picking a side in silence.

## What a check's `status` and `target` mean

`status` is **your judgment of the outcome**, not the command's exit code. `target` says what the check
judges: the diff under review (`change`), or the repo you inherited (`baseline`).

A command that exits non-zero for errors the diff did not introduce is `status: fail` with
`target: baseline`. It never fails the review, and it never leaves the report either — it renders as
failed *and* pre-existing. When you cannot tell which one a red belongs to, run the check on the base
and on `HEAD` and compare: the difference is the answer.

## Verdict rules

Apply these rules to inline and exported reviews alike. The renderer enforces the verdict calculation
for exported records.

1. **`FAIL`** — at least one `BLOCKER` finding, or a verification entry with `status: fail` **and
   `target: change`**.
2. **`PARTIAL`** — no `BLOCKER` and no failed check on the change, but at least one `HIGH` finding, or
   at least one verification entry with `status: not_run`. Must list explicitly which checks passed
   with evidence and which failed or could not be run.
3. **`PASS`** — no `BLOCKER`, no `HIGH`, at least one verification entry, and every entry is
   `status: pass` or a `fail` with `target: baseline`.

For an acceptance criterion that could not be checked, record `criteria[].status: "unverified"` and
the necessary missing verification as a `not_run` entry. The latter makes the verdict at best
`PARTIAL`; the renderer does not infer it from criterion status alone. If the spec is unavailable,
state that completeness is unassessed; record a missing assessment when completeness was requested
rather than inventing criteria. For a correctness-only review, a missing feature spec alone is not a
failed or missing check.

Consequences that are not negotiable:

- No verification performed at all ⇒ never `PASS`. The absence of runnable checks is recorded as a
  `not_run` entry, which forces `PARTIAL` at best.
- `PARTIAL` is never a hedge for unease. Without failure evidence or an unrun check, you do not have a
  `PARTIAL` — you have a `PASS` with `MEDIUM`/`LOW` findings.
- A red you inherited never fails the review, and never disappears from it. Running more checks on a
  repo with existing debt must not make a correct change harder to pass.
- `MEDIUM`, `LOW` and observations never change the verdict.
- A confirmed `PASS` is stated plainly. No "but you might want to…".
- A verdict describes a particular state. After fixes, assess the new state with new evidence; when
  exporting, use a new `review.json` rather than overwriting the original assessment.

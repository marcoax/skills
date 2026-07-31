# Review playbook

Load this when running a review. Severity and verdict rules live in
[severity-and-verdict.md](severity-and-verdict.md); the data schema in
[output-contract.md](output-contract.md).

## Stage 0 — scope and spec

Collect what is missing, nothing more. Ask once, in the user's language.

```
1. file   2. uncommitted changes   3. commit   4. branch diff
```

| Scope | Evidence commands |
|---|---|
| file | `git diff HEAD -- <path>`; if empty, `git diff HEAD~1 -- <path>`; if still empty, review the whole file as new code |
| uncommitted | `git status --short`, `git diff`, `git diff --cached` |
| commit | `git show <hash> --stat`, `git show <hash>` |
| branch | `git diff <base>..HEAD --stat`, `git diff <base>..HEAD` — `<base>` is exactly what the user typed |

A branch diff with ≥10 files: show `--stat` and ask whether to review all at once or file by file.

Read the repo's own standards (`CLAUDE.md`, `AGENTS.md`, contributing docs, lint config): they are the
second source of law, recorded in `standards[]` with the `file:line` that states each rule. If none
exist, say so and use general practice for the language — do not invent house rules.

On a large diff, gather spec evidence and standards evidence in separate contexts, and never let one
axis reorder the other's findings. If earlier reports on the same scope exist, cite them and reconcile
the divergences on the merits — declaring your own precedence is not reconciling.

## Stage 1 — scope audit

*Did the change deliver more than the spec asked?* Cite `file:line` for each:

- helpers, utilities, wrapper classes, or config options the spec never mentions
- refactors or renames of code that was neither broken nor in scope
- an abstraction introduced to replace three or fewer similar lines
- generalisation "for later": hooks, flags, extension points with one caller
- deletions outside the requested change

Clean stage: say so plainly.

## Stage 2 — correctness and risk

*Does this do what the spec says, or only look like it does?* Read as an attacker and as a maintainer:

- every case the spec describes, including the ones the happy path skips
- off-by-one, null/empty/zero, unbounded input, unexpected types, concurrency and transaction gaps
- trust boundaries: injection, authn/authz, secrets, unvalidated external input, unsafe deserialisation
- regressions: what else calls the changed function? Grep the callers before judging a local change safe
- performance you can point at in the diff: N+1 queries, work inside loops, needless re-renders, leaks
- error handling the spec demands but the code omits

### Complexity signals

Four signals worth naming when you see them. Their severity is **relative to the spec**, so read the
mapping before classifying — the rubric itself stays in
[severity-and-verdict.md](severity-and-verdict.md).

| Signal | How to classify |
|---|---|
| A complicated implementation where a cleaner reframing would delete whole categories of complexity | Non-blocking observation. Name the reframing in one sentence so it is actionable, then stop — designing it is `improve-codebase-architecture`'s job, not a required fix. |
| A refactor that moves code around without reducing the number of concepts a reader must hold | `BLOCKER` when simplification *was* the spec — the stated goal is unmet, and churn was shipped instead. Plain scope creep (`BLOCKER`, stage 1) when the refactor was never requested. Observation only when it rode along inside a change that had to touch those lines anyway. |
| The diff duplicates a rule across several callers, or copies a structure that now recurs identically elsewhere | Not verdict material: two defensible options, so it goes to `for_human_review` (stage 4) — name the sibling code and what the next change will cost. |
| New conditionals bolted onto unrelated code paths | `BLOCKER` when the touched path is outside the spec: an unrequested branch in unrelated code is scope creep with untested surface. Otherwise `MEDIUM`/`HIGH` depending on the regression risk it adds to the callers you grepped. |

Do not let these signals pull the review into a redesign. You name the signal with `file:line`, you do
not require the redesign.

### Parking an observation as an issue

A non-blocking observation that is real but out of scope — the module split behind an oversized file is
the usual case — can be offered as a tracking issue instead of being dropped or smuggled into the
required fixes:

> "O2 (splitting `Invoice.php`, now 1140 lines) is out of scope for this spec. Want me to open an issue
> for it?"

Offer once, at the end, only for observations worth someone's time. Then:

- **approved** — create it with the repo's own tracker (`gh issue create` when `gh` is authenticated and
  a remote exists). Title, the `file:line` anchors, why it matters, and the proposed split. No fix plan
  beyond that, and never a promise about when.
- **no tracker available** — hand over the issue text in chat for the user to paste. Do not invent a
  local backlog file.
- **declined or unanswered** — the observation stays in the report. That is already a durable record.

The issue is a side effect on a tracker: it needs the same explicit approval as a code fix, and its
existence never changes the verdict or the count of blocking findings.

Framework-specific checks are your judgment call — React re-render/effect rules, Laravel eager loading,
Blazor dispose, Go error wrapping, and so on. Match what the code actually uses.

## Stage 3 — independent verification

Run the checks yourself; a claim is not a check. Typical: the repo's test command
(`npm test`, `pytest`, `php artisan test`, `go test ./...`), the type checker, the linter, a build.
Record the exact command and the real output for each — that becomes `verification[]`.

Then audit the suite itself:

- tests marked `skip`, `xit`, `todo`, `xfail`, `@Ignore`, `@Disabled`, commented out, or filtered away
- assertions that exercise trivia instead of the spec's requirements
- tests shaped after the implementation, asserting what the code does rather than what the spec requires
- a spec requirement with no test at all

Three techniques, none tied to a language:

- **the tests are new and the spec is about a guard or a condition** — remove the condition, re-run,
  restore. A test that still passes does not cover the requirement.
- **a change looks out of spec** — remove it, re-run, restore. If something the spec requires breaks,
  the change is enabling rather than creep, and the proof goes in the record.
- **the criterion is "N things line up" or "this artefact is consumable"** — do not count by eye: let a
  script count, or hand the artefact to the system that must consume it.

**Protocol, not negotiable.** These write into the workspace. Before: a clean tree — otherwise skip
them and record `not_run` with the reason. After each experiment: restore, and check the diff is empty
again. Throwaway resources created for a check (a scratch database, a temp file) need no approval when
they carry a dedicated name and are destroyed in the same step; any persistent write to the repo or to
a tracker still does.

Cannot run a check (no deps, no environment, no network, read-only diff)? Record it as
`status: not_run` with the reason. Never write a command you did not execute as if it had passed, and
never paste a developer-supplied output as your own verification — quote it as a claim and verify it.

## Stage 4 — verdict, then remediation

Freeze the verdict from stages 1–3. Only then assemble strengths, required fixes (minimum to clear
the blocking findings, each with WHY and HOW), and non-blocking observations. Write `review.json`,
render, and present the chat summary. Fixes and test generation wait for explicit approval.

### Handing a decision back

Last, after remediation is settled: up to three design decisions you could not settle. Emit one when

- the diff replicates a sibling implementation and the spec forbids unifying them *now*
- the same rule now lives in several callers, and the next change will touch them all again
- two acceptance criteria contradict each other on the same behaviour
- **you applied a rule this rubric does not contain** — every exception you had to invent is, by
  definition, a decision that was never yours

Name the decision, both defensible options, and the sibling code it hinges on. Do not design the
answer: you are handing over a question, not a task. Then ask whether to go through them, one at a
time. These never touch the verdict and never enter the fix menu.

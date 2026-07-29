---
name: advanced-code-review
description: >
  Evidence-first code review: gathers its own evidence, issues a frozen PASS/PARTIAL/FAIL verdict,
  and only then offers the minimum remediation for approval. Use for any review of a file, uncommitted
  changes, a commit, or a branch diff — constructive review ("code review", "review this", "revisiona",
  "controlla modifiche"), strict or pessimistic review, adversarial verification, pre-merge review,
  completion verification ("is this really done", "verify this is complete"), scope-creep or
  gold-plating checks, and explicit PASS/FAIL requests. Candidate replacement for optimistic-code-review
  and pessimistic-code-review, which are still installed and still run their own pipelines — they are
  untouched, and this skill neither delegates to them nor is called by them. Prefer a narrower specialist when the
  request is explicitly framework-scoped (react-review for React component/hook/JSX reviews) or the
  repo ships its own review skill. Do not use to audit a spec or plan before coding (goal-spec-review),
  to hunt a live bug's root cause (diagnosing-bugs), to propose behaviour-preserving restructuring of a
  diff (improve-codebase-architecture), or to write features.
user-invocable: true
disable-model-invocation: true
argument-hint: "[scope: file|changes|commit|branch] [spec / issue ref]"
---

# Advanced Code Review

You are an independent verifier, not a coach. The developer's claims are inadmissible — only evidence
you gathered yourself counts. Coaching, praise and fixes exist, but they come *after* the verdict is
frozen and can never soften it.

**User-invoked only.** This skill is hidden from the model's skill router: it runs when the user calls
`/skill:advanced-code-review` (or a shim of it), never on the model's own initiative. Do not self-trigger
it as a side task, and do not chain into it after writing code.

Respond entirely in the language of the user's input — chat, Markdown and HTML — unless the user asks
for another language. Never switch mid-conversation.

## Required inputs

| Input | Rule |
|---|---|
| **Scope** | file, uncommitted changes, commit, or branch diff. Infer it from the request when unambiguous; otherwise ask. For a branch diff, **always ask for the base branch** — never infer it from the remote or default branch. |
| **Spec** | the requested behaviour: task text, issue, PR body, commit message, acceptance criteria. **Never infer the spec from the implementation** — that is circular. If completeness is being judged and no spec was given, ask for it and stop. |
| **Output format** | ask before starting, together with the scope, unless the request already names one: `(1) inline chat  (2) Markdown file  (3) HTML file  (4) all`. Default `4` only if the user declines to choose. |

Evidence collection needs live tool output: leave plan mode before running any `git`, test, or lint
command. Confirm you are in a git repo (`git rev-parse --is-inside-work-tree`) before diff commands;
without one, only a single-file "new code" review is possible.

## Pipeline — run in order, do not interleave with remediation

1. **Scope audit** — did the change deliver more than the spec asked? Gold-plating is a defect.
2. **Correctness & risk** — read the code hunting for failure: spec gaps, edge cases, security at
   trust boundaries, regressions, performance risk. Adapt framework-specific checks yourself.
3. **Independent verification** — run the relevant tests, type checks and linters yourself. Record
   every command and its real result. Audit the suite: skipped, disabled, trivial or
   implementation-shaped tests. If you cannot run a check, record it as not run with the reason.
4. **Verdict** — derive it mechanically from stages 1–3, then freeze it.

Detail, per-stage questions and framework hints: [references/review-playbook.md](references/review-playbook.md).

## Hard gates

- Label every finding `VERIFIED` (you observed it), `INFERRED` (your reasoning), or `UNVERIFIED`
  (could not check). Cite `file:line` for anything actionable you observed.
- A **PASS is impossible** when a required check produced failure evidence, and impossible when a
  required check was not executed — unavailable verification is never a pass.
- One severity rubric, one verdict rule, both defined in
  [references/severity-and-verdict.md](references/severity-and-verdict.md). Findings and required
  fixes stay inside the supplied spec and reviewed scope.
- Anything outside spec and scope — style, refactors, speculative abstractions, "while you're here" —
  is a non-blocking observation only. It never enters the failure criteria or the required-fix list. A
  user who wants that work done gets pointed at `improve-codebase-architecture` for a separate,
  behaviour-preserving pass — the verdict is already frozen and stays untouched by it.
- Never apply a fix, generate a test file, open an issue, or run a destructive command without explicit
  approval. Offering is free; acting on the repo or on a tracker is not.

## After the verdict

Once frozen, the review may add: genuine strengths backed by evidence (never manufactured), the
minimum remediation that clears the failed checks with concise WHY/HOW per fix, and this menu —
rendered in the user's language:

```
(1) one by one   (2) all required fixes   (3) selected (e.g. "1,3")   (4) none      [+tests]
```

Wait for an explicit choice; also honour `+tests` (add the missing tests for the fixed logic, in the
repo's existing framework and layout) and a severity filter such as "only blockers". One-by-one means
one fix shown, then `apply / skip`, then the next. After applying, report applied vs skipped — and never
restate the verdict as improved: a clean re-run is a new review with its own record.

## Output contract

Whatever the chosen format, the review is written once as a canonical `review.json` and rendered from
it — the format decides only where the numbers are shown, never what they are:

```bash
node <skill-dir>/scripts/render-review.mjs .reviews/<name>.json --format chat|md|html|all
```

| Choice | `--format` | Result |
|---|---|---|
| inline chat | `chat` | the complete report in chat — verdict, all findings with WHY/HOW, verification, strengths, numbered required fixes. No file written |
| Markdown file | `md` | `.md` report + short chat summary with the verdict, blocking findings, verification status and the file link |
| HTML file | `html` | self-contained `.html` report + the same short chat summary |
| all | `all` | both files + short chat summary |

The renderer validates the record and refuses an inconsistent verdict. Never hand-write or post-edit
the rendered output — change `review.json` and re-render. In inline mode keep the record anyway (under
`.reviews/` or the temp dir): it is the renderer's input and the proof the outputs cannot drift.

Schema, file-naming convention, and presentation rules:
[references/output-contract.md](references/output-contract.md).

---
name: advanced-code-review
description: >
  Evidence-first code review of a file, uncommitted changes, a commit, or a branch diff, judged against
  the spec and the repo's documented standards: gathers its own evidence, freezes a PASS/PARTIAL/FAIL
  verdict, then offers the minimum remediation for approval.
  Covers constructive, strict/adversarial, pre-merge, completion and scope-creep reviews alike. Prefer
  a narrower specialist when the request is framework-scoped (react-review) or the repo ships its own
  review skill. Not for auditing a spec before coding (goal-spec-review), root-causing a live bug, or
  writing features.
user-invocable: true
disable-model-invocation: true
argument-hint: "[scope: file|changes|commit|branch] [spec / issue ref]"
---

# Advanced Code Review

You are an independent verifier, not a coach. The developer's claims are inadmissible — only evidence
you gathered yourself counts. Coaching, praise and fixes exist, but they come *after* the verdict is
frozen and can never soften it.

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
   Two sources of law, and only these: the **spec** (what was asked) and the **standards written down
   in this repo** (`CLAUDE.md`, `AGENTS.md`, contributing docs, lint config). A written rule the diff
   breaks blocks, and cites its document at `file:line`; a convention that is widespread in the code
   but written nowhere does not.
3. **Independent verification** — run the relevant tests, type checks and linters yourself. Record
   every command and its real result. Audit the suite: skipped, disabled, trivial or
   implementation-shaped tests. If you cannot run a check, record it as not run with the reason.
4. **Verdict** — derive it mechanically from stages 1–3, then freeze it.

Detail, per-stage questions and framework hints: [references/review-playbook.md](references/review-playbook.md).

## Hard gates

- Label every finding `VERIFIED` (you observed it), `INFERRED` (your reasoning), or `UNVERIFIED`
  (could not check). Cite `file:line` for anything actionable you observed.
- Every blocking finding declares its `basis`: the acceptance criterion or documented rule it invokes,
  quoted verbatim in the record. Cannot quote it? Then it is not blocking — it is an opinion.
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

Wait for an explicit choice; `+tests` and a severity filter such as "only blockers" are honoured too.
After applying, report applied vs skipped — never restate the verdict as improved. Details:
[references/output-contract.md](references/output-contract.md).

**Last, once remediation is settled**: up to three design decisions you did not have the context to
settle — each with the sibling code it hinges on and two defensible options — then ask whether to go
through them, one at a time. They never touch the verdict and never enter the fix menu.

## Output contract

Whatever the chosen format, the review is written once as a canonical `review.json` and rendered from
it — the format decides only where the numbers are shown, never what they are:

```bash
node <skill-dir>/scripts/render-review.mjs ~/.agents/reviews/<repo>/<name>.json --format chat|md|html|all
```

`chat` prints the complete report and writes nothing; `md`, `html` and `all` write the file(s) plus a
short chat summary. What each one contains: [references/output-contract.md](references/output-contract.md).

The renderer validates the record and refuses an inconsistent verdict. Never hand-write or post-edit
the rendered output — change `review.json` and re-render. In inline mode keep the record anyway (under
the reviews directory): it is the renderer's input and the proof the outputs cannot drift.

Schema, file-naming convention, and presentation rules:
[references/output-contract.md](references/output-contract.md).

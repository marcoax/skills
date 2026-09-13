# Observed evaluation results

Run date: 2026-07-29 · Node v25.2.1 · macOS · authoring session for the migration from
`optimistic-code-review` + `pessimistic-code-review`.

Honesty rule applied to this file too: only checks actually executed are reported as passed.
Everything requiring a fresh model session is marked **not run**, with the reason.

## Executed

### e2e-1-real-repo — PASS (fully observed)

Fixture: throwaway git repo `/tmp/acr-e2e` with `src/discount.mjs` (missing range validation, extra
`applyAll()`) and `test/discount.test.mjs` (1 skipped test, 1 failing test).

| Check | Result | Evidence |
|---|---|---|
| Real test command executed and recorded | pass | `node --test 'test/*.test.mjs'` → `pass 1 / fail 1 / skipped 1`, `AssertionError: actual -19.999999999999996, expected -20` |
| Missing validation flagged BLOCKER | pass | F1 `src/discount.mjs:2` |
| Extra `applyAll()` flagged as scope creep | pass | F2 `src/discount.mjs:4` |
| Skipped test covering the requirement flagged | pass | F3 `test/discount.test.mjs:5` + `test_audit` |
| Second check unavailable reported honestly | pass | `npx eslint src` → `not_run`, reason "no eslint config and no node_modules" |
| Verdict FAIL | pass | derived and declared FAIL |
| Three artifacts written | pass | `.reviews/2026-07-29-2230-discount-uncommitted.{json,md,html}` + chat summary on stdout |
| No drift across chat/MD/HTML | pass | ids `F1–F4,O1` present in all three; BLOCKER count `3` in both MD and HTML tables; verdict `❌ FAIL` in both; 2 verification commands in both |
| HTML self-contained + escaped | pass | `<script` occurrences: 0; external `src=`/`href="http`/`@import`: 0; injected `<script>alert(1)</script>` in test output rendered as `&lt;script&gt;` |
| No source file modified | pass | review wrote only under `.reviews/` |

### Renderer gate cases — PASS (fully observed)

`scripts/render-review.mjs` refuses to render and exits 1 on:

| Forced record | Observed message |
|---|---|
| `PASS` with a failed check + BLOCKER | `verdict "PASS" contradicts the evidence — rules require "FAIL" (BLOCKER=1, HIGH=0, failed checks=true, unrun checks=true)` |
| `PASS` with a `not_run` check, no findings | `… rules require "PARTIAL" (… unrun checks=true)` |
| `PASS` with empty `verification` | `verification is empty: record each executed check, or a not_run entry with a reason` |
| spec `source: "the implementation"` | `spec.source: the spec must not be inferred from the implementation` |
| `VERIFIED` finding without location | `findings[0]: VERIFIED findings require a file:line location` |
| BLOCKER without `how` | `findings[0]: blocking findings require "how" (minimum fix)` |
| `required_fix: true` on MEDIUM | `findings[1]: required_fix is only for BLOCKER/HIGH` |
| valid PASS (green suite, one LOW finding) | exit 0, rendered |

### `--diff` evidence gate — PASS (fully observed, 2026-09-13)

Added so a fabricated citation cannot render. Off unless `--diff` is passed, so existing records are
unaffected. Observed against the `e2e-1` fixture and its captured diff:

| Case | Result |
|---|---|
| baseline record, no `--diff` | exit 0 — behaviour unchanged |
| baseline record, `--diff` with the real diff | exit 0 — all 4 findings cite lines that are in it |
| `F1.evidence` replaced with a plausible line never in the diff | exit 1, `findings[0] (F1): "evidence" does not occur in the reviewed diff` |
| same line re-indented (extra spaces) | exit 0 — whitespace is normalised, so quoting is not brittle |

Scope note: only `findings` carry `evidence`; `observations` and `strengths` cite a `location` and an
`evidence_class` instead, and the schema rejects an `evidence` field on them. The gate covers findings
only, which is all there is to cover.

This covers `adv-2-verdict-bypass → renderer_rejects_forced_PASS` and
`edge-3-unrunnable-tests → verdict_not_PASS / does_not_present_unrun_check_as_passing` mechanically:
those outcomes are impossible to render, not merely discouraged.

## Baseline 2026-09-13 — before the sub-agent split

Re-run of `e2e-1-real-repo` on the current version, to have something to compare against if the
stage-2 sub-agent split lands. Fixture is now reproducible: `bash evals/fixtures/make-e2e-repo.sh`
rebuilds it at `/tmp/acr-e2e` (git repo, uncommitted diff, `SPEC.md` with 3 acceptance criteria).

Node v22.23.2 · macOS · reviewer: model session, no sub-agents.

| Measure | Value |
|---|---|
| Findings | 4 — 3 BLOCKER, 1 HIGH, 0 observations |
| Verdict | `FAIL` |
| Findings whose `evidence` string occurs verbatim in the captured diff | 4 / 4 |
| Criteria | C1 met, C2 unmet, C3 unmet |
| Checks | 1 fail (`node --test`), 1 not_run (eslint absent), 1 counterfactual pass |
| Drift across chat / MD / HTML | none — F1–F4, H1, C2 appear the same number of times in both files |
| HTML self-contained | `<script`: 0 · external refs: 0 |
| Repo modified by the review | no — only the change under review is dirty; counterfactual restored cleanly |

The counterfactual is the interesting one: removing `applyAll` left the suite identical
(1 pass / 1 fail / 1 skipped), which is what turns it from a possible enabling change into
`basis: scope_creep`.

**Comparison rule for the next run.** Findings count and the evidence-in-diff ratio may move a
little. **If the verdict moves, the change is not a context optimisation** — it altered behaviour,
and that has to be understood before keeping it.

## Not run

| Cases | Reason |
|---|---|
| `pos-1` … `pos-5`, `neg-1` … `neg-5`, `edge-1`, `edge-2`, and the behavioural half of `adv-1`/`adv-2` | Require fresh model sessions with a live git repo and a judge; no automated eval harness is wired in this repository. Run them manually with `evals/evals.json` and record outcomes here. |

Anything in this table is **unverified**, not passing.

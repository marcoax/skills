# Migration plan: optimistic-code-review + pessimistic-code-review → advanced-code-review

**Status: not executed. Nothing has been replaced yet.**

`optimistic-code-review` and `pessimistic-code-review` are **untouched and fully operational** — original
`SKILL.md`, original `evals/`, both in the repo and in `~/.agents/skills/`. `advanced-code-review` is
purely additive and coexists with them. The owner decides if and when to retire them, after testing this
skill thoroughly; this document is the plan for that day, not a record of a completed change.

Date drafted: 2026-07-29. Sources studied for the design were the installed
`~/.agents/skills/{optimistic,pessimistic}-code-review/SKILL.md`, byte-identical to the repo copies.

## Behaviour map

"Status" below describes how each behaviour was treated **inside `advanced-code-review`**. It says
nothing about the old skills, which keep all of their original behaviour.

| Source behaviour | From | Treatment in advanced-code-review |
|---|---|---|
| 4-way scope selection (file / uncommitted / commit / branch) + per-scope git commands | both | **retained**, compacted into [references/review-playbook.md](references/review-playbook.md) |
| "Never infer the base branch" hard rule | optimistic | **retained** as a hard rule in `SKILL.md` |
| Git-repo precondition, empty-diff fallback to whole-file review, ≥10-file diff confirmation | optimistic | **retained** in the playbook |
| Plan-mode gate before running git | optimistic | **retained**, one line ("leave plan mode before collecting evidence") |
| Read project standards (`CLAUDE.md`/`AGENT.md`) before judging conventions | both | **retained** in the playbook |
| Severity checklist CRITICAL/HIGH/MEDIUM/LOW with framework adaptation | optimistic | **changed** into one blocking-aware rubric `BLOCKER/HIGH/MEDIUM/LOW` + non-blocking observations, [references/severity-and-verdict.md](references/severity-and-verdict.md) |
| WHY + HOW per finding, `file:line` citations | optimistic | **retained**, now required by the renderer for blocking findings |
| Mandatory ✅ Positives section | optimistic | **changed**: strengths are evidence-backed and optional — no manufactured praise, and they come after the frozen verdict |
| A–F overall grade | both | **removed**: it competed with the verdict. One verdict rule now |
| Fix menu (one-by-one / all / selected / none), approval before any edit | both | **retained**, gated behind the frozen verdict |
| `+tests` test generation on approval | both | **retained** as approval-gated remediation, no separate step |
| Step 6 "offer a Codex deep review" | optimistic | **removed**: unrequested escalation, environment-specific |
| "Respond in the user's language" | optimistic | **retained** as the canonical language rule |
| "Always respond in Italian" | pessimistic | **removed**: contradicted the rule above |
| IAV posture — adversarial verifier, developer claims inadmissible | pessimistic | **retained** as the skill's default posture |
| Spec required, never inferred from the implementation | pessimistic | **retained** as a hard gate, enforced by the renderer (`spec.source`) |
| Phase 1 scope audit / gold-plating | pessimistic | **retained** as pipeline stage 1; scope creep is `BLOCKER` |
| Phase 2 adversarial correctness | pessimistic | **retained** as stage 2, extended with regressions and performance risk |
| Phase 3 independent verification + disabled/trivial test audit | pessimistic | **retained** as stage 3, extended with static checks and a structured `test_audit` |
| PASS / FAIL / PARTIAL verdicts, "PARTIAL is not a hedge" | pessimistic | **retained** as deterministic rules, now machine-enforced |
| "Never suggest improvements" absolutism | pessimistic | **changed**: optional improvements are allowed but confined to a non-blocking section that cannot affect the verdict or the required-fix list |
| Long "What You Must Never Do" list | pessimistic | **reduced** to the gates that protect evidence integrity, verdict correctness, and the approval boundary |
| Hand-written Markdown output block | both | **replaced** by one canonical `review.json` + `scripts/render-review.mjs` → chat + Markdown + HTML |
| HTML report | neither | **new** (self-contained, semantic, responsive, printable, escaped) |
| Evidence classes VERIFIED / INFERRED / UNVERIFIED | neither | **new** |

## Current state of the repository

| Path | State |
|---|---|
| `review/advanced-code-review/**` | new, additive: pipeline, references, renderer, evals |
| `review/optimistic-code-review/**` | **untouched** — original `SKILL.md` + original `evals/` |
| `review/pessimistic-code-review/**` | **untouched** — original `SKILL.md` + original `evals/` |
| `review/react-review/SKILL.md` | **untouched** — its router line still names `optimistic-code-review` |
| `personal/deprecated/laracms-code-review/SKILL.md` | **untouched** |
| `README.md`, `review/README.md` | one added row for `advanced-code-review`; every existing row, description and install example left as it was |
| `.claude-plugin/plugin.json` | one added entry for `./review/advanced-code-review` |
| `REPORT.md` | untouched |

Check at any time:

```bash
git diff --stat HEAD -- review/optimistic-code-review review/pessimistic-code-review   # must be empty
diff -r review/optimistic-code-review ~/.agents/skills/optimistic-code-review          # must be empty
diff -r review/pessimistic-code-review ~/.agents/skills/pessimistic-code-review        # must be empty
```

## Cut-over checklist (run only when the owner decides)

1. Replace `review/optimistic-code-review/SKILL.md` and `review/pessimistic-code-review/SKILL.md` with
   redirect-only shims keeping their `name:` for backward compatibility.
2. Fold the three `pessimistic-code-review/evals` scenarios into `advanced-code-review/evals/evals.json`
   (already represented there as `adv-*` / `e2e-1`), then delete both old `evals/` directories.
3. Repoint router lines: `review/react-review/SKILL.md` and
   `personal/deprecated/laracms-code-review/SKILL.md`.
4. Update the two READMEs' old rows and the install examples; regenerate
   `.claude-plugin/plugin.json` with `node scripts/generate-plugin.mjs`.
5. Re-run `evals/evals.json` and record the outcome in `evals/results.md`.
6. Leave `REPORT.md` alone: historical record, not a router.

Note for step 4: `scripts/generate-plugin.mjs` scans the buckets, so it will also publish any other
untracked skill directory present at that moment (e.g. `utilities/php-tdd-workflow`). Decide about those
before regenerating.

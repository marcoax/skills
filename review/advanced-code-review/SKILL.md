---
name: advanced-code-review
description: Review code changes against the requested behavior and repository standards, with evidence-backed findings and a PASS/PARTIAL/FAIL verdict.
user-invocable: true
disable-model-invocation: true
argument-hint: "[scope: file|changes|commit|branch] [spec / issue ref]"
---

# Advanced Code Review

Review the requested scope independently. Treat developer statements as leads to verify, and judge
findings by their evidence and impact. Use the user's language unless asked otherwise.

## Establish scope

Use the request and available repository context to identify the file, uncommitted changes, commit,
or branch comparison. For branches, use an explicit base or the PR's target; otherwise use a clearly
established repository base and state it. Ask only when competing interpretations would change the review.

Take requirements from the task, issue, PR, or other stated acceptance criteria, never from the
implementation. If a completeness review lacks a spec, request it while continuing independent
correctness checks; leave completeness unassessed until the requirements are available.

Read applicable repository instructions and only the supporting docs relevant to the changed behavior.
A review request does not by itself authorize source fixes or tracker updates; honor authorization
already given when the user requests review and remediation together.

## Review and verify

Examine scope, correctness, regressions, and relevant documented standards. Distinguish unnecessary
scope expansion from implementation details needed to deliver the request. Trace affected callers or
boundaries where they could change a finding; avoid turning the review into a repository-wide audit.

Choose checks proportionate to the change and unresolved risk. Record commands actually run, their
results, and necessary checks that could not run. Distinguish failures introduced by the change from
baseline failures. Inspect affected tests for meaningful coverage; broaden verification only when
new evidence warrants it.

For branch comparison mechanics or counterfactual experiments, read
[review-playbook.md](references/review-playbook.md) as needed.

## Optional delegation

Use sub-agents when the review contains substantial, independent questions:
spec compliance, regressions across callers, or a focused verification gap.
Small reviews usually need no delegation.

Give each sub-agent a bounded question, the same captured code state, and
the relevant requirements. Request findings with locations, supporting
evidence, impact, and verification limits. Avoid sharing tentative conclusions
when an independent assessment would be useful.

Keep review tasks read-only; run mutation-based experiments in isolated
workspaces. The main agent reconciles overlapping findings, checks their
evidence, and owns the final verdict and any authorized remediation.

## Findings and verdict

Use [severity-and-verdict.md](references/severity-and-verdict.md) to classify findings and derive the
verdict. Keep severity, evidence class, location, impact, and minimum correction clear. Cite the
acceptance criterion or documented standard when a finding relies on one; concrete defects do not
need a written rule to be actionable. Keep optional redesigns outside required fixes.

Complete the review when the requested scope has been examined, material findings have supporting
evidence, and relevant verification is complete or its limitations are explicit. Report the verdict,
findings ordered by severity, and verification limits. State when no actionable findings were found;
include strengths or unresolved design decisions only when useful.

## Output and remediation

Default to an inline report. For requested Markdown/HTML files or a machine-readable record, read
[output-contract.md](references/output-contract.md) and use the canonical JSON record and renderer.
Do not ask for a format merely to begin reviewing.

The verdict describes the reviewed state. If fixes are already authorized, capture that assessment,
apply the in-scope corrections, and verify the resulting state without another approval round.
Otherwise offer concrete remediation when needed. A subsequent assessment must identify the new
state and new evidence; preserve existing reports rather than rewriting their history.

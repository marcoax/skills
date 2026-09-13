---
name: technical-debt-manager-php-laravel
description: >
  Audits a PHP/Laravel codebase for technical debt and turns it into a prioritised, sprint-ready
  roadmap. Use when the target project is Laravel and the user asks for a debt audit, a code-health
  review, "what should we refactor", or a refactoring plan for a quarter. Not for generic
  non-Laravel debt analysis, and not for reviewing a single diff or PR — use a code-review skill
  for that.
---

# Technical Debt Manager (PHP/Laravel)

Turn invisible code health problems into a prioritised roadmap. Baseline: PHP ≥ 8.3, Composer,
the Laravel major already in the repo.

Read the repo's own conventions first (`CLAUDE.md`, `.ai/rules/`, `AGENTS.md` if present) — a
pattern the project has chosen deliberately is not debt.

## 1. Measure before reading

Run these, they are the evidence the whole report rests on. Don't substitute intuition for them.

```bash
test -f artisan && php artisan --version; php -v; composer -V
cat composer.json

composer audit                    # security advisories
composer outdated --direct        # dependency freshness
vendor/bin/phpstan analyse --memory-limit=1G   # if the repo configures Larastan/PHPStan
vendor/bin/pint --test            # style drift, check-only
php artisan test                  # suite health

# churn hotspots, last 90 days
git log --format=format: --name-only --since="90 days ago" \
  | grep -vE '^(|\.github/|docs/|README|CHANGELOG)' | sort | uniq -c | sort -rn | head -25
```

No coverage tooling is needed: judge tests by presence or absence around critical flows and by CI
reliability, not by a percentage.

## 2. Read the hotspots

Churn × static-analysis findings tells you where to look; read the top 10–20 files yourself. What
you are hunting for in a Laravel codebase specifically:

- business rules living in controllers, jobs, console commands or Eloquent models
- N+1 and missing eager loads; missing indexes on columns the code filters or sorts on
- synchronous work that belongs on a queue
- state changes without a transaction, swallowed exceptions
- static/facade calls where a seam is needed to test
- inconsistent conventions across Actions / Services / Jobs / Listeners

Classify each finding as code quality, tests, docs, dependencies, design, infrastructure or
performance — the report groups by these seven.

## 3. Prioritise

```
Severity = (Churn × Complexity × Business criticality) / Test confidence
```

Churn is commits in the last 90 days; business criticality puts payments, auth and data integrity
above admin UI above internal tooling. Say the inputs out loud for each item so the score is
arguable, not oracular.

| | |
|---|---|
| **Critical** | security advisories on production paths; data-corruption, auth or payment-integrity risk; hotspots actively blocking delivery |
| **High** | churn + complexity + weak tests; upgrades that unblock a framework bump; user-visible performance |
| **Medium** | moderate complexity in stable areas; docs gaps that slow onboarding or ops |
| **Low** | low churn, cosmetic, or debt in code being removed anyway |

Bias the ordering toward high impact / low effort, and toward the smallest safe step first.

## 4. Deliver

An inventory report, sprint-ready work items, and a quarter roadmap — shapes in
[references/report-templates.md](references/report-templates.md). Every item needs evidence
(command output, file paths, churn counts), an effort band, and acceptance criteria that can be
checked by running something.

Write findings as cost, not as judgement: "this module is a bug hotspot, a small refactor plus
tests cuts rework" lands where "this code is bad" does not.

If the user wants the debt to stop growing, the cheap gates are `composer audit`,
`vendor/bin/pint --test`, `phpstan` (baseline-capped if noisy) and `php artisan test` in CI.

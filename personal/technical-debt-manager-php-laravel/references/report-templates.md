# Output shapes

Three deliverables. They set the format, not the depth — drop sections the audit found nothing for
rather than filling them with "none".

## 1. Inventory report

```markdown
# Technical Debt Inventory

**Repository**: <repo>   **Date**: <YYYY-MM-DD>   **Baseline**: PHP >= 8.3, Laravel <version>

## Summary
Critical <n> · High <n> · Medium <n> · Low <n>

| Category | Count | Severity | Est. effort |
|---|---:|---|---|
| Code quality / Tests / Docs / Dependencies / Design / Infrastructure / Performance | | | |

## Top items

### [Critical] <one-line title>
- **Impact**: what it costs the business or the team
- **Effort**: S / M / L, or days
- **Evidence**: `composer audit` output, churn count, static-analysis rule
- **Files**: paths, with line refs where they help
- **Fix outline**: the smallest safe steps
```

## 2. Work items

One story per item, in the tracker's own format. Acceptance criteria must be runnable:

```markdown
### Story: Resolve Composer security advisories
**Priority**: Critical · **Effort**: 1–3 pts
- [ ] `composer audit` reports 0 high/critical
- [ ] dependencies updated with minimal breaking changes
- [ ] CI green (phpstan + tests)

### Story: Stabilise <hotspot>
**Priority**: High · **Effort**: 5–8 pts
- [ ] large method(s) split into focused units
- [ ] tests cover the critical behaviour, happy and failure paths
- [ ] phpstan findings for this module reduced (before/after count)
- [ ] no behavioural regression
```

## 3. Quarter roadmap

Sequence it so each phase makes the next one safer: security and test scaffolding first, then the
refactors those tests protect, then dependencies, then performance and operability. Close with
success metrics that are measurable from the same commands as the audit — advisory count, outdated
direct deps, phpstan findings in critical modules, bugfix PRs in hotspot areas, cycle time on core
flows.

For trend tracking across months, a table of those same metrics with a target column and a
direction is enough; nothing here needs a dashboard.

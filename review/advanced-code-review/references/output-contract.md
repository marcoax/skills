# Output contract

Chat, Markdown and HTML are three renderings of **one** record. Write the record, run the renderer,
paste its stdout as the chat answer. Never author the Markdown or HTML by hand — drift between formats
is a defect, and the renderer is what makes drift impossible.

The user picks the format up front (`(1) inline chat (2) Markdown file (3) HTML file (4) all`). The
choice changes only the destination: the same validated record produces every variant, so an inline
review and a filed one carry identical verdict, ids, severities, counts, citations and verification
status.

| Choice | Command | Writes | stdout |
|---|---|---|---|
| inline chat | `--format chat` | nothing | the complete report: verdict, every finding with WHY/HOW, verification with real output, test audit, strengths, numbered required fixes, fix menu |
| Markdown | `--format md` | `.md` | short summary + link |
| HTML | `--format html` | `.html` | short summary + link |
| all (default) | `--format all` | `.md` + `.html` | short summary + both links |

Inline mode still needs the record on disk — it is the renderer's input. Keep it next to the reports,
or in `$TMPDIR` when the user wants nothing left in the repo.

## Files and naming

**Reports are written outside the repository under review**, in `~/.agents/reviews/<repo>/`:

```
~/.agents/reviews/<repo>/<YYYY-MM-DD-HHmm>-<scope-slug>.json   # canonical record (source of truth)
~/.agents/reviews/<repo>/<YYYY-MM-DD-HHmm>-<scope-slug>.md     # generated
~/.agents/reviews/<repo>/<YYYY-MM-DD-HHmm>-<scope-slug>.html   # generated
```

A review must not modify the repository it reviews — not even by adding a report or a `.gitignore`
line. A report written into the working tree becomes part of the next review's diff, where it reads as
somebody's scope creep.

Write inside the repo only when the user asks for it explicitly, and then follow the repo's own report
convention. `<scope-slug>` is a short kebab-case tag of the scope: `auth-controller`,
`feat-billing-vs-main`, `commit-a1b2c3d`, `uncommitted`. Never commit reports on the user's behalf.

## Render

```bash
node <skill-dir>/scripts/render-review.mjs ~/.agents/reviews/<repo>/2026-05-04-1130-uncommitted.json --format all
# writes the .md and .html siblings, prints the chat summary
# --format chat prints the whole report instead and writes nothing
```

The renderer exits non-zero and renders nothing when the record breaks a gate. Fix the record, do not
work around the validator. It enforces:

- required fields, enums, unique `F<n>` / `O<n>` ids, no unknown fields
- `VERIFIED` findings carry a `file:line`; blocking findings carry a `how`
- `required_fix: true` only on `BLOCKER`/`HIGH`; `MEDIUM`/`LOW` and observations can never be required
- executed checks carry real output; `not_run` checks carry a reason
- `verification` is never empty
- the declared `verdict` equals the verdict derived from the evidence (see
  [severity-and-verdict.md](severity-and-verdict.md)) — a `PASS` alongside a failed or unrun check is
  rejected, as is a spec whose `source` is the implementation

## Record shape

Schema: [review.schema.json](review.schema.json). Minimal example:

```json
{
  "schema": "advanced-code-review/1",
  "language": "it",
  "scope": { "kind": "branch", "target": "feat/billing vs main", "stats": "4 files, +180/-12",
             "files": ["app/Billing/Invoice.php", "tests/InvoiceTest.php"] },
  "spec": { "source": "issue #142", "text": "Emit an invoice PDF when an order is paid…" },
  "verdict": "FAIL",
  "verdict_reason": "Invoice totals ignore tax (F1) and the suite fails on InvoiceTest::test_totals.",
  "verification": [
    { "command": "php artisan test --filter Invoice", "status": "fail", "result": "FAILED  InvoiceTest::test_totals\nExpected 122.00, got 100.00" },
    { "command": "vendor/bin/phpstan analyse app", "status": "not_run", "reason": "phpstan not installed in this environment" }
  ],
  "test_audit": [ { "subject": "InvoiceTest::test_pdf_written", "issue": "skipped", "location": "tests/InvoiceTest.php:88", "note": "covers a spec requirement" } ],
  "findings": [
    { "id": "F1", "severity": "BLOCKER", "title": "Tax excluded from invoice total",
      "evidence_class": "VERIFIED", "location": "app/Billing/Invoice.php:64",
      "evidence": "return $this->subtotal; // tax never added",
      "why": "Spec requires gross totals; every invoice is undercharged.",
      "how": "Return $this->subtotal + $this->tax() and assert 122.00 in test_totals.",
      "required_fix": true }
  ],
  "observations": [ { "id": "O1", "note": "PdfWriter could be extracted, out of scope for #142", "location": "app/Billing/Invoice.php:120" } ],
  "strengths": [ { "text": "Money handled in integer cents throughout", "location": "app/Billing/Money.php:14" } ]
}
```

## What each surface must carry

| Surface | Content |
|---|---|
| chat | verdict first, blocking findings one line each with id/severity/location/evidence class, verification status per command, incomplete-verification warning, links to both reports, remediation menu when required fixes exist |
| Markdown | the complete durable record: scope, spec, verdict + reason, severity totals, every command with its real output, all findings, non-blocking section, test audit, strengths, required remediation |
| HTML | the same content, self-contained (inline CSS, no scripts, no fonts, no network), semantic sections, responsive, dark-mode and print stylesheets, headed tables, verdict conveyed by text as well as colour, all repository content escaped |

Regenerating after applied fixes means a **new** record and a new timestamped triple — never edit a
frozen report to look better.

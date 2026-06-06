---
name: log-analyzer
description: "Analyze Symfony app.ERROR log files for the Carimali/caricare project. Use ONLY when the user explicitly mentions a Symfony/caricare/carimali log file, or when the file clearly contains 'app.ERROR' lines. Triggers on: analizza il log, genera report dal log, pulisci il log, log_errori, app.ERROR, analisi errori caricare/carimali. Do NOT trigger on generic log analysis requests for non-Symfony systems (nginx, Apache, Laravel, etc.). Produces two files: a cleaned log (NAME_clean.txt) and a markdown report (NAME_report.md)."
---

# Log Analyzer Skill

Analyzes Symfony `app.ERROR` log files for the caricare project. Given an input log file, the script executes 7 steps:
1. **Cleans** the log by applying `CLEAN_RULES` (filters irrelevant blocks and lines)
2. **Extracts** errors from the cleaned log and normalizes messages (`{N}`, `{UUID}`, etc.)
3. **Archives** existing `log_report_*.md` files to `report/`
4. **Generates** a markdown report with hourly distribution and error-type counts
5. **Updates** `error_history.json` and regenerates `error_trend.html` (if errors found)
6. **Checks** for new error types against `assets/known_errors.txt`
7. **Moves** the original input file to `backup/`

## Output files

| File | Description |
|------|-------------|
| `BASENAME_clean.txt` | Cleaned log with irrelevant blocks/lines removed |
| `log_report_YYYY_MM_DD.md` | Markdown report with stats tables |
| `report/log_report_*.md` | Previous reports archived here (if any existed) |
| `error_history.json` | Cumulative daily error data (appended each run) |
| `error_trend.html` | Interactive dashboard with charts (generated only if log contains errors) |
| `backup/BASENAME.txt` | Original input file moved here after processing |

Example: input `log_errori_2026_03_20.txt` → `log_errori_2026_03_20_clean.txt` + `log_report_2026_03_20.md`, original moved to `backup/`

## How to run

### Automatic (preferred)

**If the user has not provided a file path**, ask before proceeding:
> "Qual è il percorso del file di log da analizzare?"

When the path is known, run the script directly:

```bash
python {SKILL_DIR}/scripts/analyze_log.py PATH/TO/log_errori_YYYY_MM_DD.txt
```

All output files are written to the **current working directory (CWD)** where the script is run,
not to the input file's directory. If the user runs from a different folder, output lands in CWD.

### Post-analysis step

After running the script:
1. Read the generated `log_report_*.md` file from CWD using the Read tool
2. Show its **full contents** to the user (do not summarize — show the complete markdown)
3. Check the script stdout for the line `*** NEW ERROR TYPES DETECTED`:
   - If present: show the new error types as a **prominent separate block** in the chat, e.g.:
     ```
     ⚠️ NUOVI TIPI DI ERRORE RILEVATI:
     - <error type 1>
     - <error type 2>
     ```
   - If absent ("No new error types detected."): no action needed
4. Then **always ask**:

> "Ci sono nuove regole di pulizia da aggiungere al log analyzer?"

If the user provides new rules, update **both** files (they must stay in sync):

1. Read `assets/CLEAN_RULES.md` and add the new rule following the existing numbered format (with Input/Output examples)

2. Update `scripts/analyze_log.py`:
   - **Add a detection helper** in the `CLEAN_RULES filtering helpers` section, following this exact pattern:
     ```python
     def is_<descriptive_name>_line(line: str) -> bool:
         return '<unique string from the line to match>' in line
     ```
     Or for block-level rules:
     ```python
     def is_<descriptive_name>_block(block_lines: list[str]) -> bool:
         return any(is_<descriptive_name>_line(line) for line in block_lines)
     ```
   - **Integrate in `clean_block()`**: Add the check at the **top** of `clean_block()` (before the serial extraction) for whole-block drop rules, or inside the `for line in block_lines` loop for line-level filters
   - If the new rule requires normalising a variable part (e.g. a new number format), also add an entry to `NORMALISE_PATTERNS` at the top of the file

3. Re-run the script on the log file from `backup/` (step 7 moves the original there):
   ```bash
   python {SKILL_DIR}/scripts/analyze_log.py backup/log_errori_YYYY_MM_DD.txt
   ```

### Regenerate HTML from existing data

If `error_history.json` has been updated outside the full analysis flow, regenerate just the HTML dashboard:

```bash
python {SKILL_DIR}/scripts/analyze_log.py --regenerate-html [path/to/error_history.json]
```

If the path is omitted, defaults to `error_history.json` in the current directory.

### Manual fallback

If the script cannot run:

1. Read `assets/CLEAN_RULES.md` to understand the cleaning rules
2. Read the input log file using the Read tool
3. For each `app.ERROR` line found:
   - Apply normalisation: replace serial numbers with `{N}`, UUIDs with `{UUID}`, counts with `{N}`, trailing date values with `{values}` — following the same patterns in `NORMALISE_PATTERNS` at the top of `analyze_log.py`
   - Skip lines matching Rule 4 (`Troppi errori di processo`)
4. Count occurrences of each normalised error type
5. Output a markdown report **directly in the conversation** using the same format as `assets/log_report_sample.md` — including: header, total count, hourly distribution table, error type table with `Count` and `%` columns
6. Do NOT attempt to write files — output the report as markdown text in the conversation

## Reference files

- `assets/SCORING_CHECKLIST.md` — 4-question yes/no checklist to verify output quality
- `assets/CLEAN_RULES.md` — full cleaning rules with examples
- `assets/known_errors.txt` — list of known normalised error types (one per line)
- `assets/error_trend_template.html` — HTML template for the trend dashboard (data injected by script)
- `assets/log_report_sample.md` — example of the expected output report format
- `assets/log_errori_sample.txt` — example input log file
- `scripts/analyze_log.py` — automation script (Python 3.10+, stdlib only)

## New error detection

The script compares normalised errors found in the log against `assets/known_errors.txt`. If new error types appear that are not in the list, they are printed as warnings at the end of the run. When confirmed as legitimate recurring errors, add them to `known_errors.txt` (one per line, normalised form).

## Input file formats

The script supports two log formats:

1. **Block format** (raw grep output with `--` separators): full cleaning rules are applied per-block (rules 1-5)
2. **Flat format** (one `app.ERROR` line per row, no `--` separators): only line-level filtering is applied (drops `Troppi errori di processo` lines)

The format is auto-detected. Flat files are typically already-cleaned logs or logs extracted without context lines.

## Error trend dashboard

The `error_trend.html` file is a self-contained interactive dashboard with:
- Daily error volume chart, stacked breakdown by type, hourly distribution
- Summary table with day-over-day comparison
- Cache-busting meta tags (browser always loads fresh data)
- Generation timestamp visible in header and footer

The HTML is regenerated automatically at step 5, or standalone via `--regenerate-html`.

## Notes

- The script uses only Python stdlib — no pip install needed
- `FIXED` column in the report is left empty by default unless the user provides a known-issues list
- If the log covers multiple days, the report groups by day then by hour automatically
- When re-running after updating clean rules, use the file from `backup/` (step 7 moves the original there)
- If `error_history.json` is edited manually, run `--regenerate-html` to sync the dashboard

---
name: log-cleaner-process-context
description: >
  Clean a linear Symfony or Carimali log file by keeping only the lines that contain
  "Process already in progress" or other process-error matches, plus the 3 previous
  lines of context, and generate an HTML report that reconstructs the command sequence
  seen immediately before each error. Use this skill whenever the user has a file like
  `log_322665_03_30.txt`, asks to keep only process-error lines with a small amount of
  context before each error, wants something like `grep -B3`, or wants an HTML view of
  the commands received before the process error.
---

# Log Cleaner - Process Error Context

Focused cleaner for linear log files that keeps the error line, the previous context,
and produces an HTML report with the pre-error sequence.

Use this skill for logs that look like:

```text
/var/www/...:[2026-03-30 13:40:28] app.INFO: ...
/var/www/...:[2026-03-30 13:40:28] app.ERROR: Process already in progress for serial 322665 [] []
```

Do not use this skill for block-format files separated by `--`. In that case, use
`log-cleaner-process`.

## When to use

- The user has a plain text log file such as `log_322665_03_30.txt`
- They want only the `Process already in progress` lines
- They also want the 3 previous lines as context
- They want a compact output without unrelated log noise
- They want an HTML report showing the command chain before each error

## How to run

```bash
python {SKILL_DIR}/scripts/clean_process_error_context.py PATH/TO/log_file.txt
```

Optional flags:

```bash
python {SKILL_DIR}/scripts/clean_process_error_context.py PATH/TO/log_file.txt --before 3
python {SKILL_DIR}/scripts/clean_process_error_context.py PATH/TO/log_file.txt --pattern "Process already in progress"
```

The script writes:

- `<basename>_process_error_context.txt`
- `<basename>_process_error_context_report.html`

Both files are written to the current working directory.

## What it does

### Phase 1 - Match lines
Scans the input file line by line and finds every line matching the search pattern.

Default pattern:

- `Process already in progress`

Matching is case-insensitive.

### Phase 2 - Keep previous context
For every matching line, keeps:

- the matching line itself
- the 3 lines immediately before it

If two matches are close together, overlapping windows are merged automatically and
duplicated lines are not repeated in the text output.

### Phase 3 - Build the report
For each error, reconstructs the immediate sequence before the failure and tries to
label:

- `Packet received`
- `Packet sent`
- application command JSON lines such as `GetGrinderCalibration`

The HTML report summarizes recurring sequences and shows a per-error timeline.

## After running

1. Show the user the summary printed by the script
2. Point them to the generated text file and HTML report
3. If they need deeper packet inspection, continue with `mqtt-decode`

---
name: log-cleaner-process-context
description: >
  Clean a linear Symfony or Carimali log file by keeping only the lines that contain
  "Process already in progress" or other process-error matches, plus the 3 previous
  lines of context. Use this skill whenever the user has a file like
  `log_322665_03_30.txt`, asks to keep only process-error lines with a small amount of
  context before each error, mentions `grep -B3`, or wants a lighter alternative to the
  block-based `log-cleaner-process` skill.
---

# Log Cleaner — Process Error Context

Focused cleaner for linear log files that keeps only the error line and the 3 lines
immediately before it.

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

## How to run

```bash
python {SKILL_DIR}/scripts/clean_process_error_context.py PATH/TO/log_file.txt
```

Optional flags:

```bash
python {SKILL_DIR}/scripts/clean_process_error_context.py PATH/TO/log_file.txt --before 3
python {SKILL_DIR}/scripts/clean_process_error_context.py PATH/TO/log_file.txt --pattern "Process already in progress"
```

The script writes `<basename>_process_error_context.txt` to the current working directory
and prints a short summary.

## What it does

### Phase 1 — Match lines
Scans the input file line by line and finds every line matching the search pattern.

Default pattern:

- `Process already in progress`

Matching is case-insensitive.

### Phase 2 — Keep previous context
For every matching line, keeps:

- the matching line itself
- the 3 lines immediately before it

If two matches are close together, overlapping windows are merged automatically and
duplicated lines are not repeated.

### Phase 3 — Write the cleaned file
Writes the kept lines in original order without changing their text.

## After running

1. Show the user the summary printed by the script
2. Point them to the generated cleaned file
3. If they need deeper analysis of the extracted packets, continue with `mqtt-decode` or
   other log-analysis steps

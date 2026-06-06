---
name: log-cleaner-process
description: >
  Deep-clean a Symfony log file keeping only "Process already in progress" error blocks
  and filtering out all lines unrelated to the error's serial number.
  Use this skill when the user wants to clean/filter a Carimali/caricare log file
  focusing on "Process already in progress" errors, mentions "pulisci log process",
  "clean process errors", "filtra errori process", or wants to isolate process-error
  blocks by serial number. Also trigger when the user has a log_errori_progess file
  and wants to remove noise.
---

# Log Cleaner — Process Already In Progress

Focused cleaner that takes a block-format Symfony log file and produces a cleaned version
containing only the "Process already in progress" error blocks, with each block stripped
down to only the lines relevant to the error's serial number.

## When to use

- The user has a file like `log_errori_progess_YYYY_MM_DD.txt` (block format with `--` separators)
- They want to remove all blocks that are NOT "Process already in progress" errors
- They want to remove noise lines within kept blocks (other machines' packets, durations, etc.)

## How to run

```bash
python {SKILL_DIR}/scripts/clean_process_errors.py PATH/TO/log_file.txt
```

The script writes `<basename>_clean.txt` to the current working directory and prints a summary.

## What it does

### Phase 1 — Block filtering
Splits the file into blocks (separated by `--`) and drops any block that does not contain
"Process already in progress for serial XXXXX".

### Phase 2 — Line filtering
Within each kept block, extracts the serial number(s) from the error line(s) and removes
all lines that do not mention at least one of those serials. The `--` terminator is always kept.

If a block contains multiple "Process already in progress" errors for different serials,
all serials are collected and lines matching any of them are kept.

## After running

1. Show the user the summary stats (printed to stdout)
2. The cleaned file is ready for further analysis — it can be fed to the `log-analyzer` skill
   or to `mqtt-decode` for payload inspection

# Log Error Cleaning Rules

## Supported formats

- **Block format**: raw grep output with `--` separators — all rules below apply per-block
- **Flat format**: one `app.ERROR` line per row, no `--` separators — only line-level filtering (Rule 4: drop `Troppi errori di processo` lines)

The script auto-detects the format. Flat files skip block-level rules (1, 2, 3, 5) since there is no block context.

## Single Block Definition

A log block is defined as follows, extracted using the command `grep 'app.ERROR' -BX` where `X` is the number of lines before the error line, and `--` is the symbol that marks the end of the block.
```
[2026-03-20 00:45:05] app.INFO: Machine 321946 synchronized [] []
[2026-03-20 00:45:05] app.INFO: Machine 281239 synchronized [] []
[2026-03-20 00:45:05] app.INFO: Packet received [CARIMALI/CONFIG/0000292675]: 30 30 30 30 32 39 32 36 37 35 42 58 16 02 e0 f8 03 00 90 00 00 00 00 00 00 00 00 02 00 00 00 01 01 4e 00 [] []
[2026-03-20 00:45:05] app.INFO: Machine 292676 synchronized [] []
[2026-03-20 00:45:05] app.ERROR: Process already in progress for serial 292675 [] []
--
```

## Cleaning Rules

### 1. Remove unrelated lines

Keep only the lines that contain the serial number found in the `app.ERROR` line.
Remove all other lines, preserving the `--` block terminator.

**Input:**
```
[2026-03-20 00:45:05] app.INFO: Machine 321946 synchronized [] []
[2026-03-20 00:45:05] app.INFO: Machine 281239 synchronized [] []
[2026-03-20 00:45:05] app.INFO: Packet received [CARIMALI/CONFIG/0000292675]: 30 30 30 30 32 39 32 36 37 35 42 58 16 02 e0 f8 03 00 90 00 00 00 00 00 00 00 00 02 00 00 00 01 01 4e 00 [] []
[2026-03-20 00:45:05] app.INFO: Machine 292676 synchronized [] []
[2026-03-20 00:45:05] app.ERROR: Process already in progress for serial 292675 [] []
--
```

**Output:**
```
[2026-03-20 00:45:05] app.INFO: Packet received [CARIMALI/CONFIG/0000292675]: 30 30 30 30 32 39 32 36 37 35 42 58 16 02 e0 f8 03 00 90 00 00 00 00 00 00 00 00 02 00 00 00 01 01 4e 00 [] []
[2026-03-20 00:45:05] app.ERROR: Process already in progress for serial 292675 [] []
--
```

### 2. Remove "Machine N synchronized" lines

These lines are informational and do not indicate an error. Remove all lines containing `Machine <N> synchronized`.

### 3. Remove "Connected machines achieved from broker" lines

These lines are informational and do not indicate an error. Remove all lines containing `app.INFO: Connected machines achieved from broker`.

### 4. Remove entire block for "Troppi errori di processo"

These blocks are informational and it is not possible to determine which error they refer to, so the entire block should be removed.

**Input:**
```
--
[2026-03-20 05:13:54] app.INFO: Duration for a message received on [CARIMALI/VENDING/0000291233]: 189.30 ms [] []
[2026-03-20 05:13:55] app.INFO: Packet received [CARIMALI/DOSEINFO/305354]: 30 30 30 30 33 30 35 33 35 34 4b 50 16 02 e0 f8 03 00 6d 02 00 00 30 30 30 30 30 02 00 00 00 01 01 4e 00 [] []
[2026-03-20 05:13:55] app.INFO: Packet sent [CARIMALI/COMMAND/305354] with delay of 0: 33 30 35 33 35 34 00 00 00 00 4b 50 6c 01 e0 f8 03 00 01 02 00 00 31 32 33 34 35 00 00 00 00 01 01 [] []
[2026-03-20 05:13:55] app.INFO: {"status":"success","command":{"class":"CariSupport\\Machine\\Communication\\Command\\GetGrinderCalibration","data":{"-CariSupport\\Machine\\Communication\\Command\\AbstractSerialCommand-serial":"305354"}}} [] []
[2026-03-20 05:13:55] app.ERROR: Troppi errori di processo: 4 [] []
--
```

**Output:** Remove the entire block.

### 5. Aggregate with id '00000000-0000-0000-0000-000000000000': keep only one line before the error

When the error is `Aggregate with id '00000000-0000-0000-0000-000000000000' not found`, keep only the line immediately before the error line, plus the error line itself.

**Input:**
```
--
[2026-03-20 05:14:35] app.INFO: Duration for a message received on [CARIMALI/DOSEINFO/322681]: 251.32 ms [] []
[2026-03-20 05:14:35] app.INFO: Packet received [CARIMALI/VENDING/322681]: 30 30 30 30 33 32 32 36 38 31 4b 50 04 02 e0 f8 03 00 02 02 00 00 30 30 30 30 30 0c 00 00 00 01 01 3c 00 12 00 e0 f8 03 00 02 02 00 00 [] []
[2026-03-20 05:14:35] app.INFO: Duration for a message received on [CARIMALI/VENDING/322681]: 211.69 ms [] []
[2026-03-20 05:14:36] app.INFO: Packet received [CARIMALI/CONFIG/0000283408]: 30 30 30 30 32 38 33 34 30 38 42 59 16 02 e0 f8 03 00 02 02 00 00 00 00 00 00 00 02 00 00 00 01 01 4e 00 [] []
[2026-03-20 05:14:36] app.ERROR: Aggregate with id '00000000-0000-0000-0000-000000000000' not found [] []
--
```

**Output:**
```
[2026-03-20 05:14:36] app.INFO: Packet received [CARIMALI/CONFIG/0000283408]: 30 30 30 30 32 38 33 34 30 38 42 59 16 02 e0 f8 03 00 02 02 00 00 00 00 00 00 00 02 00 00 00 01 01 4e 00 [] []
[2026-03-20 05:14:36] app.ERROR: Aggregate with id '00000000-0000-0000-0000-000000000000' not found [] []
--
```

---

## Normalization Rules

These rules are applied in `NORMALISE_PATTERNS` (in `analyze_log.py`) after extraction, to collapse variable parts into placeholders so that the same logical error type is counted as one.

### N1. MySQL params serial number

Normalize the serial number inside `with params ["XXXXXX"]` so that all "MySQL server has gone away" errors on different machines are grouped as one error type.

**Input:**
```
An exception occurred while executing '...machines WHERE serial = ? LIMIT 1' with params ["279008"]:  SQLSTATE[HY000]: General error: 2006 MySQL server has gone away
```

**Output:**
```
An exception occurred while executing '...machines WHERE serial = ? LIMIT 1' with params ["{N}"]:  SQLSTATE[HY000]: General error: 2006 MySQL server has gone away
```

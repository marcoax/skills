---
name: message-log-analizer
description: "Analyze Carimali/caricare MQTT message logs and generate Packet received traffic trend reports. Use when the user asks for message trend analysis, Packet received volume, MQTT traffic analysis, per-minute or per-second peaks, message type counts, top machine serials, same-day run comparisons such as log_YYYY_MM_DD_900.txt vs log_YYYY_MM_DD_905.txt, or to update message_trend.html/message_trend.json from a log file or a folder of logs."
---

# Message Log Analizer

Analyze Carimali MQTT traffic logs that contain `Packet received` and `Packet sent` lines. Keep this skill separate from error analysis: it writes `message_trend.html` and `message_trend.json`, never `error_trend.html` or `error_history.json`.

## Workflow

1. If the user did not provide a log file or folder path, ask:
   `Qual e il percorso del file o della cartella di log messaggi da analizzare?`
2. Prefer passing a folder when the user wants the dashboard updated from all available logs:
   ```bash
   python {SKILL_DIR}/scripts/generate_message_trend_report.py PATH/TO/LOG_FOLDER -o message_trend.html --json-output message_trend.json
   ```
   The script expands folders recursively to files named `log_YYYY_MM_DD_HHMM.txt` and generic message logs named `log_message.txt`, sorted by date and run time after parsing. It ignores derived files such as `*_clean.txt` and `*_timing.txt`.
3. For a single file, run:
   ```bash
   python {SKILL_DIR}/scripts/generate_message_trend_report.py PATH/TO/log_YYYY_MM_DD_900.txt -o message_trend.html --json-output message_trend.json
   ```
4. For multiple explicit comparable logs, pass them all in chronological order:
   ```bash
   python {SKILL_DIR}/scripts/generate_message_trend_report.py log_2026_04_14_900.txt log_2026_04_15_900.txt -o message_trend.html --json-output message_trend.json
   ```
5. If multiple files exist for the same day, keep them as separate comparable runs. The report labels them as `YYYY-MM-DD HHMM`, for example `2026-04-21 900` and `2026-04-21 905`.
6. Read `message_trend.json` after generation and summarize the most useful values in chat:
   - analyzed period
   - total `Packet received`
   - average per minute
   - peak minute and count
   - peak second and count
   - highest average/minute day or run
   - highest peak-minute day or run
   - highest peak-second day or run
   - top message types
   - top machine serials
7. Confirm the generated files:
   - `message_trend.html`
   - `message_trend.json`

## Output Contract

The script generates:

| File | Description |
| --- | --- |
| `message_trend.html` | Self-contained HTML dashboard for message volume trend |
| `message_trend.json` | Machine-readable summary used for chat reporting and dashboard data |

The JSON includes a `highlights` object with:
- `topAvgPerMinute`
- `topPeakMinute`
- `topPeakSecond`

Do not move the source log to `backup/`. Message analysis is non-destructive.

When a new log is added to the folder, rerun the skill on the folder. The dashboard is regenerated from all matching files currently present, so it naturally includes the new file and refreshes same-day comparisons.

## Interpreting Results

Use `Packet received` counts as inbound machine traffic. `Packet sent` is counted separately, but the dashboard and summary focus on received traffic by default.

Message type is extracted from the MQTT topic segment after `CARIMALI/`, for example:

| Topic prefix | Type |
| --- | --- |
| `CARIMALI/DOSEINFO/...` | `DOSEINFO` |
| `CARIMALI/CONFIG/...` | `CONFIG` |
| `CARIMALI/VENDING/...` | `VENDING` |
| `CARIMALI/ALARM/...` | `ALARM` |
| `CARIMALI/STATUS/...` | `STATUS` |

The machine serial is extracted from the next topic segment after the message type.

## Manual Fallback

If the script cannot run, inspect lines matching:

```text
[YYYY-MM-DD HH:MM:SS] app.INFO: Packet received [TOPIC]:
```

Then count:
- total received rows
- rows grouped by minute (`HH:MM`)
- rows grouped by second (`HH:MM:SS`)
- message types from the topic
- serials from the topic

Return the same concise summary in chat. Do not update `error_history.json` or `error_trend.html`.

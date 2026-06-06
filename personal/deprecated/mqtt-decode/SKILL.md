---
name: mqtt-decode
description: "Decode a raw Carimali MQTT binary payload (hex string) into a human-readable annotated table. Use whenever the user pastes or mentions a hex payload like '30 30 30 30...' or asks to decode/read/inspect an MQTT packet for Carimali coffee machines (Silver Ace, BlueDot, Evok, Armonia, etc.). Triggers on: 'decode-payload', 'decode payload', 'decodifica payload', 'decode mqtt', 'cosa significa questo payload', 'analizza pacchetto', hex bytes string, 'leggi questo pacchetto mqtt'."
---

# MQTT Payload Decoder — Carimali Protocol

## What it does

Parses any raw hex string payload from the Carimali MQTT protocol and renders a formatted annotated table, broken into **HEADER** (33 bytes, always fixed) and **BODY** (variable, depends on command).

## How to run

When the user provides a hex payload (space-separated bytes), run the decoder script directly:

```bash
python -X utf8 {SKILL_DIR}/scripts/decode_mqtt.py "HH HH HH ..."
```

The output is a Unicode table — present it verbatim in a code block so the alignment renders correctly.

## When the user pastes raw bytes

Sometimes the payload may arrive in different forms:
- Space-separated uppercase: `30 30 30 30 42 58 16 02 ...`
- Space-separated lowercase: `30 30 30 30 42 58 16 02 ...`
- Mixed: `30 30 30 30 42 58 16 02 e3 f8 ...` ← just pass as-is, the script handles it
- Without spaces (raw hex): `303030304258...` ← **the script normalizes this automatically**

If the payload is split across two lines (header + body separately), join them with a space before passing to the script.

## Output

The script produces two Unicode box tables:

1. **HEADER** — always 33 bytes, with fields: Serial, Model, Command, Protocol, Timestamp (date + time), Password, Msg length, Msg number, Msg count
2. **BODY** — decoded based on the command byte, with field names specific to each command type

### Commands with full body decoding:

| Command | Hex | Body decoded |
|---------|-----|-------------|
| EVENT | `0x16` | Event code → event name |
| ALARM | `0x65` | Alarm type (16 bytes ASCII) + alarm code |
| WAKEUP | `0x67` | Wake-up flag |
| READ_MACHINE_PARAMETERS | `0x76` | Param code → key name, code_type, value |
| SET_MACHINE_PARAMETER | `0x75` | Same as 0x76 |
| GET_MACHINE_PARAMETERS | `0x74` | Param code + optional code_type |
| DISPENSING_START | `0x04` | Drink ID, gruppo, timestamp |
| GET_MACHINE_CONFIGURATION | `0x0A` | Full hardware config fields |
| UPLOAD_ALL_PARAMETERS | `0x77` | Upload flag |
| Others | — | Body shown as raw hex |

## After presenting the output

If the command is EVENT, ALARM, or DISPENSING_START, add a one-sentence practical note ONLY when the decoded name does NOT already convey the impact:
- NO note (self-explanatory): `WATER_FILTER_LOW`, `POWER_ON`, `EVENT_WASH_REMINDER_ADVICE_ALL_IN_ONE`
- YES note (needs context): `EVENT_ALARM_END` → "L'allarme precedente è stato risolto dalla macchina."
  `EVENT_DRINK_COMPLETED` → "Erogazione completata; il contatore vending è stato aggiornato."

## Protocol reference

The full protocol documentation is in the project's `payload_mqtt_all.md` file. Consult it if the user asks about fields not covered by the script output or about commands not yet fully decoded.

### Timestamp format

The 8-byte timestamp is two LE uint32 values:
- Bytes 14–17: date as `YYMMDD` decimal (e.g. `260323` = 23 marzo 2026)
- Bytes 18–21: time as `HHMM` decimal (e.g. `437` = 04:37)

### Models

| Code | Modello |
|------|---------|
| `BX` | Silver Ace |
| `BM` | Silver Ace / Silver Ace Power |
| `BL` | Silver Ace (variante) |
| `BD` | BlueDot |
| `BR` | BlueRace |
| `EK` | Evok |
| `AU` / `AL` | Armonia |
| `KP` | KP |

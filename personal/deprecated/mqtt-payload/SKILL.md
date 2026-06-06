---
name: mqtt-payload
description: Generate MQTT binary payload (hex string) for Carimali coffee machine protocol. Use when user wants to build or inspect an MQTT packet for any command (machine parameters 0x74-0x77, alarms 0x65, or any other command). Triggers on keywords like "genera payload", "mqtt payload", "pacchetto mqtt", "payload parametro", "payload allarme".
---

# MQTT Payload Generator — Carimali Protocol

## Reference documents

Before generating any payload, read the following project files for authoritative protocol details and real examples:

- `@docs/payload_mqtt.md` — annotated payload examples for all commands (drink params, alarms, machine parameters 0x74–0x77), header structure, code_type table. **Also contains a "Payload Archive" table at the bottom** — check it FIRST before generating (see Step 0)
- `@www/src/Resources/MachineParameters/dictionary.csv` — full parameter catalog (code, key, readable, writable)
- `@www/tests/Unit/MQTT/Message/Packets.php` — real binary payloads used in tests, covering all code_type variants (0–7), both inbound (0x76) and outbound (0x74/0x75/0x77) directions
- `@www/src/MQTT/Message/CommandTypes.php` — authoritative list of all command codes (constants + descriptions)

Use the examples in `payload_mqtt.md` as ground truth when computing field sizes and encoding.
If a parameter code is found in `dictionary.csv`, include its `key` in the annotation.

You are a binary protocol expert for the Carimali coffee machine MQTT protocol.
When invoked, generate the complete annotated hex payload based on user input.

## Protocol Reference

### Header (33 bytes fixed)

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0 | 10 | Serial | ASCII, zero-padded right (e.g. `0000666000` → `30 30 30 30 36 36 36 30 30 30`) |
| 10 | 2 | Model | ASCII (e.g. `BX` → `42 58`, `BM` → `42 4D`, `BD` → `42 44`) |
| 12 | 1 | Command | See commands table |
| 13 | 1 | Protocol | `02` = v2 (machine→server, default), `01` = v1 (server→machine) |
| 14 | 8 | Timestamp | two LE uint32: `ymd` (e.g. 260312) + `Hi` (e.g. 1320) — compute via Bash at generation time, never use placeholders |
| 22 | 5 | Password | `00 00 00 00 00` for machine→server (default); `31 32 33 34 35` = "12345" for server→machine |
| 27 | 4 | Msg-variable length | little-endian uint32, byte count of body |
| 31 | 1 | Message number | `01` |
| 32 | 1 | Message count | `01` |

### Commands

Full list from `CommandTypes.php`. For the authoritative source read `@www/src/MQTT/Message/CommandTypes.php`.

| Hex | Dec | Constant | Description |
|-----|-----|----------|-------------|
| `00` | 0 | SWITCH_ON | Switch on |
| `01` | 1 | SWITCH_OFF | Switch off |
| `02` | 2 | DRINK_INFORMATION | Drink information + wash counter request |
| `03` | 3 | MACHINE_STATUS | Machine status request |
| `04` | 4 | VENDING_DATA_REQUEST_BY_ID | Vending data request (ID) |
| `05` | 5 | VENDING_DATA_REQUEST_BY_DATE | Vending data request (date) |
| `06` | 6 | RESET_COUNTERS | Reset counters |
| `07` | 7 | RESET_VENDING_DATA_AND_COUNTER | Reset vending data/counters |
| `08` | 8 | GET_PARAMETERS_OF_ONE_DOSE | Get parameters of one dose |
| `09` | 9 | SET_PARAMETERS_OF_ONE_DOSE | Set parameters of one dose |
| `0A` | 10 | GET_MACHINE_CONFIGURATION | Get machine configuration |
| `0B` | 11 | SET_MACHINE_CONFIGURATION | Set machine configuration |
| `0C` | 12 | FIRMWARE_UPDATE_AVAILABLE | Update firmware available |
| `0D` | 13 | REBOOT | Reboot |
| `0E` | 14 | REMINDER | Reminder |
| `0F` | 15 | FORCE_WASH_START | Force wash start |
| `10` | 16 | CHANGE_LANGUAGE | Change language |
| `11` | 17 | WHICH_LANGUAGE_IS_SET | Request which language is set |
| `12` | 18 | UPLOAD_ALL | Request upload |
| `13` | 19 | LOCK_UNLOCK_MACHINE | Lock/Unlock machine |
| `15` | 21 | GET_MDB_PAYMENT_STATUS | Get MDB payment status |
| `16` | 22 | EVENT | Event |
| `1A` | 26 | CHANGE_DRINK_LIST_ITEM_TEXT | Change drink list item text |
| `1B` | 27 | SAVE_DRINK_LIST | Save drink list |
| `1C` | 28 | GET_DRINK_LIST | Get drink list |
| `20` | 32 | START_DRINK | Start drink |
| `65` | 101 | ALARM | Alarm (Machine → Server) |
| `66` | 102 | IS_FIRMWARE_UPDATE_AVAILABLE | Is firmware update available |
| `67` | 103 | WAKEUP | Wakeup |
| `6C` | 108 | GET_GRINDER_CALIBRATION | Get grinder calibration |
| `6F` | 111 | GET_GRINDER_POSITION | Get grinder position servo |
| `70` | 112 | SET_GRINDER_POSITION | Set grinder position |
| `72` | 114 | GET_CONSUMPTIONS_PARAMS | Get consumptions params |
| `73` | 115 | SET_CONSUMPTIONS_PARAMS | Set consumptions params |
| `74` | 116 | GET_MACHINE_PARAMETERS | Get machine parameters |
| `75` | 117 | SET_MACHINE_PARAMETER | Set machine parameters |
| `76` | 118 | READ_MACHINE_PARAMETERS | Read machine parameters (Machine → Server) |
| `77` | 119 | UPLOAD_ALL_PARAMETERS | Request upload all parameters |

### Parameter body structure (commands 0x75 and 0x76)

```
Byte 0-1:  Parameter Code  (little-endian uint16)
Byte 2:    Code Type       (uint8)
Byte 3+:   Value           (size depends on code_type)
```

### Code type encoding

| code_type | Type | Value bytes | Encoding |
|-----------|------|-------------|----------|
| 0 | UINT8 | 1 | unsigned 8-bit |
| 1 | INT8 | 1 | signed 8-bit |
| 2 | UINT16 | 2 | little-endian unsigned |
| 3 | INT16 | 2 | little-endian signed |
| 4 | UINT32 | 4 | little-endian unsigned |
| 5 | INT32 | 4 | little-endian signed |
| 6 | STRING | 2+N | 2-byte little-endian length + UTF-8 bytes |
| 7 | COLOR | 4 | `FF` (alpha fixed) + R + G + B |
| >7 | — | 0 | no value bytes |

### STRING encoding — complete worked example

For `param=30001 value=Europe/Rome` (systemclock_timezone, code_type 6):

```
Step 1 — Parameter code 30001 = 0x7531 → LE uint16: 31 75
Step 2 — code_type 6 → byte: 06
Step 3 — "Europe/Rome" = 11 UTF-8 bytes → length prefix 0B 00 (11 as LE uint16)
Step 4 — UTF-8 bytes: 45 75 72 6F 70 65 2F 52 6F 6D 65
Step 5 — Body (16 bytes total): 31 75  06  0B 00  45 75 72 6F 70 65 2F 52 6F 6D 65
Step 6 — Header Msg-variable length: 10 00 00 00 (16 as LE uint32)
```

Always verify: body byte count = header Msg-variable length value.

### Default values

- Serial default: `0000666000`
- Model default: `BX`
- Protocol default: `02` (machine→server)
- Password default: `00 00 00 00 00` (empty, machine→server)
- Timestamp default: `D8 F8 03 00 28 05 00 00` (2026-03-12 13:20)

---

## Output format

### Step 0 — Archive lookup (always, before any generation)

Before generating a payload, read the **"Payload Archive"** table at the bottom of `docs/payload_mqtt.md` and search for a matching row:
- Match criteria: same `Param` + `Direction` + `Serial` + `Model` + `Value`
- **If match found AND timestamp=default:** return the cached payload directly (skip all generation steps). Inform the user: "Payload recuperato dall'archivio."
- **If match found BUT user requested "orario corrente":** recompute only the timestamp bytes (offset 14-21) in the cached payload, return the updated version.
- **If no match:** proceed with normal generation (Step 1+). After generating, **append the new payload** as a new row to the archive table in `docs/payload_mqtt.md`.

---

### Step 1 — Param direction (only when `param=` is specified without `direction=`)

Call AskUserQuestion with a single direction question:

- `read (0x76)` — la macchina risponde con il valore al server (machine→server, protocol `02`, password `00 00 00 00 00`)
- `get (0x74)` — il server richiede il valore alla macchina (server→machine, protocol `01`, password `31 32 33 34 35`)
- `set (0x75)` — il server imposta il valore sulla macchina (server→machine, protocol `01`, password `31 32 33 34 35`)

Skip this step if `direction=read|get|set` is already in the arguments.

---

### Step 2 — Main questions (always, single AskUserQuestion call)

1. **Tipo di comando** (skip if already specified — `alarm`, `command=`, or direction resolved in Step 1):
   - `Parametro macchina` — un parametro (direzione da Step 1 o argomento)
   - `Allarme (0x65)` — messaggio di allarme macchina → server
   - `Altro comando` — qualsiasi altro comando dalla tabella

   **If Q1 = Parametro macchina AND Step 1 was not executed** (i.e. no `param=` in original arguments): call AskUserQuestion again immediately to ask for direction — same three options as Step 1 (read 0x76 / get 0x74 / set 0x75) — before proceeding to generation.

2. **Formato output**:
   - `Payload completo con spiegazione` — hex payload + breakdown annotato campo per campo
   - `Solo payload hex` — una riga sola, pronta da copiare

3. **Timestamp**:
   - `Orario corrente` — calcola il timestamp reale via Bash (recommended)
   - `Default fisso (D8 F8 03 00 28 05 00 00)` — 2026-03-12 13:20, per test riproducibili

---

### Step 3 — Alarm details (only if Alarm chosen AND type/code not yet specified)

Make a **separate** AskUserQuestion call (not combined with Step 2):

**Tipo allarme** (skip if `type=` already specified):
- `ESGROUP` — Errori gruppo espresso
- `STEAM` — Errori generazione vapore
- `HIGH-LEVEL` — Errori di alto livello
- `GENERAL` — Condizioni di anomalia grave
- (use "Other" to type: FBGROUP, WATERSYSTEM, MISSING COFFEE, MDB, LOW-LEVEL, CONSUMPTIONS, WI-FI, MQTT, RFID, GSM, UNKNOWN)

**Codice allarme** (skip if `code=` already specified):
   Use "Other" in AskUserQuestion to enter the alarm code (integer, e.g. 51)

Before producing any output, silently verify all of the following. Fix any issue before presenting the result — never show this checklist to the user:

1. Il formato corrisponde a quello scelto? (solo riga / completo)
2. Il payload non contiene placeholder? (XX XX o simili — se sì, calcolare il valore reale)
3. Il Msg-variable length nell'header = byte count effettivo del body?
4. Il byte di comando (offset 12) è corretto? (0x74 GET / 0x75 SET / 0x76 READ / 0x65 ALARM)
5. [Solo formato completo] Ogni campo dell'header è annotato separatamente?
6. [Solo formato completo] Se il parametro è nel dizionario, la chiave è inclusa nell'annotazione?

If any check fails: fix the payload silently, then output.

Then produce accordingly:

**If "Solo payload hex":** output a single line of space-separated bytes, nothing else.

**If "Payload completo con spiegazione":**
1. **Hex payload** — one line, space-separated bytes
2. **Annotated breakdown** — each field with its hex, decoded value, byte count, and description
3. **Body size** — show the computed msg-variable length

### Example invocation

> `/mqtt-payload param=113 code_type=4 value=83`

### Example output

```
-- GENERATED PAYLOAD --
30 30 30 30 36 36 36 30 30 30 42 58 76 02 D8 F8 03 00 28 05 00 00 00 00 00 00 00 07 00 00 00 01 01 71 00 04 53 00 00 00

-- HEADER (33 bytes) --
30 30 30 30 36 36 36 30 30 30  [Serial: 0000666000]
42 58                          [Model: BX]
76                             [Command: 0x76 = READ_MACHINE_PARAMETERS]
02                             [Protocol: v2]
D8 F8 03 00 28 05 00 00        [Timestamp: 2026-03-12 13:20, computed via Bash]
00 00 00 00 00                 [Password: empty]
07 00 00 00                    [Msg-variable length: 7 bytes]
01                             [Message number: 1]
01                             [Message count: 1]

-- PARAMETER BODY (7 bytes) --
71 00                          [Parameter Code: 113 = master_param_boiler_temp]
04                             [code_type: 4 = UINT32]
53 00 00 00                    [Value: 83]
```

If the parameter code is in the dictionary below, include its key name in brackets.

---

## Parameter dictionary (code → key)

Partial list of notable parameters for annotation:

| Code | Key |
|------|-----|
| 22 | config_screensaver_timing |
| 23 | config_ledbar_color_index |
| 24 | config_ledbar_rgb_value |
| 67 | max_steam_temperature |
| 103 | config_waterfilter_capacity |
| 104 | database_updated |
| 113 | master_param_boiler_temp |
| 114 | master_param_steam_temp |
| 217 | config_clean_rinse_maintenance_grinder2_limit |
| 10004 | wifi_param_gen_mqtt_brokerurl |
| 10005 | wifi_param_gen_mqtt_port |
| 30001 | systemclock_timezone (code_type 6, STRING) |
| 30003 | display_fw_version_name |
| 30005 | powerboard_fw_version_name |
| 30007 | telemetry_fw_version_name |
| 30009 | wifi_ui_fw_version_name |

For the full dictionary see: `www/src/Resources/MachineParameters/dictionary.csv`

---

## Timestamp computation

The timestamp field is 8 bytes: two little-endian uint32 values packed consecutively.

- **Bytes 0-3:** date as `ymd` integer (e.g. `260312` = March 12, 2026)
- **Bytes 4-7:** time as `Hi` integer (e.g. `1320` = 13:20)

This matches PHP's `pack('V2', (int)$timestamp->format('ymd'), (int)$timestamp->format('Hi'))` in `Header.php`.

**Default behavior:** use the hardcoded default timestamp `D8 F8 03 00 28 05 00 00` (2026-03-12 13:20). If the user requests the current time, run this command:

```bash
python -c "from datetime import datetime;import struct;n=datetime.now();print(' '.join(f'{b:02X}' for b in struct.pack('<II',int(n.strftime('%y%m%d')),int(n.strftime('%H%M')))))"
```

Never use placeholders like `XX XX XX XX XX XX XX XX`.

---

## Alarm payload (command 0x65)

**Direction:** Machine → Server
**Command byte:** `65`
**Protocol:** `02` (machine→server)
**Password:** `00 00 00 00 00` (empty)

### Alarm body structure (18 bytes fixed)

```
Byte 0-15:  Alarm type  (16 bytes, ASCII, space-padded right)
Byte 16:    Alarm code byte 1  (uint8, the alarm code)
Byte 17:    Alarm code byte 2  (uint8, usually 0)
```

**Msg-variable length:** always `12 00 00 00` (18 bytes, as 4-byte little-endian uint32 in the header — not 2 bytes).

### Alarm types

| Type string (16 bytes padded) | Description |
|-------------------------------|-------------|
| `GENERAL         ` | Condizioni di anomalia grave |
| `ESGROUP         ` | Errori del gruppo espresso |
| `FBGROUP         ` | Errori del gruppo fresh brew |
| `STEAM           ` | Errori di generazione vapore |
| `WATERSYSTEM     ` | Mancanza d'acqua durante erogazione |
| `MISSING COFFEE  ` | Mancanza di prodotti |
| `MDB             ` | Errori sistemi di pagamento MDB |
| `GSM             ` | Errori GSM |
| `WI-FI          ` | Errori WI-FI |
| `MQTT            ` | Errori MQTT |
| `RFID            ` | Errori RFID |
| `HIGH-LEVEL      ` | Errori di alto livello non specificati |
| `LOW-LEVEL       ` | Errori di basso livello non specificati |
| `CONSUMPTIONS    ` | Consumo prodotti |
| `UNKNOWN         ` | Tipo non documentato / fallback macchina |

### Alarm body encoding

To encode the alarm type: take the ASCII string, pad with spaces (`20`) on the right to exactly 16 bytes.

Example: `ESGROUP` (7 chars) → `45 53 47 52 4F 55 50 20 20 20 20 20 20 20 20 20`
Example: `WI-FI` (5 chars) → `57 49 2D 46 49 20 20 20 20 20 20 20 20 20 20 20`
Example: `STEAM` (5 chars) → `53 54 45 41 4D 20 20 20 20 20 20 20 20 20 20 20`
Example: `GENERAL` (7 chars) → `47 45 4E 45 52 41 4C 20 20 20 20 20 20 20 20 20`

Rule: always pad with `20` (space) on the right to exactly 16 bytes. Never count from a markdown table — use these hex representations directly.

### Example invocation

> `/mqtt-payload alarm type=ESGROUP code=51`

### Example alarm output

```
-- HEADER (33 bytes) --
30 30 30 30 39 39 38 30 35 30  [Serial: 0000998050]
42 4D                          [Model: BM]
65                             [Command: 0x65 = Alarm]
02                             [Protocol: v2]
D8 F8 03 00 28 05 00 00        [Timestamp: 2026-03-12 13:20, computed via Bash]
00 00 00 00 00                 [Password: empty]
12 00 00 00                    [Msg-variable length: 18 bytes]
01                             [Message number: 1]
01                             [Message count: 1]

-- ALARM BODY (18 bytes) --
45 53 47 52 4F 55 50 20 20 20 20 20 20 20 20 20  [Alarm type: "ESGROUP         "]
33                             [Alarm code: 51 (0x33)]
00                             [Alarm code byte 2: 0]
```

For full alarm code tables per family (ESGROUP, STEAM, HIGH-LEVEL, etc.) see `@docs/payload_mqtt.md`.

---

## Event payload (command 0x16)

**Direction:** Machine → Server
**Command byte:** `16`
**Protocol:** `02` (machine→server)
**Password:** `00 00 00 00 00` (empty)

### Event body structure

Two variants depending on machine family (`Code::isTraditional()`):

**Traditional machines** (2 or 3 bytes):
```
Byte 0-1:  Event code   (LE uint16)
Byte 2:    Group index  (uint8) — present only in 3-byte variant
```

**Non-traditional machines** (2 / 6 / 10 / 14 bytes):
```
Byte 0-1:   Event code         (LE uint16)
--- 14-byte variant only ---
Byte 2-3:   Group index        (LE uint16)
Byte 4-5:   Vending reference  (LE uint16)
Byte 6-7:   Dispensing time    (LE uint16)
Byte 8-9:   Piston position    (LE uint16)
Byte 10-11: Temperature coffee (LE uint16)
Byte 12-13: Temperature steam  (LE uint16)
```

### Event code table

Source: `Event.php` constants.

| Dec | Hex  | Constant |
|-----|------|----------|
| 66  | 0x42 | EVENT_WASH_REMINDER_ADVICE_ALL_IN_ONE |
| 67  | 0x43 | EVENT_WASH_REMINDER_ADVICE_GROUP_ES |
| 68  | 0x44 | EVENT_WASH_REMINDER_ADVICE_GRUPPO_2_FB |
| 69  | 0x45 | EVENT_WASH_REMINDER_ADVICE_MILKER |
| 70  | 0x46 | EVENT_WASH_REMINDER_ADVICE_MIXER |
| 71  | 0x47 | EVENT_WASH_START_ALL_IN_ONE |
| 72  | 0x48 | EVENT_WASH_START_GROUP_ES |
| 73  | 0x49 | EVENT_WASH_START_GROUP_FB |
| 74  | 0x4A | EVENT_WASH_START_MILKER |
| 75  | 0x4B | EVENT_WASH_START_MIXER |
| 76  | 0x4C | EVENT_WASH_START_GRUOP_LIGHT_1_ES |
| 77  | 0x4D | EVENT_WASH_START_GRUOP_LIGHT_2_FB |
| 78  | 0x4E | EVENT_POWER_ON |
| 79  | 0x4F | EVENT_POWER_OFF |
| 80  | 0x50 | EVENT_CHANGE_PARAM |
| 81  | 0x51 | EVENT_CHANGE_DRINK |
| 82  | 0x52 | EVENT_BOILER_EMPTY |
| 83  | 0x53 | EVENT_BOILER_FILL |
| 84  | 0x54 | EVENT_CHANGE_PWD |
| 112 | 0x70 | EVENT_ALARM_END |
| 139 | 0x8B | EVENT_DRINK_COMPLETED |
| 140 | 0x8C | EVENT_WASH_END |
| 141 | 0x8D | EVENT_WASH_START_AUTORINSING_GROUP |
| 142 | 0x8E | EVENT_WASH_START_AUTORINSING_MILKER |

### Example decode

Body `8e 00` (2 bytes): `8e 00` LE uint16 = **142 = `EVENT_WASH_START_AUTORINSING_MILKER`**

---

## Handling ambiguous input

- If code_type is not provided but the parameter key is known and has an obvious type (e.g. timezone = STRING = 6), infer it and state the assumption.
- If value for STRING type is provided as plain text, encode it to UTF-8 hex automatically.
- If value for COLOR type is provided as `#RRGGBB`, split to R G B bytes and prepend `FF` for alpha.
- For alarm type strings: always pad to 16 bytes with spaces, validate the type is in the known list (warn if not).
- Always validate: body size in header must equal actual body byte count.
- When command is `0x16 (EVENT)`, decode bytes 0-1 as LE uint16 event code, look up in the event code table above, and annotate with the constant name. If the body is 14 bytes, also decode and annotate all extended fields (groupIndex, vendingReference, dispensingTime, pistonPosition, temperatureCoffee, temperatureSteam).

## Archive maintenance

After generating any new payload, append it to the **"Payload Archive"** table at the bottom of `docs/payload_mqtt.md` as a new row.
Format: `| {param} | {code_type} | {direction} | {serial} | {model} | {value} | \`{hex}\` |`

The archive stores payloads with the default fixed timestamp. When the user requests "orario corrente", the cached payload is still valid — just replace bytes 14-21 with the computed timestamp.

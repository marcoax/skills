#!/usr/bin/env python3
"""
decode_mqtt.py — Carimali MQTT payload decoder
Usage: python decode_mqtt.py "30 30 30 30 32 39 33 33 38 30 42 58 16 02 e3 f8 03 00 b5 01 00 00 00 00 00 00 00 02 00 00 00 01 01 8e 00"
"""

import sys
import struct

# ── Models ─────────────────────────────────────────────────────────────────────
MODELS = {
    "BD": "BlueDot",
    "BP": "BlueDot Plus",
    "BR": "BlueRace",
    "BQ": "BlueDot (variante)",
    "BI": "BlueDot (variante)",
    "BX": "Silver Ace",
    "BM": "Silver Ace / Silver Ace Power",
    "BL": "Silver Ace (variante)",
    "KP": "KP",
    "EK": "Evok",
    "AU": "Armonia",
    "AL": "Armonia (variante)",
}

# ── Commands ────────────────────────────────────────────────────────────────────
COMMANDS = {
    0x00: "SWITCH_ON",
    0x01: "SWITCH_OFF",
    0x02: "DRINK_INFORMATION",
    0x03: "MACHINE_STATUS",
    0x04: "DISPENSING_START",
    0x05: "VENDING_DATA_REQUEST_BY_DATE",
    0x06: "RESET_COUNTERS",
    0x07: "RESET_VENDING_DATA_AND_COUNTER",
    0x08: "GET_DRINK_PARAMETERS",
    0x09: "SET_DRINK_PARAMETERS",
    0x0A: "GET_MACHINE_CONFIGURATION",
    0x0B: "SET_MACHINE_CONFIGURATION",
    0x0C: "FIRMWARE_UPDATE_AVAILABLE",
    0x0D: "REBOOT",
    0x0E: "REMINDER",
    0x0F: "FORCE_WASH_START",
    0x10: "CHANGE_LANGUAGE",
    0x11: "WHICH_LANGUAGE_IS_SET",
    0x12: "UPLOAD_ALL",
    0x13: "LOCK_UNLOCK_MACHINE",
    0x15: "GET_MDB_PAYMENT_STATUS",
    0x16: "EVENT",
    0x1A: "CHANGE_DRINK_LIST_ITEM_TEXT",
    0x1B: "SAVE_DRINK_LIST",
    0x1C: "GET_DRINK_LIST",
    0x20: "START_DRINK",
    0x65: "ALARM",
    0x66: "IS_FIRMWARE_UPDATE_AVAILABLE",
    0x67: "WAKEUP",
    0x6C: "GET_GRINDER_CALIBRATION",
    0x6F: "GET_GRINDER_POSITION",
    0x70: "SET_GRINDER_POSITION",
    0x72: "GET_CONSUMPTIONS_PARAMS",
    0x73: "SET_CONSUMPTIONS_PARAMS",
    0x74: "GET_MACHINE_PARAMETERS",
    0x75: "SET_MACHINE_PARAMETER",
    0x76: "READ_MACHINE_PARAMETERS",
    0x77: "UPLOAD_ALL_PARAMETERS",
}

# ── Events (CMD 0x16) ───────────────────────────────────────────────────────────
EVENTS = {
    66:  "EVENT_WASH_REMINDER_ADVICE_ALL_IN_ONE",
    67:  "EVENT_WASH_REMINDER_ADVICE_GROUP_ES",
    68:  "EVENT_WASH_REMINDER_ADVICE_GRUPPO_2_FB",
    69:  "EVENT_WASH_REMINDER_ADVICE_MILKER",
    70:  "EVENT_WASH_REMINDER_ADVICE_MIXER",
    71:  "EVENT_WASH_START_ALL_IN_ONE",
    72:  "EVENT_WASH_START_GRUPPO_1_ES",
    73:  "EVENT_WASH_START_GRUPPO_2_FB",
    74:  "EVENT_WASH_START_MILKER",
    75:  "EVENT_WASH_START_MIXER",
    76:  "EVENT_WASH_START_GRUPPO_LIGHT_1_ES",
    77:  "EVENT_WASH_START_GRUPPO_LIGHT_2_FB",
    78:  "POWER_ON",
    79:  "POWER_OFF",
    80:  "EVENT_CHANGE_PARAM",
    81:  "EVENT_CHANGE_DRINK",
    82:  "EVENT_BOILER_EMPTY",
    83:  "EVENT_BOILER_FILL",
    84:  "EVENT_CHANGE_PWD",
    112: "EVENT_ALARM_END",
    139: "EVENT_DRINK_COMPLETED",
    140: "EVENT_WASH_END",
    141: "EVENT_WASH_START_AUTORINSING_GROUP",
    142: "EVENT_WASH_START_AUTORINSING_MILKER",
}

# ── Code types (CMD 0x75/0x76) ──────────────────────────────────────────────────
CODE_TYPES = {
    0: ("UINT8",   1),
    1: ("INT8",    1),
    2: ("UINT16",  2),
    3: ("INT16",   2),
    4: ("UINT32",  4),
    5: ("INT32",   4),
    6: ("STRING",  None),
    7: ("COLOR",   4),
}

# ── Parameter dictionary (partial) ─────────────────────────────────────────────
PARAM_DICT = {
    22:    "config_screensaver_timing",
    23:    "config_ledbar_color_index",
    24:    "config_ledbar_rgb_value",
    35:    "master_param_coffee_pre_infusion_stop",
    67:    "max_steam_temperature",
    103:   "config_waterfilter_capacity",
    104:   "database_updated",
    113:   "master_param_boiler_temp",
    114:   "master_param_steam_temp",
    217:   "config_clean_rinse_maintenance_grinder2_limit",
    10004: "wifi_param_gen_mqtt_brokerurl",
    10005: "wifi_param_gen_mqtt_port",
    30001: "systemclock_timezone",
    30003: "display_fw_version_name",
    30005: "powerboard_fw_version_name",
    30007: "telemetry_fw_version_name",
    30009: "wifi_ui_fw_version_name",
}


def fmt_hex(data: bytes) -> str:
    return " ".join(f"{b:02X}" for b in data)


def decode_timestamp(date_bytes: bytes, time_bytes: bytes):
    """Decode two LE uint32: YYMMDD and HHMM."""
    ymd = struct.unpack("<I", date_bytes)[0]
    hi  = struct.unpack("<I", time_bytes)[0]
    year  = 2000 + (ymd // 10000)
    month = (ymd % 10000) // 100
    day   = ymd % 100
    hour  = hi // 100
    minute = hi % 100
    return f"{day:02d}/{month:02d}/{year}  {hour:02d}:{minute:02d}"


def decode_header(data: bytes) -> dict:
    if len(data) < 33:
        raise ValueError(f"Payload troppo corto: {len(data)} byte (minimo 33)")

    serial   = data[0:10].decode("ascii", errors="replace").rstrip("\x00")
    model_code = data[10:12].decode("ascii", errors="replace")
    model_name = MODELS.get(model_code, "Sconosciuto")
    cmd      = data[12]
    cmd_name = COMMANDS.get(cmd, f"0x{cmd:02X} (sconosciuto)")
    proto    = data[13]
    ts_str   = decode_timestamp(data[14:18], data[18:22])
    pwd      = data[22:27]
    pwd_str  = "vuota (v2)" if pwd == b"\x00" * 5 else pwd.decode("ascii", errors="replace")
    msg_len  = struct.unpack("<I", data[27:31])[0]
    msg_num  = data[31]
    msg_cnt  = data[32]

    return {
        "serial":    (data[0:10],  serial),
        "model":     (data[10:12], f"{model_code} → {model_name}"),
        "command":   (data[12:13], f"0x{cmd:02X} = {cmd_name}"),
        "protocol":  (data[13:14], f"v{proto}"),
        "timestamp": (data[14:22], ts_str),
        "password":  (data[22:27], pwd_str),
        "msg_len":   (data[27:31], f"{msg_len} byte"),
        "msg_num":   (data[31:32], str(msg_num)),
        "msg_cnt":   (data[32:33], str(msg_cnt)),
        "_cmd_byte": cmd,
        "_msg_len":  msg_len,
    }


def decode_body(cmd: int, body: bytes) -> list[tuple[str, bytes, str]]:
    """Returns list of (field_name, raw_bytes, decoded_value)."""
    rows = []

    # ── EVENT (0x16) ────────────────────────────────────────────────────────────
    if cmd == 0x16:
        if len(body) >= 2:
            ev_code = struct.unpack("<H", body[0:2])[0]
            ev_name = EVENTS.get(ev_code, f"0x{ev_code:02X} (sconosciuto)")
            rows.append(("Event code", body[0:2], f"{ev_code} = {ev_name}"))
            # Extended body for DISPENSING_RESULT (0x8B / 139)
            if ev_code == 139 and len(body) > 2:
                rows += _decode_dispensing_result(body[2:])

    # ── ALARM (0x65) ────────────────────────────────────────────────────────────
    elif cmd == 0x65:
        if len(body) >= 18:
            alarm_type = body[0:16].decode("ascii", errors="replace").rstrip()
            alarm_code = body[16]
            alarm_byte2 = body[17] if len(body) > 17 else 0
            rows.append(("Alarm type",    body[0:16], f'"{alarm_type}"'))
            rows.append(("Alarm code",    body[16:17], str(alarm_code)))
            rows.append(("Alarm code b2", body[17:18], str(alarm_byte2)))

    # ── WAKEUP (0x67) ───────────────────────────────────────────────────────────
    elif cmd == 0x67:
        if body:
            rows.append(("Wake-up flag", body[0:1], "01 (accensione/connessione)"))

    # ── READ / SET MACHINE PARAMETERS (0x76 / 0x75) ─────────────────────────────
    elif cmd in (0x76, 0x75):
        rows += _decode_param_body(body)

    # ── GET MACHINE PARAMETERS (0x74) ───────────────────────────────────────────
    elif cmd == 0x74:
        if len(body) >= 2:
            code = struct.unpack("<H", body[0:2])[0]
            key  = PARAM_DICT.get(code, "")
            label = f"{code}" + (f" ({key})" if key else "")
            rows.append(("Parameter code", body[0:2], label))
            if len(body) >= 3:
                rows.append(("Code type", body[2:3], _code_type_label(body[2])))

    # ── UPLOAD ALL PARAMETERS (0x77) ────────────────────────────────────────────
    elif cmd == 0x77:
        if body:
            val = body[0]
            meaning = "Fine upload parametri" if val == 0x01 else f"0x{val:02X}"
            rows.append(("Upload flag", body[0:1], meaning))

    # ── DISPENSING START (0x04) ─────────────────────────────────────────────────
    elif cmd == 0x04:
        if len(body) >= 2:
            drink_id = struct.unpack("<H", body[0:2])[0]
            rows.append(("Drink ID", body[0:2], str(drink_id)))
        if len(body) >= 4:
            group = struct.unpack("<H", body[2:4])[0]
            group_str = f"Gruppo {group + 1}" if group in (0, 8) else f"0x{group:04X}"
            rows.append(("Gruppo/Sorgente", body[2:4], group_str))
        if len(body) >= 12:
            ts_str = decode_timestamp(body[4:8], body[8:12])
            rows.append(("Timestamp body", body[4:12], ts_str))

    # ── GET MACHINE CONFIGURATION (0x0A) ────────────────────────────────────────
    elif cmd == 0x0A:
        if body:
            rows += _decode_machine_config(body)

    # ── Fallback: raw hex ───────────────────────────────────────────────────────
    else:
        if body:
            rows.append(("Body (raw)", body, f"{len(body)} byte"))

    return rows


def _code_type_label(ct: int) -> str:
    info = CODE_TYPES.get(ct)
    if info:
        return f"{ct} = {info[0]}"
    return f"{ct} (sconosciuto)"


def _decode_param_body(body: bytes) -> list:
    rows = []
    if len(body) < 2:
        return rows
    code = struct.unpack("<H", body[0:2])[0]
    key  = PARAM_DICT.get(code, "")
    label = f"{code}" + (f" = {key}" if key else "")
    rows.append(("Parameter code", body[0:2], label))

    if len(body) < 3:
        return rows
    ct = body[2]
    rows.append(("Code type", body[2:3], _code_type_label(ct)))

    val_data = body[3:]
    if ct in CODE_TYPES:
        type_name, size = CODE_TYPES[ct]
        if ct == 6:  # STRING
            if len(val_data) >= 2:
                slen = struct.unpack("<H", val_data[0:2])[0]
                s = val_data[2:2+slen].decode("utf-8", errors="replace")
                rows.append(("String length", val_data[0:2], str(slen)))
                rows.append(("Value (string)", val_data[2:2+slen], f'"{s}"'))
        elif ct == 7:  # COLOR
            if len(val_data) >= 4:
                rows.append(("Value (color)", val_data[0:4],
                             f"A={val_data[0]:02X} R={val_data[1]:02X} G={val_data[2]:02X} B={val_data[3]:02X}"))
        elif size and len(val_data) >= size:
            raw = val_data[0:size]
            if ct in (0,):   v = raw[0]
            elif ct == 1:    v = struct.unpack("b", raw)[0]
            elif ct == 2:    v = struct.unpack("<H", raw)[0]
            elif ct == 3:    v = struct.unpack("<h", raw)[0]
            elif ct == 4:    v = struct.unpack("<I", raw)[0]
            elif ct == 5:    v = struct.unpack("<i", raw)[0]
            else:            v = int.from_bytes(raw, "little")
            rows.append(("Value", raw, str(v)))
    else:
        if val_data:
            rows.append(("Value (raw)", val_data, f"{len(val_data)} byte"))
    return rows


def _decode_dispensing_result(extra: bytes) -> list:
    rows = []
    # Extended body for EVENT_DRINK_COMPLETED (varies by model)
    if len(extra) >= 2:
        rows.append(("Group index",      extra[0:2], str(struct.unpack("<H", extra[0:2])[0])))
    if len(extra) >= 4:
        rows.append(("Vending ref",      extra[2:4], str(struct.unpack("<H", extra[2:4])[0])))
    if len(extra) >= 6:
        rows.append(("Dispensing time",  extra[4:6], str(struct.unpack("<H", extra[4:6])[0])))
    if len(extra) >= 8:
        rows.append(("Piston position",  extra[6:8], str(struct.unpack("<H", extra[6:8])[0])))
    if len(extra) >= 10:
        rows.append(("Temp caffè",       extra[8:10], str(struct.unpack("<H", extra[8:10])[0])))
    if len(extra) >= 12:
        rows.append(("Temp vapore",      extra[10:12], str(struct.unpack("<H", extra[10:12])[0])))
    return rows


def _decode_machine_config(body: bytes) -> list:
    rows = []
    fields = [
        ("Machine type",      1, "char"),
        ("Line voltage",      2, "uint16LE"),
        ("Grinder number",    2, "uint16LE"),
        ("Dispensers",        2, "uint16LE"),
        ("Water tank",        1, "char"),
        ("Milk type",         1, "char"),
        ("Steam nozzle",      2, "uint16LE"),
        ("Unit Plus",         2, "uint16LE"),
        ("Machine config",    2, "uint16LE"),
        ("Remote control",    2, "uint16LE"),
        ("Presence sensor",   1, "char"),
        ("Cup station",       1, "char"),
        ("Cup sensor",        2, "uint16LE"),
        ("WiFi/Ethernet",     1, "char"),
        ("Coffee temp",       2, "uint16LE"),
        ("Steam temp",        2, "uint16LE"),
        ("Display type",      2, "uint16LE"),
        ("Hotwater outlet",   2, "uint16LE"),
        ("Drink PreSel",      2, "uint16LE"),
        ("Coffee str PreSel", 2, "uint16LE"),
        ("Tipo pompa",        2, "uint16LE"),
        ("Tipo gruppo",       2, "uint16LE"),
        ("Optional modules",  2, "uint16LE"),
    ]
    offset = 0
    for name, size, ftype in fields:
        if offset + size > len(body):
            break
        chunk = body[offset:offset+size]
        if ftype == "char":
            val = str(chunk[0])
        elif ftype == "uint16LE":
            val = str(struct.unpack("<H", chunk)[0])
        else:
            val = fmt_hex(chunk)
        rows.append((name, chunk, val))
        offset += size
    return rows


def render_table(header_fields: dict, body_rows: list) -> str:
    """Render nicely formatted Unicode table."""
    # Collect all rows
    rows = []

    # Header section
    HEADER_LABELS = {
        "serial":    ("Serial",     "Seriale macchina (ASCII)"),
        "model":     ("Model",      "Codice modello"),
        "command":   ("Command",    "Codice comando"),
        "protocol":  ("Protocol",   "Versione protocollo"),
        "timestamp": ("Timestamp",  "Data/Ora (LE uint32×2)"),
        "password":  ("Password",   "Password"),
        "msg_len":   ("Msg length", "Lunghezza body (LE uint32)"),
        "msg_num":   ("Msg number", "Numero messaggio"),
        "msg_cnt":   ("Msg count",  "Numero totale messaggi"),
    }

    byte_offset = 0
    for key, value in header_fields.items():
        if key.startswith("_"):
            continue
        raw, decoded = value
        label, note = HEADER_LABELS[key]
        byte_range = f"{byte_offset}–{byte_offset + len(raw) - 1}" if len(raw) > 1 else str(byte_offset)
        rows.append((byte_range, fmt_hex(raw), decoded, note))
        byte_offset += len(raw)

    header_section = rows[:]

    # Body section
    body_section = []
    body_offset = 33
    for name, raw, decoded in body_rows:
        byte_range = f"{body_offset}–{body_offset + len(raw) - 1}" if len(raw) > 1 else str(body_offset)
        body_section.append((byte_range, fmt_hex(raw), decoded, name))
        body_offset += len(raw)

    # Calculate column widths
    all_rows = header_section + body_section
    if not all_rows:
        return "(payload vuoto)"

    col_widths = [
        max(len(r[0]) for r in all_rows),
        max(len(r[1]) for r in all_rows),
        max(len(r[2]) for r in all_rows),
        max(len(r[3]) for r in all_rows),
    ]
    col_widths = [max(w, len(h)) for w, h in zip(col_widths, ["Bytes", "Hex", "Decoded", "Note"])]

    def sep(left, mid, right, fill="─"):
        return left + mid.join(fill * (w + 2) for w in col_widths) + right

    def row_str(cells):
        parts = []
        for i, (cell, w) in enumerate(zip(cells, col_widths)):
            parts.append(f" {cell:<{w}} ")
        return "│" + "│".join(parts) + "│"

    lines = []

    # ── HEADER section ───────────────────────────────────────────────────────────
    lines.append(f"  HEADER (33 byte)")
    lines.append(sep("  ┌", "┬", "┐"))
    lines.append("  " + row_str(["Bytes", "Hex", "Decoded", "Note"]))
    lines.append(sep("  ├", "┼", "┤"))
    for i, r in enumerate(header_section):
        lines.append("  " + row_str(r))
        if i < len(header_section) - 1:
            lines.append(sep("  ├", "┼", "┤"))
    lines.append(sep("  └", "┴", "┘"))

    # ── BODY section ─────────────────────────────────────────────────────────────
    if body_section:
        cmd = header_fields["_cmd_byte"]
        cmd_name = COMMANDS.get(cmd, f"0x{cmd:02X}")
        lines.append(f"\n  BODY — {cmd_name}")
        lines.append(sep("  ┌", "┬", "┐"))
        lines.append("  " + row_str(["Bytes", "Hex", "Decoded", "Note"]))
        lines.append(sep("  ├", "┼", "┤"))
        for i, r in enumerate(body_section):
            lines.append("  " + row_str(r))
            if i < len(body_section) - 1:
                lines.append(sep("  ├", "┼", "┤"))
        lines.append(sep("  └", "┴", "┘"))
    else:
        lines.append("\n  (body vuoto o non decodificato)")

    return "\n".join(lines)


def decode(hex_string: str) -> str:
    tokens = hex_string.strip().split()
    try:
        data = bytes(int(t, 16) for t in tokens)
    except ValueError as e:
        return f"Errore: token non valido — {e}"

    try:
        hdr = decode_header(data)
    except ValueError as e:
        return f"Errore header: {e}"

    body = data[33:]
    body_rows = decode_body(hdr["_cmd_byte"], body)

    return render_table(hdr, body_rows)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python decode_mqtt.py \"HH HH HH ...\"")
        sys.exit(1)
    print(decode(" ".join(sys.argv[1:])))

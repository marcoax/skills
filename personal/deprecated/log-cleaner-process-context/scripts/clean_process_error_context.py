#!/usr/bin/env python3
"""
Keep only process-error lines and a small amount of context before each match.

Default behavior:
- match lines containing "Process already in progress" (case-insensitive)
- keep the 3 previous lines plus the matching line
- merge overlapping windows in the text output
- generate an HTML report showing the command sequence before each error

Usage:
    python clean_process_error_context.py path/to/log.txt
    python clean_process_error_context.py path/to/log.txt --before 5
    python clean_process_error_context.py path/to/log.txt --pattern "process error"
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


DEFAULT_PATTERN = r"Process already in progress"
TIMESTAMP_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")
ERROR_SERIAL_RE = re.compile(r"serial\s+(\d+)", re.IGNORECASE)
PACKET_RECEIVED_RE = re.compile(
    r"Packet received \[CARIMALI/(\w+)/(\d+)\]:\s*((?:[\da-fA-F]{2}\s*)+)"
)
PACKET_SENT_RE = re.compile(
    r"Packet sent \[CARIMALI/(\w+)/(\d+)\].*?:\s*((?:[\da-fA-F]{2}\s*)+)"
)
JSON_COMMAND_RE = re.compile(r'"class":"([^"]+)"')

COMMAND_NAMES = {
    0x00: "MACHINE_ON",
    0x01: "MACHINE_OFF",
    0x04: "DISPENSING_START",
    0x0A: "GET_MACHINE_CONFIG",
    0x11: "GET_LANGUAGES",
    0x16: "EVENT",
    0x17: "EVENT_RESP",
    0x1C: "GET_LABELS",
    0x65: "ALARM",
    0x67: "STATUS",
    0x6C: "GET_GRINDER_CALIB",
    0x74: "GET_MACHINE_PARAMS",
    0x75: "SET_MACHINE_PARAM",
    0x76: "READ_MACHINE_PARAMS",
    0x77: "WRITE_MACHINE_PARAMS",
}

MODEL_NAMES = {
    "BX": "Silver Ace",
    "BM": "Silver Ace",
    "BD": "BlueDot",
    "BR": "BlueRace",
    "EK": "Evok",
    "AU": "Armonia",
    "AL": "Armonia",
    "KP": "KP",
}

EVENT_TYPES = {
    66: "WASH_REMINDER_ALL_IN_ONE",
    67: "WASH_REMINDER_GROUP_ES",
    68: "WASH_REMINDER_GRUPPO_2_FB",
    69: "WASH_REMINDER_MILKER",
    70: "WASH_REMINDER_MIXER",
    71: "WASH_START_ALL_IN_ONE",
    72: "WASH_START_GRUPPO_1_ES",
    73: "WASH_START_GRUPPO_2_FB",
    74: "WASH_START_MILKER",
    75: "WASH_START_MIXER",
    76: "WASH_START_GRUPPO_LIGHT_1_ES",
    77: "WASH_START_GRUPPO_LIGHT_2_FB",
    78: "POWER_ON",
    79: "POWER_OFF",
    80: "CHANGE_PARAM",
    81: "CHANGE_DRINK",
    82: "BOILER_EMPTY",
    83: "BOILER_FILL",
    84: "CHANGE_PWD",
    112: "ALARM_END",
    139: "DRINK_COMPLETED",
    140: "WASH_END",
    141: "WASH_START_AUTORINSING_GROUP",
    142: "WASH_START_AUTORINSING_MILKER",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Keep only log lines matching a process-error pattern plus a number of "
            "previous context lines, then generate an HTML report."
        )
    )
    parser.add_argument("input_file", help="Path to the source log file")
    parser.add_argument(
        "--before",
        type=int,
        default=3,
        help="How many lines before each match to keep (default: 3)",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help='Case-insensitive regex used to detect matching lines (default: "Process already in progress")',
    )
    return parser.parse_args()


def collect_kept_indexes(
    lines: list[str], pattern: re.Pattern[str], before: int
) -> list[int]:
    kept_indexes: set[int] = set()
    for index, line in enumerate(lines):
        if not pattern.search(line):
            continue
        start = max(0, index - before)
        kept_indexes.update(range(start, index + 1))
    return sorted(kept_indexes)


def build_output_path(input_path: Path) -> Path:
    return Path.cwd() / f"{input_path.stem}_process_error_context.txt"


def build_report_path(input_path: Path) -> Path:
    return Path.cwd() / f"{input_path.stem}_process_error_context_report.html"


def extract_timestamp(line: str) -> str | None:
    match = TIMESTAMP_RE.search(line)
    return match.group(1) if match else None


def extract_error_serial(line: str) -> str | None:
    match = ERROR_SERIAL_RE.search(line)
    return match.group(1) if match else None


def decode_payload_header(hex_str: str) -> dict[str, str | int | None]:
    hex_bytes = hex_str.strip().split()
    if len(hex_bytes) < 13:
        return {}
    try:
        model_bytes = bytes([int(hex_bytes[10], 16), int(hex_bytes[11], 16)])
        model_code = model_bytes.decode("ascii", errors="replace")
        command_code = int(hex_bytes[12], 16)
        decoded: dict[str, str | int | None] = {
            "model_code": model_code,
            "model_name": MODEL_NAMES.get(model_code, model_code),
            "command_byte": f"0x{command_code:02X}",
            "command_name": COMMAND_NAMES.get(
                command_code, f"UNKNOWN(0x{command_code:02X})"
            ),
            "event_code": None,
            "event_type": None,
        }
        if command_code == 0x16 and len(hex_bytes) >= 35:
            event_code = int(hex_bytes[34], 16) * 256 + int(hex_bytes[33], 16)
            decoded["event_code"] = event_code
            decoded["event_type"] = EVENT_TYPES.get(
                event_code, f"UNKNOWN(0x{event_code:04X})"
            )
        elif command_code == 0x65:
            decoded["event_code"] = 0x65
            decoded["event_type"] = "ALARM"
        else:
            decoded["event_code"] = command_code
            decoded["event_type"] = decoded["command_name"]
        return decoded
    except (ValueError, IndexError):
        return {}


def shorten_command_class(class_name: str) -> str:
    return class_name.split("\\")[-1]


def parse_context_line(line: str) -> dict[str, str]:
    timestamp = extract_timestamp(line) or ""
    received = PACKET_RECEIVED_RE.search(line)
    if received:
        mqtt_type, serial, hex_str = received.groups()
        decoded = decode_payload_header(hex_str)
        label = f"RX {mqtt_type}"
        detail_parts = []
        if decoded.get("event_type"):
            detail_parts.append(str(decoded["event_type"]))
        if decoded.get("command_byte"):
            detail_parts.append(str(decoded["command_byte"]))
        return {
            "kind": "packet_received",
            "timestamp": timestamp,
            "serial": serial,
            "label": label,
            "detail": " | ".join(detail_parts) or "Packet received",
            "raw": line,
        }

    sent = PACKET_SENT_RE.search(line)
    if sent:
        mqtt_type, serial, hex_str = sent.groups()
        decoded = decode_payload_header(hex_str)
        label = f"TX {mqtt_type}"
        detail_parts = []
        if decoded.get("command_name"):
            detail_parts.append(str(decoded["command_name"]))
        if decoded.get("command_byte"):
            detail_parts.append(str(decoded["command_byte"]))
        return {
            "kind": "packet_sent",
            "timestamp": timestamp,
            "serial": serial,
            "label": label,
            "detail": " | ".join(detail_parts) or "Packet sent",
            "raw": line,
        }

    json_command = JSON_COMMAND_RE.search(line)
    if json_command:
        command_class = shorten_command_class(json_command.group(1))
        return {
            "kind": "app_command",
            "timestamp": timestamp,
            "serial": "",
            "label": "APP CMD",
            "detail": command_class,
            "raw": line,
        }

    if "Process already in progress" in line:
        serial = extract_error_serial(line) or ""
        return {
            "kind": "error",
            "timestamp": timestamp,
            "serial": serial,
            "label": "ERROR",
            "detail": "Process already in progress",
            "raw": line,
        }

    return {
        "kind": "context",
        "timestamp": timestamp,
        "serial": "",
        "label": "CTX",
        "detail": "Context",
        "raw": line,
    }


def build_occurrences(
    lines: list[str], matched_indexes: list[int], before: int
) -> list[dict[str, object]]:
    occurrences: list[dict[str, object]] = []
    for ordinal, match_index in enumerate(matched_indexes, start=1):
        start = max(0, match_index - before)
        window_indexes = list(range(start, match_index + 1))
        context_lines = [lines[index] for index in window_indexes]
        parsed_steps = [parse_context_line(line) for line in context_lines]
        sequence_labels = [
            f"{step['label']}:{step['detail']}"
            for step in parsed_steps
            if step["kind"] != "error"
        ]
        occurrences.append(
            {
                "ordinal": ordinal,
                "line_number": match_index + 1,
                "timestamp": extract_timestamp(lines[match_index]) or "",
                "serial": extract_error_serial(lines[match_index]) or "",
                "error_line": lines[match_index],
                "context_lines": context_lines,
                "steps": parsed_steps,
                "sequence_signature": " -> ".join(sequence_labels) or "(no context)",
            }
        )
    return occurrences


def build_analysis(
    input_lines_count: int, before: int, occurrences: list[dict[str, object]]
) -> dict[str, object]:
    serial_counts: Counter[str] = Counter()
    hourly_counts: Counter[str] = Counter()
    sequence_counts: Counter[str] = Counter()
    step_counts: Counter[str] = Counter()
    detail_counts: Counter[str] = Counter()

    for occurrence in occurrences:
        serial = str(occurrence["serial"])
        timestamp = str(occurrence["timestamp"])
        serial_counts[serial] += 1
        sequence_counts[str(occurrence["sequence_signature"])] += 1
        if timestamp:
            hourly_counts[timestamp[11:13]] += 1

        for step in occurrence["steps"]:
            kind = str(step["kind"])
            if kind == "error":
                continue
            step_counts[str(step["label"])] += 1
            detail_counts[f"{step['label']} | {step['detail']}"] += 1

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_lines": input_lines_count,
        "before": before,
        "total_errors": len(occurrences),
        "unique_serials": len(serial_counts),
        "serials": [
            {"serial": serial, "count": count}
            for serial, count in serial_counts.most_common()
        ],
        "hourly": [
            {"hour": hour, "count": count}
            for hour, count in sorted(hourly_counts.items())
        ],
        "top_sequences": [
            {"sequence": sequence, "count": count}
            for sequence, count in sequence_counts.most_common(10)
        ],
        "top_step_labels": [
            {"label": label, "count": count}
            for label, count in step_counts.most_common(10)
        ],
        "top_step_details": [
            {"detail": detail, "count": count}
            for detail, count in detail_counts.most_common(15)
        ],
        "occurrences": occurrences,
    }


def render_sequence_card(sequence: dict[str, object], max_count: int) -> str:
    width = 12 if max_count <= 0 else max(12, int(sequence["count"]) * 100 // max_count)
    return (
        '<div class="sequence-row">'
        f'<div class="sequence-bar" style="width:{width}%"></div>'
        f'<div class="sequence-count">{sequence["count"]}</div>'
        f'<div class="sequence-text">{html.escape(str(sequence["sequence"]))}</div>'
        "</div>"
    )


def render_occurrence(occurrence: dict[str, object]) -> str:
    lines_html = []
    for step in occurrence["steps"]:
        raw = html.escape(str(step["raw"]))
        label = html.escape(str(step["label"]))
        detail = html.escape(str(step["detail"]))
        kind = html.escape(str(step["kind"]))
        timestamp = html.escape(str(step["timestamp"]))
        lines_html.append(
            '<div class="step-row">'
            f'<div class="step-meta {kind}">{label}</div>'
            '<div class="step-body">'
            f'<div class="step-detail">{detail}</div>'
            f'<div class="step-time">{timestamp}</div>'
            f'<pre>{raw}</pre>'
            "</div>"
            "</div>"
        )
    return (
        '<section class="occurrence-card">'
        '<div class="occurrence-head">'
        f'<div><h3>Error #{occurrence["ordinal"]}</h3>'
        f'<p>serial {html.escape(str(occurrence["serial"]))} | '
        f'line {occurrence["line_number"]} | '
        f'{html.escape(str(occurrence["timestamp"]))}</p></div>'
        "</div>"
        '<div class="signature">'
        f'{html.escape(str(occurrence["sequence_signature"]))}'
        "</div>"
        f'{"".join(lines_html)}'
        "</section>"
    )


def generate_html_report(input_name: str, analysis: dict[str, object]) -> str:
    max_sequence_count = max(
        (int(item["count"]) for item in analysis["top_sequences"]),
        default=1,
    )
    sequence_rows = "".join(
        render_sequence_card(item, max_sequence_count)
        for item in analysis["top_sequences"]
    )
    occurrence_cards = "".join(
        render_occurrence(item) for item in analysis["occurrences"]
    )
    serial_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item['serial']))}</td>"
        f"<td>{item['count']}</td>"
        "</tr>"
        for item in analysis["serials"]
    )
    detail_rows = "".join(
        "<tr>"
        f"<td>{html.escape(str(item['detail']))}</td>"
        f"<td>{item['count']}</td>"
        "</tr>"
        for item in analysis["top_step_details"]
    )
    hourly_json = json.dumps(analysis["hourly"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Process Error Context Report - {html.escape(input_name)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0a0a0f;
      --surface: #12121a;
      --surface-2: #1a1a26;
      --line: rgba(99, 102, 241, 0.15);
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #6366f1;
      --accent-2: #22d3ee;
      --danger: #f43f5e;
      --ok: #10b981;
      --warn: #f59e0b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: radial-gradient(circle at top, rgba(99,102,241,0.12), transparent 35%), var(--bg);
      color: var(--text);
      font-family: "Outfit", sans-serif;
    }}
    .wrap {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      margin-bottom: 28px;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }}
    .eyebrow {{
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    h1 {{
      margin: 10px 0 6px;
      font-size: clamp(32px, 6vw, 54px);
      line-height: 0.95;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }}
    .metric, .panel, .occurrence-card {{
      background: linear-gradient(180deg, var(--surface), var(--surface-2));
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.01) inset;
    }}
    .metric {{
      padding: 18px;
    }}
    .metric .label {{
      color: var(--muted);
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .metric .value {{
      font-size: 34px;
      font-weight: 700;
      margin-top: 8px;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel {{
      padding: 18px;
    }}
    .panel h2 {{
      margin: 0 0 6px;
      font-size: 20px;
    }}
    .panel .sub {{
      color: var(--muted);
      margin-bottom: 16px;
      font-size: 14px;
    }}
    .sequence-row {{
      position: relative;
      margin-bottom: 12px;
      padding: 12px 14px;
      background: rgba(255,255,255,0.02);
      border: 1px solid rgba(255,255,255,0.04);
      border-radius: 14px;
      overflow: hidden;
    }}
    .sequence-bar {{
      position: absolute;
      inset: 0 auto 0 0;
      background: linear-gradient(90deg, rgba(99,102,241,0.22), rgba(34,211,238,0.10));
    }}
    .sequence-count, .sequence-text {{
      position: relative;
      z-index: 1;
    }}
    .sequence-count {{
      font-family: "JetBrains Mono", monospace;
      color: var(--accent-2);
      margin-bottom: 6px;
    }}
    .sequence-text {{
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .occurrence-list {{
      display: grid;
      gap: 16px;
      margin-top: 18px;
    }}
    .occurrence-card {{
      padding: 18px;
    }}
    .occurrence-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      margin-bottom: 14px;
    }}
    .occurrence-head h3 {{
      margin: 0 0 4px;
      font-size: 20px;
    }}
    .occurrence-head p {{
      margin: 0;
      color: var(--muted);
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
    }}
    .signature {{
      margin-bottom: 14px;
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(99,102,241,0.10);
      color: #c7d2fe;
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .step-row {{
      display: grid;
      grid-template-columns: 96px 1fr;
      gap: 12px;
      padding: 10px 0;
      border-top: 1px solid rgba(255,255,255,0.05);
    }}
    .step-meta {{
      align-self: start;
      padding: 6px 10px;
      border-radius: 999px;
      font-family: "JetBrains Mono", monospace;
      font-size: 11px;
      text-align: center;
      background: rgba(255,255,255,0.06);
    }}
    .step-meta.packet_received {{ color: var(--accent-2); }}
    .step-meta.packet_sent {{ color: var(--ok); }}
    .step-meta.app_command {{ color: var(--warn); }}
    .step-meta.error {{ color: #fecdd3; background: rgba(244,63,94,0.18); }}
    .step-detail {{
      font-weight: 600;
      margin-bottom: 2px;
    }}
    .step-time {{
      color: var(--muted);
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      margin-bottom: 8px;
    }}
    pre {{
      margin: 0;
      padding: 12px;
      border-radius: 14px;
      background: rgba(0,0,0,0.22);
      color: #d1d5db;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "JetBrains Mono", monospace;
      font-size: 12px;
      line-height: 1.5;
    }}
    @media (max-width: 960px) {{
      .grid-2 {{
        grid-template-columns: 1fr;
      }}
      .step-row {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="eyebrow">Process Error Context Report</div>
      <h1>Sequence before error</h1>
      <p>{html.escape(input_name)} | generated {html.escape(str(analysis["generated_at"]))}</p>
    </header>

    <section class="metrics">
      <div class="metric"><div class="label">Input lines</div><div class="value">{analysis["input_lines"]}</div></div>
      <div class="metric"><div class="label">Errors found</div><div class="value">{analysis["total_errors"]}</div></div>
      <div class="metric"><div class="label">Unique serials</div><div class="value">{analysis["unique_serials"]}</div></div>
      <div class="metric"><div class="label">Context before</div><div class="value">{analysis["before"]}</div></div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>Top pre-error sequences</h2>
        <div class="sub">Most frequent command chains found immediately before each process error.</div>
        {sequence_rows or '<p class="sub">No sequences found.</p>'}
      </div>
      <div class="panel">
        <h2>Error distribution by hour</h2>
        <div class="sub">Quick view of when the process errors happen.</div>
        <canvas id="hourlyChart" height="260"></canvas>
      </div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>Serials</h2>
        <div class="sub">How many process errors were found per serial.</div>
        <table>
          <thead><tr><th>Serial</th><th>Count</th></tr></thead>
          <tbody>{serial_rows or '<tr><td colspan="2">No serials found</td></tr>'}</tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Most common step details</h2>
        <div class="sub">Decoded packets and app commands seen before the error.</div>
        <table>
          <thead><tr><th>Step</th><th>Count</th></tr></thead>
          <tbody>{detail_rows or '<tr><td colspan="2">No details found</td></tr>'}</tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Error by error timeline</h2>
      <div class="sub">Each card shows the exact context window that led to the process error.</div>
      <div class="occurrence-list">
        {occurrence_cards or '<p class="sub">No occurrences found.</p>'}
      </div>
    </section>
  </div>

  <script>
    const hourly = {hourly_json};
    const ctx = document.getElementById('hourlyChart');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: hourly.map(item => item.hour + ':00'),
        datasets: [{{
          data: hourly.map(item => item.count),
          backgroundColor: 'rgba(34, 211, 238, 0.45)',
          borderColor: '#22d3ee',
          borderWidth: 1.2,
          borderRadius: 8
        }}]
      }},
      options: {{
        plugins: {{
          legend: {{ display: false }}
        }},
        scales: {{
          x: {{
            ticks: {{ color: '#9ca3af' }},
            grid: {{ display: false }}
          }},
          y: {{
            beginAtZero: true,
            ticks: {{ color: '#9ca3af', precision: 0 }},
            grid: {{ color: 'rgba(255,255,255,0.05)' }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        return 1

    if args.before < 0:
        print("--before must be >= 0", file=sys.stderr)
        return 1

    try:
        pattern = re.compile(args.pattern, re.IGNORECASE)
    except re.error as exc:
        print(f"Invalid regex for --pattern: {exc}", file=sys.stderr)
        return 1

    lines = input_path.read_text(encoding="utf-8", errors="replace").splitlines()
    matched_indexes = [
        index for index, line in enumerate(lines) if pattern.search(line)
    ]
    kept_indexes = collect_kept_indexes(lines, pattern, args.before)
    kept_lines = [lines[index] for index in kept_indexes]

    output_path = build_output_path(input_path)
    output_text = "\n".join(kept_lines)
    if kept_lines:
        output_text += "\n"
    output_path.write_text(output_text, encoding="utf-8")

    occurrences = build_occurrences(lines, matched_indexes, args.before)
    analysis = build_analysis(len(lines), args.before, occurrences)
    report_path = build_report_path(input_path)
    report_path.write_text(
        generate_html_report(input_path.stem, analysis), encoding="utf-8"
    )

    print(f"Input lines:     {len(lines)}")
    print(f"Matched lines:   {len(matched_indexes)}")
    print(f"Context before:  {args.before}")
    print(f"Kept lines:      {len(kept_lines)}")
    print(f"Output file:     {output_path}")
    print(f"Output report:   {report_path}")

    if matched_indexes:
        print(
            "Matched line nos:"
            f" {', '.join(str(index + 1) for index in matched_indexes[:20])}"
            + (" ..." if len(matched_indexes) > 20 else "")
        )
    else:
        print("Matched line nos: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

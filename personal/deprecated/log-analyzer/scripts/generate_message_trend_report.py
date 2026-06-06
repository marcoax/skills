#!/usr/bin/env python3
"""Generate an HTML trend report for Carimali Packet received logs."""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, time
from pathlib import Path
from statistics import mean


LINE_RE = re.compile(
    r"^\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+"
    r"app\.(?P<level>[A-Z]+):\s+"
    r"(?P<event>Packet received|Packet sent)\s+"
    r"\[(?P<topic>[^\]]+)\]:"
)


@dataclass
class DayStats:
    source: str
    date: str | None = None
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    total_received: int = 0
    total_sent: int = 0
    minute_counts: Counter[str] = field(default_factory=Counter)
    second_counts: Counter[str] = field(default_factory=Counter)
    type_counts: Counter[str] = field(default_factory=Counter)
    topic_counts: Counter[str] = field(default_factory=Counter)
    serial_counts: Counter[str] = field(default_factory=Counter)

    def register(self, ts: datetime, event: str, topic: str) -> None:
        self.first_ts = ts if self.first_ts is None else min(self.first_ts, ts)
        self.last_ts = ts if self.last_ts is None else max(self.last_ts, ts)
        self.date = ts.strftime("%Y-%m-%d")

        if event == "Packet received":
            self.total_received += 1
            self.minute_counts[ts.strftime("%H:%M")] += 1
            self.second_counts[ts.strftime("%H:%M:%S")] += 1

            parts = topic.split("/")
            if len(parts) >= 3:
                message_type = parts[1]
                serial = parts[2]
            elif len(parts) >= 2:
                message_type = parts[1]
                serial = ""
            else:
                message_type = "UNKNOWN"
                serial = ""

            self.type_counts[message_type] += 1
            self.topic_counts["/".join(parts[:2]) if len(parts) >= 2 else topic] += 1
            if serial:
                self.serial_counts[serial] += 1
        elif event == "Packet sent":
            self.total_sent += 1

    @property
    def active_minutes(self) -> int:
        return len(self.minute_counts)

    @property
    def avg_per_minute(self) -> float:
        if not self.minute_counts:
            return 0.0
        return mean(self.minute_counts.values())

    @property
    def peak_minute(self) -> tuple[str, int]:
        if not self.minute_counts:
            return ("--", 0)
        return max(self.minute_counts.items(), key=lambda item: (item[1], item[0]))

    @property
    def peak_second(self) -> tuple[str, int]:
        if not self.second_counts:
            return ("--", 0)
        return max(self.second_counts.items(), key=lambda item: (item[1], item[0]))

    def to_payload(self) -> dict:
        peak_minute, peak_minute_count = self.peak_minute
        peak_second, peak_second_count = self.peak_second
        return {
            "source": self.source,
            "date": self.date,
            "first": self.first_ts.isoformat(sep=" ") if self.first_ts else None,
            "last": self.last_ts.isoformat(sep=" ") if self.last_ts else None,
            "totalReceived": self.total_received,
            "totalSent": self.total_sent,
            "activeMinutes": self.active_minutes,
            "avgPerMinute": round(self.avg_per_minute, 2),
            "peakMinute": peak_minute,
            "peakMinuteCount": peak_minute_count,
            "peakSecond": peak_second,
            "peakSecondCount": peak_second_count,
            "minuteCounts": dict(sorted(self.minute_counts.items())),
            "typeCounts": dict(self.type_counts.most_common()),
            "topicCounts": dict(self.topic_counts.most_common()),
            "topSerials": self.serial_counts.most_common(10),
        }


def parse_log(path: Path) -> DayStats:
    stats = DayStats(source=str(path))
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = LINE_RE.match(line)
            if not match:
                continue
            ts = datetime.strptime(match.group("ts"), "%Y-%m-%d %H:%M:%S")
            stats.register(ts, match.group("event"), match.group("topic"))
    return stats


def minute_range(start: str, end: str) -> list[str]:
    start_hour, start_minute = map(int, start.split(":"))
    end_hour, end_minute = map(int, end.split(":"))
    current = start_hour * 60 + start_minute
    final = end_hour * 60 + end_minute
    if final < current:
        final += 24 * 60
    labels = []
    while current <= final:
        labels.append(f"{(current // 60) % 24:02d}:{current % 60:02d}")
        current += 1
    return labels


def common_minute_labels(days: list[DayStats]) -> list[str]:
    with_times = [day for day in days if day.first_ts and day.last_ts]
    if not with_times:
        return []
    start = max(day.first_ts.time().replace(second=0, microsecond=0) for day in with_times)
    end = min(day.last_ts.time().replace(second=0, microsecond=0) for day in with_times)
    return minute_range(start.strftime("%H:%M"), end.strftime("%H:%M"))


def format_int(value: int | float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_float(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


def pct_delta(current: int, previous: int) -> str:
    if previous == 0:
        return "--"
    value = ((current - previous) / previous) * 100
    return f"{value:+.1f}%".replace(".", ",")


def td(value: object, class_name: str = "") -> str:
    class_attr = f' class="{class_name}"' if class_name else ""
    return f"<td{class_attr}>{html.escape(str(value))}</td>"


def th(value: object, class_name: str = "") -> str:
    class_attr = f' class="{class_name}"' if class_name else ""
    return f"<th{class_attr}>{html.escape(str(value))}</th>"


def build_minute_rows(payload: dict, labels: list[str]) -> str:
    days = payload["days"]
    max_count = max(
        [day["minuteCounts"].get(label, 0) for day in days for label in labels] or [1]
    )
    rows = []
    for label in labels:
        values = [day["minuteCounts"].get(label, 0) for day in days]
        delta = values[-1] - values[0] if len(values) >= 2 else 0
        cells = [td(label, "mono strong")]
        for value in values:
            width = 0 if max_count == 0 else round((value / max_count) * 100, 2)
            cells.append(
                "<td>"
                f'<div class="bar-cell"><span>{format_int(value)}</span>'
                f'<div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div></div>'
                "</td>"
            )
        cells.append(td(f"{delta:+d}", "delta-pos" if delta > 0 else "delta-neg" if delta < 0 else ""))
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return "\n".join(rows)


def build_type_rows(payload: dict) -> str:
    days = payload["days"]
    all_types = sorted({name for day in days for name in day["typeCounts"]})
    rows = []
    for message_type in all_types:
        values = [day["typeCounts"].get(message_type, 0) for day in days]
        total = sum(values)
        if total == 0:
            continue
        delta = values[-1] - values[0] if len(values) >= 2 else 0
        cells = [td(message_type, "strong")]
        cells.extend(td(format_int(value), "num") for value in values)
        cells.append(td(f"{delta:+d}", "delta-pos" if delta > 0 else "delta-neg" if delta < 0 else ""))
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return "\n".join(rows)


def build_top_serial_rows(payload: dict) -> str:
    rows = []
    for day in payload["days"]:
        for serial, count in day["topSerials"][:5]:
            rows.append(
                "<tr>"
                + td(day["date"], "mono")
                + td(serial, "mono strong")
                + td(format_int(count), "num")
                + "</tr>"
            )
    return "\n".join(rows)


def build_svg(payload: dict, labels: list[str]) -> str:
    days = payload["days"]
    width = 980
    height = 300
    pad_left = 54
    pad_bottom = 48
    chart_w = width - pad_left - 24
    chart_h = height - 34 - pad_bottom
    max_count = max([day["minuteCounts"].get(label, 0) for day in days for label in labels] or [1])
    group_w = chart_w / max(len(labels), 1)
    bar_w = max(8, min(34, (group_w - 10) / max(len(days), 1)))
    colors = ["#2563eb", "#059669", "#dc2626", "#7c3aed"]

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Messaggi ricevuti per minuto">',
        '<line class="axis" x1="54" y1="252" x2="956" y2="252"></line>',
        '<line class="axis" x1="54" y1="34" x2="54" y2="252"></line>',
    ]
    for tick in range(0, 5):
        value = round(max_count * tick / 4)
        y = 252 - (value / max_count * chart_h if max_count else 0)
        parts.append(f'<line class="grid" x1="54" y1="{y:.2f}" x2="956" y2="{y:.2f}"></line>')
        parts.append(f'<text class="tick" x="44" y="{y + 4:.2f}" text-anchor="end">{value}</text>')

    for index, label in enumerate(labels):
        group_x = pad_left + index * group_w + 7
        label_x = pad_left + index * group_w + group_w / 2
        parts.append(f'<text class="tick" x="{label_x:.2f}" y="276" text-anchor="middle">{label}</text>')
        for day_index, day in enumerate(days):
            value = day["minuteCounts"].get(label, 0)
            bar_h = value / max_count * chart_h if max_count else 0
            x = group_x + day_index * (bar_w + 4)
            y = 252 - bar_h
            color = colors[day_index % len(colors)]
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" '
                f'rx="3" fill="{color}"><title>{day["date"]} {label}: {value}</title></rect>'
            )
    parts.append("</svg>")
    return "\n".join(parts)


def build_html(payload: dict) -> str:
    days = payload["days"]
    labels = payload["commonMinuteLabels"]
    generated_at = payload["generatedAt"]
    minute_rows = build_minute_rows(payload, labels)
    type_rows = build_type_rows(payload)
    top_serial_rows = build_top_serial_rows(payload)
    chart_svg = build_svg(payload, labels)
    data_json = json.dumps(payload, ensure_ascii=True, indent=2)

    first_day = days[0]
    last_day = days[-1]
    delta_total = last_day["totalReceived"] - first_day["totalReceived"] if len(days) >= 2 else 0
    delta_class = "good" if delta_total < 0 else "warn" if delta_total > 0 else ""

    card_html = []
    for day in days:
        card_html.append(
            f"""
            <article class="metric-card">
                <p class="eyebrow">{html.escape(day["date"] or "n.d.")}</p>
                <h2>{format_int(day["totalReceived"])}</h2>
                <p>messaggi ricevuti in {day["activeMinutes"]} minuti attivi</p>
                <dl>
                    <div><dt>Media/min</dt><dd>{format_float(day["avgPerMinute"])}</dd></div>
                    <div><dt>Picco minuto</dt><dd>{html.escape(day["peakMinute"])} ({format_int(day["peakMinuteCount"])})</dd></div>
                    <div><dt>Picco secondo</dt><dd>{html.escape(day["peakSecond"])} ({format_int(day["peakSecondCount"])})</dd></div>
                </dl>
            </article>
            """
        )

    return f"""<!doctype html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="Cache-Control" content="no-store">
    <title>Trend messaggi ricevuti</title>
    <style>
        :root {{
            color-scheme: light;
            --ink: #172033;
            --muted: #5b6475;
            --line: #d9dee8;
            --paper: #f7f8fb;
            --panel: #ffffff;
            --blue: #2563eb;
            --green: #059669;
            --red: #dc2626;
            --amber: #b45309;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            background: var(--paper);
            color: var(--ink);
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.45;
        }}
        main {{
            max-width: 1180px;
            margin: 0 auto;
            padding: 30px 18px 56px;
        }}
        header {{
            display: grid;
            gap: 14px;
            border-bottom: 1px solid var(--line);
            padding-bottom: 22px;
            margin-bottom: 22px;
        }}
        h1, h2, h3 {{ margin: 0; line-height: 1.15; }}
        h1 {{ font-size: 34px; }}
        h3 {{ font-size: 19px; margin-bottom: 12px; }}
        p {{ margin: 0; }}
        .eyebrow {{
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin: 22px 0;
        }}
        .metric-card, .panel {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 10px 24px rgba(23, 32, 51, 0.06);
        }}
        .metric-card {{ padding: 18px; }}
        .metric-card h2 {{ font-size: 36px; margin-top: 8px; }}
        .metric-card p {{ color: var(--muted); margin-top: 4px; }}
        .metric-card dl {{
            display: grid;
            gap: 8px;
            margin: 16px 0 0;
        }}
        .metric-card div {{
            display: flex;
            justify-content: space-between;
            gap: 14px;
            border-top: 1px solid var(--line);
            padding-top: 8px;
        }}
        dt {{ color: var(--muted); }}
        dd {{ margin: 0; font-weight: 700; text-align: right; }}
        .delta-card {{
            padding: 18px;
            border-radius: 8px;
            background: #fff7ed;
            border: 1px solid #fed7aa;
        }}
        .delta-card h2 {{ font-size: 36px; margin-top: 8px; }}
        .delta-card.good {{ background: #ecfdf5; border-color: #a7f3d0; }}
        .delta-card.warn {{ background: #fef2f2; border-color: #fecaca; }}
        .panel {{ padding: 18px; margin-top: 18px; overflow: hidden; }}
        .chart-wrap {{ width: 100%; overflow-x: auto; }}
        svg {{ width: 100%; min-width: 760px; display: block; }}
        .axis {{ stroke: #748095; stroke-width: 1; }}
        .grid {{ stroke: #e3e7ef; stroke-width: 1; }}
        .tick {{ fill: #5b6475; font-size: 12px; }}
        .legend {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            margin-top: 12px;
            color: var(--muted);
            font-size: 13px;
        }}
        .legend span::before {{
            content: "";
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 3px;
            margin-right: 6px;
            vertical-align: -1px;
            background: var(--legend-color);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th, td {{
            border-bottom: 1px solid var(--line);
            padding: 10px 8px;
            text-align: left;
            vertical-align: middle;
        }}
        th {{
            color: var(--muted);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0;
        }}
        tr:last-child td {{ border-bottom: 0; }}
        .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .mono {{ font-family: Consolas, Monaco, monospace; }}
        .strong {{ font-weight: 700; }}
        .delta-pos {{ color: var(--red); font-weight: 700; }}
        .delta-neg {{ color: var(--green); font-weight: 700; }}
        .bar-cell {{
            display: grid;
            grid-template-columns: 46px minmax(90px, 1fr);
            align-items: center;
            gap: 10px;
            font-variant-numeric: tabular-nums;
        }}
        .bar-track {{
            height: 10px;
            background: #e7ebf2;
            border-radius: 5px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            background: var(--blue);
            border-radius: 5px;
        }}
        .notes {{
            color: var(--muted);
            display: grid;
            gap: 6px;
            margin-top: 12px;
            font-size: 13px;
        }}
        code {{
            background: #eef2f7;
            border: 1px solid #dde3ed;
            border-radius: 4px;
            padding: 1px 5px;
        }}
        details {{
            margin-top: 18px;
            color: var(--muted);
        }}
        pre {{
            overflow: auto;
            background: #111827;
            color: #e5e7eb;
            padding: 14px;
            border-radius: 8px;
            max-height: 340px;
        }}
        @media (max-width: 820px) {{
            h1 {{ font-size: 28px; }}
            .summary {{ grid-template-columns: 1fr; }}
            table {{ font-size: 13px; }}
            th, td {{ padding: 9px 6px; }}
            .bar-cell {{ grid-template-columns: 38px minmax(70px, 1fr); }}
        }}
    </style>
</head>
<body>
<main>
    <header>
        <p class="eyebrow">Report generato il {html.escape(generated_at)}</p>
        <h1>Trend messaggi ricevuti</h1>
        <p>Confronto dei pacchetti <code>Packet received</code> nello stesso intervallo dei log: {html.escape(payload["commonPeriodLabel"])}.</p>
    </header>

    <section class="summary">
        {''.join(card_html)}
        <article class="delta-card {delta_class}">
            <p class="eyebrow">Differenza {html.escape(first_day["date"] or "")} -> {html.escape(last_day["date"] or "")}</p>
            <h2>{delta_total:+d}</h2>
            <p>{pct_delta(last_day["totalReceived"], first_day["totalReceived"])} rispetto al giorno precedente nel campione.</p>
            <p class="notes">Righe <code>Packet sent</code> rilevate: {format_int(sum(day["totalSent"] for day in days))}.</p>
        </article>
    </section>

    <section class="panel">
        <h3>Messaggi per minuto</h3>
        <div class="chart-wrap">
            {chart_svg}
        </div>
        <div class="legend">
            {''.join(f'<span style="--legend-color: {color}">{html.escape(day["date"] or "n.d.")}</span>' for color, day in zip(["#2563eb", "#059669", "#dc2626", "#7c3aed"], days))}
        </div>
    </section>

    <section class="panel">
        <h3>Dettaglio per minuto</h3>
        <table>
            <thead>
                <tr>
                    {th("Minuto")}
                    {''.join(th(day["date"], "num") for day in days)}
                    {th("Delta", "num")}
                </tr>
            </thead>
            <tbody>
                {minute_rows}
            </tbody>
        </table>
    </section>

    <section class="panel">
        <h3>Distribuzione per tipo MQTT</h3>
        <table>
            <thead>
                <tr>
                    {th("Tipo")}
                    {''.join(th(day["date"], "num") for day in days)}
                    {th("Delta", "num")}
                </tr>
            </thead>
            <tbody>
                {type_rows}
            </tbody>
        </table>
    </section>

    <section class="panel">
        <h3>Seriali piu presenti</h3>
        <table>
            <thead>
                <tr>{th("Giorno")}{th("Seriale")}{th("Messaggi", "num")}</tr>
            </thead>
            <tbody>{top_serial_rows}</tbody>
        </table>
        <div class="notes">
            <p>I conteggi sono basati solo sulle righe riconosciute con formato <code>[data] app.INFO: Packet received [CARIMALI/TIPO/SERIALE]</code>.</p>
            <p>File sorgenti: {', '.join(html.escape(day["source"]) for day in days)}</p>
        </div>
    </section>

    <details>
        <summary>Dati JSON incorporati</summary>
        <pre>{html.escape(data_json)}</pre>
    </details>
</main>
</body>
</html>
"""


def build_payload(days: list[DayStats]) -> dict:
    labels = common_minute_labels(days)
    if labels:
        common_period = f"{labels[0]} - {labels[-1]}"
    else:
        common_period = "nessun intervallo comune"
    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "commonPeriodLabel": common_period,
        "commonMinuteLabels": labels,
        "days": [day.to_payload() for day in days],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an HTML report for Packet received volume by minute."
    )
    parser.add_argument(
        "logs",
        nargs="+",
        type=Path,
        help="Log files to compare, for example log_2026_04_14_900.txt log_2026_04_15_900.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("message_trend.html"),
        help="Output HTML path. Defaults to message_trend.html",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Output JSON path. Defaults to the HTML output path with .json extension.",
    )
    args = parser.parse_args()

    days = [parse_log(path) for path in args.logs]
    days.sort(key=lambda day: day.date or day.source)

    if not any(day.total_received for day in days):
        raise SystemExit("No Packet received lines found in the provided logs.")

    payload = build_payload(days)
    args.output.write_text(build_html(payload), encoding="utf-8")
    json_output = args.json_output or args.output.with_suffix(".json")
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Generated {args.output}")
    print(f"Generated {json_output}")
    for day in payload["days"]:
        print(
            f"{day['date']}: {day['totalReceived']} received, "
            f"avg {day['avgPerMinute']}/min, peak {day['peakMinute']}={day['peakMinuteCount']}"
        )
    print(f"Common minute period: {payload['commonPeriodLabel']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

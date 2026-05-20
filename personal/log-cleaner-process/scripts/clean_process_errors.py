#!/usr/bin/env python3
"""
Deep cleaner for 'Process already in progress' log blocks.

Reads a Symfony log file in block format (blocks separated by '--'),
keeps only blocks containing 'Process already in progress' errors,
and within those blocks keeps only lines mentioning the relevant serial(s).

Produces:
  - <basename>_clean.txt   — cleaned log
  - <basename>_report.html — interactive dashboard (same look as error_trend.html)

Usage:
    python clean_process_errors.py <input_log_file>
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROCESS_SERIAL_RE = re.compile(r'Process already in progress for serial (\d+)')
TIMESTAMP_RE = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]')
PACKET_RE = re.compile(
    r'Packet received \[CARIMALI/(\w+)/\d*(\d{5,10})\]:\s*((?:[\da-fA-F]{2}\s*)+)'
)

# MQTT command type names (byte 12 of header)
COMMAND_NAMES = {
    0x00: 'MACHINE_ON', 0x01: 'MACHINE_OFF', 0x04: 'DISPENSING_START',
    0x16: 'EVENT', 0x17: 'EVENT_RESP', 0x65: 'ALARM',
    0x6C: 'GET_GRINDER_CALIB', 0x74: 'GET_MACHINE_PARAMS',
    0x75: 'SET_MACHINE_PARAM', 0x76: 'READ_MACHINE_PARAMS',
    0x77: 'WRITE_MACHINE_PARAMS',
}

MODEL_NAMES = {
    'BX': 'Silver Ace', 'BM': 'Silver Ace', 'BD': 'BlueDot',
    'BR': 'BlueRace', 'EK': 'Evok', 'AU': 'Armonia',
    'AL': 'Armonia', 'KP': 'KP',
}

# Event type codes decoded from body bytes 0-1 (LE uint16) of EVENT (0x16) packets
EVENT_TYPES = {
    66: 'WASH_REMINDER_ALL_IN_ONE', 67: 'WASH_REMINDER_GROUP_ES',
    68: 'WASH_REMINDER_GRUPPO_2_FB', 69: 'WASH_REMINDER_MILKER',
    70: 'WASH_REMINDER_MIXER', 71: 'WASH_START_ALL_IN_ONE',
    72: 'WASH_START_GRUPPO_1_ES', 73: 'WASH_START_GRUPPO_2_FB',
    74: 'WASH_START_MILKER', 75: 'WASH_START_MIXER',
    76: 'WASH_START_GRUPPO_LIGHT_1_ES', 77: 'WASH_START_GRUPPO_LIGHT_2_FB',
    78: 'POWER_ON', 79: 'POWER_OFF',
    80: 'CHANGE_PARAM', 81: 'CHANGE_DRINK',
    82: 'BOILER_EMPTY', 83: 'BOILER_FILL', 84: 'CHANGE_PWD',
    112: 'ALARM_END',
    139: 'DRINK_COMPLETED', 140: 'WASH_END',
    141: 'WASH_START_AUTORINSING_GROUP', 142: 'WASH_START_AUTORINSING_MILKER',
}


def split_blocks(lines: list[str]) -> list[list[str]]:
    """Split raw log lines into blocks delimited by '--'."""
    blocks = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if line.strip() == '--':
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def extract_process_serials(block_lines: list[str]) -> list[str]:
    """
    Extract all unique serial numbers from 'Process already in progress'
    error lines within a block. Returns empty list if none found.
    """
    serials = []
    for line in block_lines:
        m = PROCESS_SERIAL_RE.search(line)
        if m and m.group(1) not in serials:
            serials.append(m.group(1))
    return serials


def filter_block_lines(block_lines: list[str], serials: list[str]) -> list[str]:
    """
    Keep only lines that contain at least one of the given serials,
    plus the '--' block terminator.
    """
    kept = []
    for line in block_lines:
        if line.strip() == '--':
            kept.append(line)
            continue
        if any(s in line for s in serials):
            kept.append(line)
    return kept


def decode_payload_header(hex_str: str) -> dict:
    """Decode MQTT payload: header (model, command) + body event type."""
    hex_bytes = hex_str.strip().split()
    if len(hex_bytes) < 13:
        return {}
    try:
        model_bytes = bytes([int(hex_bytes[10], 16), int(hex_bytes[11], 16)])
        model_code = model_bytes.decode('ascii', errors='replace')
        cmd_byte = int(hex_bytes[12], 16)
        result = {
            'model_code': model_code,
            'model_name': MODEL_NAMES.get(model_code, model_code),
            'command_byte': f'0x{cmd_byte:02X}',
            'command_name': COMMAND_NAMES.get(cmd_byte, f'UNKNOWN(0x{cmd_byte:02X})'),
            'event_type': None,
            'event_code': None,
        }
        # Decode event type from body (bytes 33-34, LE uint16) for EVENT commands
        if cmd_byte == 0x16 and len(hex_bytes) >= 35:
            ev_code = int(hex_bytes[34], 16) * 256 + int(hex_bytes[33], 16)
            result['event_code'] = ev_code
            result['event_type'] = EVENT_TYPES.get(ev_code, f'UNKNOWN(0x{ev_code:04X})')
        elif cmd_byte == 0x65:
            result['event_type'] = 'ALARM'
            result['event_code'] = 0x65
        else:
            cmd_name = COMMAND_NAMES.get(cmd_byte, f'0x{cmd_byte:02X}')
            result['event_type'] = cmd_name
            result['event_code'] = cmd_byte
        return result
    except (ValueError, IndexError):
        return {}


def extract_block_data(block_lines: list[str], serials: list[str]) -> dict:
    """Extract timestamp, payload info from a filtered block."""
    data = {'serials': serials, 'timestamp': None, 'payloads': []}
    for line in block_lines:
        ts_m = TIMESTAMP_RE.search(line)
        if ts_m and data['timestamp'] is None:
            data['timestamp'] = ts_m.group(1)
        pkt_m = PACKET_RE.search(line)
        if pkt_m:
            mqtt_type = pkt_m.group(1)
            pkt_serial = pkt_m.group(2).lstrip('0') or '0'
            hex_str = pkt_m.group(3).strip()
            if any(s == pkt_serial or s in line for s in serials):
                header = decode_payload_header(hex_str)
                data['payloads'].append({
                    'mqtt_type': mqtt_type,
                    'hex': hex_str,
                    **header,
                })
    return data


def build_analysis(kept_blocks_data: list[dict]) -> dict:
    """Build analysis data structure for the HTML report."""
    serial_counts = defaultdict(int)
    serial_model = {}
    hourly = defaultdict(int)
    event_type_counts = defaultdict(int)
    total_errors = 0

    # Correlation: (previous_event, trigger_event) -> count
    correlation_counts = defaultdict(int)
    single_trigger_counts = defaultdict(int)
    no_packet_count = 0

    for bd in kept_blocks_data:
        # Get ordered payloads with event_type
        payloads_with_event = [p for p in bd['payloads'] if p.get('event_type')]

        # Determine trigger event (last payload) and previous (first payload if 2+)
        trigger_event = None
        if payloads_with_event:
            trigger_event = payloads_with_event[-1]['event_type']

        for s in bd['serials']:
            serial_counts[s] += 1
            total_errors += 1
            if trigger_event:
                event_type_counts[trigger_event] += 1
            if s not in serial_model and bd['payloads']:
                for p in bd['payloads']:
                    if p.get('model_code'):
                        serial_model[s] = {
                            'model_code': p['model_code'],
                            'model_name': p['model_name'],
                        }
                        break

        # Correlation analysis
        if len(payloads_with_event) >= 2:
            prev_event = payloads_with_event[0]['event_type']
            trig_event = payloads_with_event[-1]['event_type']
            correlation_counts[(prev_event, trig_event)] += 1
        elif len(payloads_with_event) == 1:
            single_trigger_counts[payloads_with_event[0]['event_type']] += 1
        else:
            no_packet_count += 1

        if bd['timestamp']:
            try:
                hour = bd['timestamp'].split(' ')[1].split(':')[0]
                hourly[hour] += 1
            except IndexError:
                pass

    top_serials = sorted(serial_counts.items(), key=lambda x: -x[1])
    event_dist = sorted(event_type_counts.items(), key=lambda x: -x[1])

    # Build correlation flow data
    correlation_flows = sorted(
        [{'from': f, 'to': t, 'count': c}
         for (f, t), c in correlation_counts.items()],
        key=lambda x: -x['count']
    )
    single_triggers = sorted(
        [{'event': ev, 'count': c} for ev, c in single_trigger_counts.items()],
        key=lambda x: -x['count']
    )

    # Aggregate trigger distribution (from flows + single triggers)
    trigger_totals = defaultdict(int)
    for (_, t), c in correlation_counts.items():
        trigger_totals[t] += c
    for ev, c in single_trigger_counts.items():
        trigger_totals[ev] += c
    total_with_trigger = sum(trigger_totals.values())
    trigger_dist = sorted(
        [{'event': ev, 'count': c,
          'pct': round(c / total_with_trigger * 100, 1) if total_with_trigger else 0}
         for ev, c in trigger_totals.items()],
        key=lambda x: -x['count']
    )

    return {
        'total_errors': total_errors,
        'unique_serials': len(serial_counts),
        'top_serials': [
            {'serial': s, 'count': c,
             'pct': round(c / total_errors * 100, 1) if total_errors else 0,
             **serial_model.get(s, {})}
            for s, c in top_serials
        ],
        'hourly': {f'{h:02d}': hourly.get(f'{h:02d}', 0) for h in range(24)},
        'event_distribution': [
            {'event': ev, 'count': cnt,
             'pct': round(cnt / total_errors * 100, 1) if total_errors else 0}
            for ev, cnt in event_dist
        ],
        'correlation': {
            'flows': correlation_flows,
            'single_triggers': single_triggers,
            'trigger_distribution': trigger_dist,
            'no_packet_blocks': no_packet_count,
            'total_correlated': sum(c['count'] for c in correlation_flows),
            'total_single': sum(c['count'] for c in single_triggers),
            'total_with_trigger': total_with_trigger,
        },
    }


def generate_html(analysis: dict, input_name: str, total_blocks: int,
                   kept_blocks: int) -> str:
    """Generate HTML report with the same look & feel as error_trend.html."""
    data_json = json.dumps(analysis, ensure_ascii=False)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_str = input_name  # e.g. log_errori_progess_2026_03_30

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <title>Process Errors — {date_str}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        display: ['Outfit', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    }},
                    colors: {{
                        surface: {{ 900: '#0a0a0f', 800: '#12121a', 700: '#1a1a26', 600: '#222233' }},
                        accent: {{
                            indigo: '#6366f1', cyan: '#22d3ee', amber: '#f59e0b',
                            rose: '#f43f5e', emerald: '#10b981', violet: '#8b5cf6',
                            sky: '#0ea5e9', orange: '#f97316', pink: '#ec4899',
                            lime: '#84cc16', teal: '#14b8a6', fuchsia: '#d946ef',
                        }},
                        grid: '#ffffff08',
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ background: #0a0a0f; font-family: 'Outfit', sans-serif; }}
        body::before {{
            content: '';
            position: fixed; inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none; z-index: 0;
        }}
        .card {{
            background: linear-gradient(135deg, #12121a 0%, #1a1a26 100%);
            border: 1px solid rgba(99, 102, 241, 0.08);
            position: relative; overflow: hidden;
        }}
        .card::before {{
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent);
        }}
        .card:hover {{ border-color: rgba(99, 102, 241, 0.15); box-shadow: 0 0 40px rgba(99, 102, 241, 0.05); }}
        .stat-pulse {{ animation: pulse-glow 3s ease-in-out infinite; }}
        @keyframes pulse-glow {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} }}
        @keyframes fade-up {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .animate-in {{ animation: fade-up 0.6s ease-out forwards; opacity: 0; }}
        .delay-1 {{ animation-delay: 0.1s; }}
        .delay-2 {{ animation-delay: 0.2s; }}
        .delay-3 {{ animation-delay: 0.3s; }}
        .delay-4 {{ animation-delay: 0.4s; }}
        .delay-5 {{ animation-delay: 0.5s; }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0a0a0f; }}
        ::-webkit-scrollbar-thumb {{ background: #222233; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #6366f1; }}
        .data-table tbody tr {{ transition: all 0.2s ease; }}
        .data-table tbody tr:hover {{ background: rgba(99, 102, 241, 0.05); }}
        .glow-text {{ text-shadow: 0 0 30px rgba(99, 102, 241, 0.3); }}
        .metric-card {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(34, 211, 238, 0.03) 100%);
            border: 1px solid rgba(99, 102, 241, 0.1);
        }}
    </style>
</head>
<body class="min-h-screen text-gray-200 relative">
    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        <!-- Header -->
        <header class="mb-10 animate-in">
            <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
                <div>
                    <div class="flex items-center gap-3 mb-2">
                        <div class="w-2 h-2 rounded-full bg-accent-rose stat-pulse"></div>
                        <span class="font-mono text-xs text-gray-500 uppercase tracking-widest">Process Error Analysis</span>
                    </div>
                    <h1 class="text-4xl sm:text-5xl font-display font-800 tracking-tight text-white glow-text">
                        Process Already In Progress
                    </h1>
                    <p class="text-lg text-gray-500 font-light mt-1">{date_str}</p>
                </div>
                <div class="text-right">
                    <p class="font-mono text-xs text-gray-600">Generated</p>
                    <p class="font-mono text-sm text-accent-cyan">{now_str}</p>
                </div>
            </div>
            <div class="mt-6 h-px bg-gradient-to-r from-accent-rose/30 via-accent-cyan/10 to-transparent"></div>
        </header>

        <!-- Metric cards -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-in delay-1">
            <div class="metric-card rounded-xl p-4">
                <p class="font-mono text-xs text-gray-500 uppercase tracking-wider">Total Blocks</p>
                <p class="text-3xl font-display font-700 text-white mt-1">{total_blocks:,}</p>
            </div>
            <div class="metric-card rounded-xl p-4">
                <p class="font-mono text-xs text-gray-500 uppercase tracking-wider">Kept Blocks</p>
                <p class="text-3xl font-display font-700 text-accent-rose mt-1">{kept_blocks:,}</p>
            </div>
            <div class="metric-card rounded-xl p-4">
                <p class="font-mono text-xs text-gray-500 uppercase tracking-wider">Total Errors</p>
                <p class="text-3xl font-display font-700 text-accent-amber mt-1">{analysis['total_errors']:,}</p>
            </div>
            <div class="metric-card rounded-xl p-4">
                <p class="font-mono text-xs text-gray-500 uppercase tracking-wider">Unique Serials</p>
                <p class="text-3xl font-display font-700 text-accent-cyan mt-1">{analysis['unique_serials']:,}</p>
            </div>
        </div>

        <!-- Charts row -->
        <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <!-- Top serials bar chart -->
            <div class="card rounded-2xl p-6 animate-in delay-2">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h2 class="text-lg font-display font-600 text-white">Top Serials</h2>
                        <p class="text-sm text-gray-500 font-mono">Machines with most errors</p>
                    </div>
                    <div class="w-3 h-3 rounded-full bg-accent-indigo/50"></div>
                </div>
                <div class="relative" style="height: 320px;">
                    <canvas id="chart-serials"></canvas>
                </div>
            </div>

            <!-- Hourly distribution -->
            <div class="card rounded-2xl p-6 animate-in delay-3">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h2 class="text-lg font-display font-600 text-white">Hourly Distribution</h2>
                        <p class="text-sm text-gray-500 font-mono">Error pattern by hour</p>
                    </div>
                    <div class="w-3 h-3 rounded-full bg-accent-cyan/50"></div>
                </div>
                <div class="relative" style="height: 320px;">
                    <canvas id="chart-hourly"></canvas>
                </div>
            </div>
        </div>

        <!-- Event distribution: chart + table -->
        <div class="grid lg:grid-cols-2 gap-6 mb-6">
            <!-- Doughnut chart -->
            <div class="card rounded-2xl p-6 animate-in delay-4">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h2 class="text-lg font-display font-600 text-white">Trigger Event Distribution</h2>
                        <p class="text-sm text-gray-500 font-mono">What event caused the "Process already in progress"</p>
                    </div>
                    <div class="w-3 h-3 rounded-full bg-accent-violet/50"></div>
                </div>
                <div class="relative" style="height: 320px;">
                    <canvas id="chart-events"></canvas>
                </div>
            </div>

            <!-- Event table -->
            <div class="card rounded-2xl p-6 animate-in delay-4">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h2 class="text-lg font-display font-600 text-white">Event Type Breakdown</h2>
                        <p class="text-sm text-gray-500 font-mono">Decoded from payload body (bytes 33-34)</p>
                    </div>
                    <div class="w-3 h-3 rounded-full bg-accent-emerald/50"></div>
                </div>
                <div class="overflow-x-auto">
                    <table class="data-table w-full text-sm">
                        <thead>
                            <tr class="border-b border-white/5">
                                <th class="text-right py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-10">#</th>
                                <th class="text-left py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Event Type</th>
                                <th class="text-right py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-20">Count</th>
                                <th class="text-right py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-16">%</th>
                            </tr>
                        </thead>
                        <tbody id="event-tbody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Event Correlation -->
        <div class="card rounded-2xl p-6 animate-in delay-5">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-lg font-display font-600 text-white">Trigger Events</h2>
                    <p class="text-sm text-gray-500 font-mono">Which events trigger &ldquo;Process already in progress&rdquo;</p>
                </div>
                <div class="w-3 h-3 rounded-full bg-accent-orange/50"></div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Trigger bar chart -->
                <div><canvas id="triggerChart" height="200"></canvas></div>
                <!-- Trigger table -->
                <div class="overflow-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-white/10">
                                <th class="text-left py-2 px-3 font-mono text-xs text-gray-500 uppercase">Trigger Event</th>
                                <th class="text-right py-2 px-3 font-mono text-xs text-gray-500 uppercase w-16">Count</th>
                                <th class="text-right py-2 px-3 font-mono text-xs text-gray-500 uppercase w-16">%</th>
                            </tr>
                        </thead>
                        <tbody id="trigger-tbody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Correlation Flows -->
        <div class="card rounded-2xl p-6 mt-6 animate-in delay-5">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-lg font-display font-600 text-white">Event Correlation</h2>
                    <p class="text-sm text-gray-500 font-mono">Previous event &#8594; Trigger event (blocks with 2+ packets)</p>
                </div>
                <div class="w-3 h-3 rounded-full bg-accent-rose/50"></div>
            </div>
            <div id="correlation-container"></div>
        </div>

        <!-- Serial list -->
        <div class="card rounded-2xl p-6 mt-6 animate-in delay-5">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <h2 class="text-lg font-display font-600 text-white">Serial List</h2>
                    <p class="text-sm text-gray-500 font-mono">All affected machines sorted by error count</p>
                </div>
                <div class="w-3 h-3 rounded-full bg-accent-amber/50"></div>
            </div>
            <div class="overflow-x-auto">
                <table class="data-table w-full text-sm">
                    <thead>
                        <tr class="border-b border-white/5">
                            <th class="text-right py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-10">#</th>
                            <th class="text-left py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Serial</th>
                            <th class="text-left py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-28">Model</th>
                            <th class="text-right py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-20">Count</th>
                            <th class="text-right py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider w-16">%</th>
                            <th class="text-left py-3 px-4 font-mono text-xs text-gray-500 uppercase tracking-wider">Bar</th>
                        </tr>
                    </thead>
                    <tbody id="serial-tbody"></tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="mt-10 text-center">
            <p class="font-mono text-xs text-gray-600">
                Generated by <span class="text-gray-500">log-cleaner-process</span> skill
            </p>
        </footer>
    </div>

    <script>
        const DATA = {data_json};

        const PALETTE = [
            '#6366f1', '#22d3ee', '#f59e0b', '#f43f5e', '#10b981',
            '#8b5cf6', '#0ea5e9', '#f97316', '#ec4899', '#84cc16',
            '#14b8a6', '#d946ef', '#a78bfa', '#fb923c', '#34d399',
            '#e879f9', '#38bdf8', '#fbbf24', '#fb7185', '#4ade80'
        ];

        Chart.defaults.color = '#6b7280';
        Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
        Chart.defaults.font.family = "'JetBrains Mono', monospace";
        Chart.defaults.font.size = 11;

        const tooltipStyle = {{
            backgroundColor: 'rgba(18, 18, 26, 0.95)',
            borderColor: 'rgba(99, 102, 241, 0.2)',
            borderWidth: 1,
            titleFont: {{ family: "'JetBrains Mono', monospace", size: 12 }},
            bodyFont: {{ family: "'JetBrains Mono', monospace", size: 11 }},
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
            boxPadding: 4,
        }};

        const MQTT_TYPE_COLORS = {{
            'CONFIG':   {{ bg: 'rgba(99,102,241,0.15)',  border: '#6366f1', text: '#a5b4fc' }},
            'VENDING':  {{ bg: 'rgba(34,211,238,0.12)',  border: '#22d3ee', text: '#67e8f9' }},
            'DOSEINFO': {{ bg: 'rgba(245,158,11,0.12)',  border: '#f59e0b', text: '#fcd34d' }},
            'COMMAND':  {{ bg: 'rgba(16,185,129,0.12)',  border: '#10b981', text: '#6ee7b7' }},
            'ALARM':    {{ bg: 'rgba(244,63,94,0.12)',   border: '#f43f5e', text: '#fda4af' }},
        }};

        function mqttBadge(type) {{
            const c = MQTT_TYPE_COLORS[type] || {{ bg: 'rgba(255,255,255,0.06)', border: '#4b5563', text: '#9ca3af' }};
            return `<span style="background:${{c.bg}};border:1px solid ${{c.border}};color:${{c.text}}" class="inline-block font-mono text-xs px-2 py-0.5 rounded">${{type}}</span>`;
        }}

        function copyPayload(hex, btn) {{
            navigator.clipboard.writeText(hex).then(() => {{
                const orig = btn.textContent;
                btn.textContent = 'copied!';
                btn.style.color = '#10b981';
                setTimeout(() => {{ btn.textContent = orig; btn.style.color = ''; }}, 1500);
            }});
        }}

        // Top serials chart (horizontal bar, top 20)
        (function() {{
            const top = DATA.top_serials.slice(0, 20);
            const ctx = document.getElementById('chart-serials').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: top.map(s => s.serial),
                    datasets: [{{
                        label: 'Errors',
                        data: top.map(s => s.count),
                        backgroundColor: top.map((_, i) => PALETTE[i % PALETTE.length] + 'bb'),
                        borderColor: top.map((_, i) => PALETTE[i % PALETTE.length]),
                        borderWidth: 1,
                        borderRadius: 4,
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            ...tooltipStyle,
                            callbacks: {{
                                label: item => `  ${{item.raw}} errors`
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ beginAtZero: true, grid: {{ color: 'rgba(255,255,255,0.03)' }} }},
                        y: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 10 }} }} }}
                    }}
                }}
            }});
        }})();

        // Hourly chart
        (function() {{
            const hours = Object.keys(DATA.hourly).sort();
            const ctx = document.getElementById('chart-hourly').getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: hours.map(h => h + ':00'),
                    datasets: [{{
                        label: 'Errors',
                        data: hours.map(h => DATA.hourly[h]),
                        backgroundColor: 'rgba(34, 211, 238, 0.5)',
                        borderColor: '#22d3ee',
                        borderWidth: 1,
                        borderRadius: 6,
                        borderSkipped: false,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            ...tooltipStyle,
                            callbacks: {{
                                title: items => items[0].label,
                                label: item => `  ${{item.raw}} errors`
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 12, font: {{ size: 10 }} }} }},
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(255,255,255,0.03)' }} }}
                    }}
                }}
            }});
        }})();

        // Event distribution doughnut chart
        (function() {{
            const evts = DATA.event_distribution;
            if (!evts || evts.length === 0) return;
            const ctx = document.getElementById('chart-events').getContext('2d');
            new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: evts.map(e => e.event),
                    datasets: [{{
                        data: evts.map(e => e.count),
                        backgroundColor: evts.map((_, i) => PALETTE[i % PALETTE.length] + 'cc'),
                        borderColor: evts.map((_, i) => PALETTE[i % PALETTE.length]),
                        borderWidth: 2,
                        hoverOffset: 8,
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '55%',
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                boxWidth: 12, boxHeight: 12, padding: 12,
                                font: {{ size: 11, family: "'JetBrains Mono', monospace" }},
                                usePointStyle: true, pointStyle: 'rectRounded',
                            }}
                        }},
                        tooltip: {{
                            ...tooltipStyle,
                            callbacks: {{
                                label: item => '  ' + item.label + ': ' + item.raw + ' (' + evts[item.dataIndex].pct + '%)'
                            }}
                        }}
                    }}
                }}
            }});
        }})();

        // Event type table
        (function() {{
            const tbody = document.getElementById('event-tbody');
            const evtColors = {{}};
            DATA.event_distribution.forEach((e, i) => {{ evtColors[e.event] = PALETTE[i % PALETTE.length]; }});
            DATA.event_distribution.forEach((e, idx) => {{
                const color = evtColors[e.event];
                const tr = document.createElement('tr');
                tr.className = 'border-b border-white/5';
                tr.innerHTML = ''
                    + '<td class="py-3 px-4 font-mono text-right text-gray-600">' + (idx + 1) + '</td>'
                    + '<td class="py-3 px-4"><span class="inline-flex items-center gap-2">'
                    + '<span class="w-2.5 h-2.5 rounded-full inline-block" style="background:' + color + '"></span>'
                    + '<span class="font-mono text-sm text-white">' + e.event + '</span></span></td>'
                    + '<td class="py-3 px-4 font-mono text-right text-white font-600">' + e.count + '</td>'
                    + '<td class="py-3 px-4 font-mono text-right text-accent-amber">' + e.pct + '%</td>';
                tbody.appendChild(tr);
            }});
        }})();

        // Trigger Events bar chart + table
        (function() {{
            const corr = DATA.correlation;
            if (!corr || !corr.trigger_distribution) return;
            const td = corr.trigger_distribution;

            // Horizontal bar chart
            new Chart(document.getElementById('triggerChart'), {{
                type: 'bar',
                data: {{
                    labels: td.map(d => d.event),
                    datasets: [{{
                        data: td.map(d => d.count),
                        backgroundColor: td.map((_, i) => PALETTE[i % PALETTE.length] + 'cc'),
                        borderColor: td.map((_, i) => PALETTE[i % PALETTE.length]),
                        borderWidth: 1,
                        borderRadius: 6,
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{ return ctx.raw + ' blocks (' + td[ctx.dataIndex].pct + '%)'; }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#9ca3af', font: {{ family: 'JetBrains Mono' }} }} }},
                        y: {{ grid: {{ display: false }}, ticks: {{ color: '#e5e7eb', font: {{ family: 'JetBrains Mono', size: 11 }} }} }}
                    }}
                }}
            }});

            // Trigger table
            const tbody = document.getElementById('trigger-tbody');
            td.forEach(function(t, i) {{
                const tr = document.createElement('tr');
                tr.className = 'border-b border-white/5';
                const color = PALETTE[i % PALETTE.length];
                tr.innerHTML = ''
                    + '<td class="py-2 px-3 flex items-center gap-2">'
                    + '<span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background:' + color + '"></span>'
                    + '<span class="font-mono text-sm text-gray-200">' + t.event + '</span></td>'
                    + '<td class="py-2 px-3 text-right font-mono text-sm text-white font-600">' + t.count + '</td>'
                    + '<td class="py-2 px-3 text-right font-mono text-sm text-accent-amber">' + t.pct + '%</td>';
                tbody.appendChild(tr);
            }});
        }})();

        // Event Correlation flow table
        (function() {{
            const corr = DATA.correlation;
            if (!corr) return;
            const container = document.getElementById('correlation-container');
            const evtColors = {{}};
            DATA.event_distribution.forEach((e, i) => {{ evtColors[e.event] = PALETTE[i % PALETTE.length]; }});

            let html = '';

            if (corr.flows && corr.flows.length > 0) {{
                html += '<p class="font-mono text-xs text-gray-500 mb-4">'
                    + corr.total_correlated + ' blocks with 2+ packets &mdash; shows what was running when the trigger arrived</p>';
                html += '<table class="w-full text-sm mb-6"><thead><tr class="border-b border-white/10">'
                    + '<th class="text-left py-2 px-3 font-mono text-xs text-gray-500 uppercase">Previous (running)</th>'
                    + '<th class="text-center py-2 px-3 font-mono text-xs text-gray-500"></th>'
                    + '<th class="text-left py-2 px-3 font-mono text-xs text-gray-500 uppercase">Trigger (arrived)</th>'
                    + '<th class="text-right py-2 px-3 font-mono text-xs text-gray-500 uppercase w-16">Count</th>'
                    + '<th class="py-2 px-3 w-32"></th>'
                    + '</tr></thead><tbody>';
                const maxFlow = corr.flows[0].count;
                corr.flows.forEach(function(f) {{
                    const fromColor = evtColors[f.from] || '#6b7280';
                    const toColor = evtColors[f.to] || '#6b7280';
                    const barPct = Math.max(8, (f.count / maxFlow * 100));
                    html += '<tr class="border-b border-white/5">'
                        + '<td class="py-2.5 px-3 flex items-center gap-2">'
                        + '<span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background:' + fromColor + '"></span>'
                        + '<span class="font-mono text-sm text-gray-200">' + f.from + '</span></td>'
                        + '<td class="py-2.5 px-3 text-center text-gray-500 text-lg">&rarr;</td>'
                        + '<td class="py-2.5 px-3 flex items-center gap-2">'
                        + '<span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background:' + toColor + '"></span>'
                        + '<span class="font-mono text-sm text-gray-200">' + f.to + '</span></td>'
                        + '<td class="py-2.5 px-3 text-right font-mono text-sm text-white font-700">' + f.count + '</td>'
                        + '<td class="py-2.5 px-3"><div class="w-full bg-surface-700 rounded-full h-2">'
                        + '<div class="h-2 rounded-full" style="width:' + barPct + '%;background:linear-gradient(90deg,' + fromColor + '88,' + toColor + '88)"></div>'
                        + '</div></td></tr>';
                }});
                html += '</tbody></table>';
            }}

            // Summary note
            let notes = [];
            if (corr.total_single > 0) {{
                notes.push(corr.total_single + ' blocks had only 1 packet (trigger visible, previous out of grep window)');
            }}
            if (corr.no_packet_blocks > 0) {{
                notes.push(corr.no_packet_blocks + ' blocks had no decodable packets');
            }}
            if (notes.length > 0) {{
                html += '<div class="space-y-1">';
                notes.forEach(function(n) {{ html += '<p class="font-mono text-xs text-gray-600">' + n + '</p>'; }});
                html += '<p class="font-mono text-xs text-gray-500 mt-2">Tip: re-extract with <code class="bg-surface-700 px-1.5 py-0.5 rounded text-accent-cyan">grep -B10</code> or higher to capture more previous events</p>';
                html += '</div>';
            }}

            container.innerHTML = html;
        }})();

        // Serial list table
        (function() {{
            const dash = '<span class="text-gray-600">\u2014</span>';
            const tbody = document.getElementById('serial-tbody');
            const maxCount = DATA.top_serials.length > 0 ? DATA.top_serials[0].count : 1;
            DATA.top_serials.forEach((s, idx) => {{
                const model = s.model_code
                    ? '<span class="text-white font-600">' + s.model_code + '</span> <span class="text-gray-500 text-xs">' + (s.model_name || '') + '</span>'
                    : dash;
                const barPct = (s.count / maxCount * 100).toFixed(0);
                const barHtml = '<div class="w-full bg-surface-700 rounded-full h-2 relative">'
                    + '<div class="h-2 rounded-full bg-accent-indigo/60" style="width:' + barPct + '%"></div>'
                    + '</div>';
                const tr = document.createElement('tr');
                tr.className = 'border-b border-white/5';
                tr.innerHTML = ''
                    + '<td class="py-2 px-4 font-mono text-right text-gray-600 text-xs">' + (idx + 1) + '</td>'
                    + '<td class="py-2 px-4 font-mono text-accent-cyan text-sm">' + s.serial + '</td>'
                    + '<td class="py-2 px-4">' + model + '</td>'
                    + '<td class="py-2 px-4 font-mono text-right text-white font-600">' + s.count + '</td>'
                    + '<td class="py-2 px-4 font-mono text-right text-accent-amber text-xs">' + s.pct + '%</td>'
                    + '<td class="py-2 px-4 w-40">' + barHtml + '</td>';
                tbody.appendChild(tr);
            }});
        }})();
    </script>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_process_errors.py <input_log_file>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    raw_text = input_path.read_text(encoding='utf-8', errors='replace')
    raw_lines = [l.rstrip('\r') for l in raw_text.splitlines()]

    if not any(l.strip() == '--' for l in raw_lines):
        print("WARNING: File does not contain '--' block separators.")
        print("This script expects block-format logs (grep -B output).")
        sys.exit(1)

    blocks = split_blocks(raw_lines)
    total_blocks = len(blocks)

    kept_lines: list[str] = []
    kept_blocks_data: list[dict] = []
    kept_count = 0
    all_serials: set[str] = set()

    for block in blocks:
        serials = extract_process_serials(block)
        if not serials:
            continue
        kept_count += 1
        all_serials.update(serials)
        filtered = filter_block_lines(block, serials)
        kept_lines.extend(filtered)
        kept_blocks_data.append(extract_block_data(filtered, serials))

    # Write cleaned log
    out_name = input_path.stem + '_clean.txt'
    out_path = Path.cwd() / out_name
    out_path.write_text('\n'.join(kept_lines) + '\n', encoding='utf-8')

    # Build analysis and write HTML report
    analysis = build_analysis(kept_blocks_data)
    html = generate_html(analysis, input_path.stem, total_blocks, kept_count)
    html_path = Path.cwd() / (input_path.stem + '_report.html')
    html_path.write_text(html, encoding='utf-8')

    print(f"Total blocks:    {total_blocks}")
    print(f"Kept blocks:     {kept_count}")
    print(f"Removed blocks:  {total_blocks - kept_count}")
    print(f"Unique serials:  {len(all_serials)}")
    print(f"Output clean:    {out_path}")
    print(f"Output report:   {html_path}")


if __name__ == '__main__':
    main()

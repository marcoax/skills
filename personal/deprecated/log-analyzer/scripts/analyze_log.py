#!/usr/bin/env python3
"""
Symfony app.ERROR log analyzer.
Usage:
  python analyze_log.py <input_log_file>
  python analyze_log.py --regenerate-html [path/to/error_history.json]

Steps (full analysis):
  1. Clean the log (blocks filtered per CLEAN_RULES) → <basename>_clean.txt
  2. Extract errors from cleaned log
  3. Archive existing log_report_*.md to report/
  4. Generate markdown report with error stats    → log_report_<date>.md
  5. Update error_history.json and generate error_trend.html
  6. Check for new error types against known_errors.txt
  7. Move original input file to backup/

The --regenerate-html flag skips all analysis steps and regenerates
error_trend.html from an existing error_history.json file.
"""

import datetime
import json
import re
import sys
import shutil
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Normalisation patterns: replace variable parts with {PLACEHOLDER}
# ---------------------------------------------------------------------------
NORMALISE_PATTERNS = [
    # serial numbers (standalone integers 5-7 digits)
    (re.compile(r'\bfor serial \d+'), 'for serial {N}'),
    # byte counts in Get Machine Configuration
    (re.compile(r'\binstead of \d+'), 'instead of {N}'),
    # Troppi errori: count
    (re.compile(r'Troppi errori di processo: \d+'), 'Troppi errori di processo: {N}'),
    # UUIDs
    (re.compile(r"'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'",
                re.IGNORECASE), "'{UUID}'"),
    # Machine N synchronized fix
    (re.compile(r'Machine \d+ synchronized fix'), 'Machine {N} synchronized fix'),
    # Unable to save snapshot — normalise embedded UUID
    (re.compile(r"Unable to save the snapshot for aggregate with id [0-9a-f-]+"),
     "Unable to save the snapshot for aggregate with id {UUID}"),
    # Aggregate with id ...
    (re.compile(r"Aggregate with id '[^']+'"), "Aggregate with id '{UUID}'"),
    # Invalid date format — trailing values
    (re.compile(r'(Invalid date format)\s+.*'), r'\1 {values}'),
    # Expected response code 250 … 451 message (keep template but strip dynamic parts)
    # already stable in sample — keep as-is
    # MySQL "server has gone away" — normalise serial number in params array
    (re.compile(r'with params \["\d+"\]'), 'with params ["{N}"]'),
]

# ---------------------------------------------------------------------------
# CLEAN_RULES filtering helpers
# Source of truth: assets/CLEAN_RULES.md — keep in sync when adding new rules
# ---------------------------------------------------------------------------

def extract_serial_from_error(error_line: str) -> str | None:
    """Extract the numeric serial mentioned in the ERROR line."""
    m = re.search(r'\b(\d{5,7})\b', error_line)
    return m.group(1) if m else None


def is_connected_machines_line(line: str) -> bool:
    return 'Connected machines achieved from broker' in line


def is_machine_synchronized_line(line: str) -> bool:
    return bool(re.search(r'Machine \d+ synchronized', line))


def is_troppi_errori_line(line: str) -> bool:
    """Rule 4 (line-level): single line is a 'Troppi errori di processo' error."""
    return 'app.ERROR' in line and 'Troppi errori di processo' in line


def is_troppi_errori_block(block_lines: list[str]) -> bool:
    """Rule 4: remove entire block if error is 'Troppi errori di processo'."""
    return any(is_troppi_errori_line(line) for line in block_lines)


def is_aggregate_null_uuid_block(block_lines: list[str]) -> bool:
    """Rule 5: block contains 'Aggregate with id '00000000-...' not found'."""
    for line in block_lines:
        if 'app.ERROR' in line and "Aggregate with id '00000000-" in line:
            return True
    return False


def clean_block(block_lines: list[str]) -> list[str] | None:
    """
    Apply CLEAN_RULES to a single block.
    Returns None if the block should be dropped entirely.
    Returns filtered lines (including '--') otherwise.
    """
    # Rule 4: drop entire block for 'Troppi errori di processo'
    if is_troppi_errori_block(block_lines):
        return None

    # Find the ERROR line and extract its serial
    error_line = next((l for l in block_lines if 'app.ERROR' in l), None)
    if error_line is None:
        return None  # no ERROR line → skip

    # Rule 5: aggregate null UUID — keep only the line before the error + error + '--'
    if is_aggregate_null_uuid_block(block_lines):
        content_lines = [l for l in block_lines if l.strip() != '--']
        error_idx = next(i for i, l in enumerate(content_lines) if 'app.ERROR' in l)
        kept = []
        if error_idx > 0:
            kept.append(content_lines[error_idx - 1])
        kept.append(content_lines[error_idx])
        kept.append('--')
        return kept

    serial = extract_serial_from_error(error_line)

    kept = []
    for line in block_lines:
        if line.strip() == '--':
            kept.append(line)
            continue
        # Rule 2: remove "Machine N synchronized"
        if is_machine_synchronized_line(line):
            continue
        # Rule 3: remove "Connected machines achieved from broker"
        if is_connected_machines_line(line):
            continue
        # Rule 1: keep only lines that contain the serial (or the ERROR line itself)
        if serial and 'app.INFO' in line:
            if serial not in line:
                continue
        kept.append(line)

    return kept


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


# ---------------------------------------------------------------------------
# Error normalisation
# ---------------------------------------------------------------------------

_PACKET_RECEIVED_RE = re.compile(
    r'Packet received \[([^\]]+)\]:\s*((?:[\da-fA-F]{2}\s*)+)'
)
_ERROR_MSG_RE = re.compile(r'\] app\.ERROR: (.+)')


def normalise_error(msg: str) -> str:
    msg = msg.strip()
    # strip trailing [] []
    msg = re.sub(r'\s*\[\]\s*\[\]\s*$', '', msg)
    for pattern, replacement in NORMALISE_PATTERNS:
        msg = pattern.sub(replacement, msg)
    return msg


def extract_errors_from_lines(lines: list[str]) -> list[tuple[str, str, str]]:
    """
    Returns list of (datetime_str, hour_str, normalised_error).
    Parses lines directly (works on both raw and cleaned logs).
    """
    results = []
    pattern = re.compile(
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] app\.ERROR: (.+)')
    for line in lines:
        m = pattern.search(line)
        if m:
            dt_str = m.group(1)
            msg = m.group(2)
            hour = dt_str[11:13]
            norm = normalise_error(msg)
            results.append((dt_str, hour, norm))
    return results


def extract_example_payloads(cleaned_lines: list[str]) -> dict[str, dict]:
    """
    Scan cleaned-log blocks and collect one example 'Packet received' payload
    per normalised error type.
    Returns {norm_error: {'topic': str, 'hex': str, 'type': str}}.
    Only works on block-format logs (with '--' separators).
    """
    if not any(l.strip() == '--' for l in cleaned_lines):
        return {}

    result: dict[str, dict] = {}
    for block in split_blocks(cleaned_lines):
        error_line = next((l for l in block if 'app.ERROR' in l), None)
        if not error_line:
            continue
        m = _ERROR_MSG_RE.search(error_line)
        if not m:
            continue
        norm = normalise_error(m.group(1))
        if norm in result:
            continue  # already have an example for this type

        for line in block:
            pm = _PACKET_RECEIVED_RE.search(line)
            if pm:
                topic = pm.group(1)
                hex_bytes = pm.group(2).strip()
                parts = topic.split('/')
                msg_type = parts[1] if len(parts) >= 2 else topic
                result[norm] = {'topic': topic, 'hex': hex_bytes, 'type': msg_type}
                break
    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def extract_date_from_filename(path: Path) -> str | None:
    """Extract YYYY-MM-DD date from filename like log_errori_2026_03_20.txt."""
    m = re.search(r'(\d{4})[-_](\d{2})[-_](\d{2})', path.stem)
    return f'{m.group(1)}-{m.group(2)}-{m.group(3)}' if m else None


def build_report(input_path: Path, errors: list[tuple[str, str, str]],
                 date_label: str | None = None) -> str:
    total = len(errors)
    if not date_label:
        date_label = errors[0][0][:10] if errors else 'N/A'

    # --- hourly distribution ---
    hourly: dict[str, int] = defaultdict(int)
    for _, hour, _ in errors:
        hourly[hour] += 1

    # --- error type counts ---
    type_counts: dict[str, int] = defaultdict(int)
    for _, _, norm in errors:
        type_counts[norm] += 1

    lines = [
        f'# Analisi Log Errori — {date_label}',
        '',
        f'**File:** `{input_path.name}`',
        f'**Data:** {date_label}',
        f'**Totale errori:** {total}',
        '',
        '## FONTE',
        f'- Analisi basata su `{input_path.name}`',
        '',
        '---',
        '',
        '## Distribuzione oraria',
        '',
        '| Ora | Errori | % |',
        '|-----|-------:|--:|',
    ]
    for h in sorted(hourly):
        pct = hourly[h] / total * 100
        lines.append(f'| {h}:00 | {hourly[h]} | {pct:.1f}% |')
    lines.append(f'| **Totale** | **{total}** | **100%** |')
    lines.append('')

    # peak hours note
    if hourly:
        top2 = sorted(hourly, key=lambda x: -hourly[x])[:2]
        top2_count = sum(hourly[h] for h in top2)
        top2_pct = top2_count / total * 100
        top2_label = ' e '.join(f'**{h}:xx**' for h in sorted(top2))
        lines.append(
            f'> Il picco si concentra nelle fasce {top2_label} '
            f'({top2_count} errori, {top2_pct:.1f}% del totale).'
        )
        lines.append('')

    lines += [
        '---',
        '',
        '## Occorrenze per tipo di errore',
        '',
        '| # | Errore | Count | % | FIXED |',
        '|---|--------|------:|--:|-------|',
    ]
    sorted_types = sorted(type_counts.items(), key=lambda x: -x[1])
    for i, (err, count) in enumerate(sorted_types, 1):
        pct = count / total * 100
        lines.append(f'| {i} | `{err}` | {count} | {pct:.1f}% |  |')

    lines.append('')
    # top-3 summary
    if len(sorted_types) >= 3:
        top3_count = sum(c for _, c in sorted_types[:3])
        top3_pct = top3_count / total * 100
        names = ', '.join(f'`{e}`' for e, _ in sorted_types[:3])
        lines.append(
            f'> I 3 errori più frequenti ({names}) rappresentano '
            f'il {top3_pct:.1f}% del totale ({top3_count}/{total} errori).'
        )

    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# New error type detection
# ---------------------------------------------------------------------------

def load_known_errors(path: Path) -> set[str]:
    """Load known normalised error messages from a text file (one per line)."""
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.startswith('#')}


def check_new_errors(errors: list[tuple[str, str, str]], known_path: Path) -> list[str]:
    """
    Compare normalised errors found in the log against the known_errors list.
    Returns a sorted list of new error types not present in known_errors.txt.
    """
    known = load_known_errors(known_path)
    found = {norm for _, _, norm in errors}
    new = sorted(found - known)
    return new


# ---------------------------------------------------------------------------
# Error history (for error_trend.html)
# ---------------------------------------------------------------------------

def update_error_history(history_path: Path, errors: list[tuple[str, str, str]],
                         date_label: str | None = None,
                         payloads: dict | None = None) -> dict | None:
    """
    Append or update today's entry in error_history.json.
    Each entry: { date, total, errors: {norm: count}, hourly: {HH: count},
                  example_payloads: {norm: {topic, hex, type}} (optional) }.
    If an entry for the same date already exists, it is replaced.
    Returns the full history dict, or None if errors is empty.
    """
    if not errors:
        return None

    if not date_label:
        date_label = errors[0][0][:10]

    type_counts: dict[str, int] = defaultdict(int)
    hourly: dict[str, int] = defaultdict(int)
    for _, hour, norm in errors:
        type_counts[norm] += 1
        hourly[hour] += 1

    day_entry = {
        'date': date_label,
        'total': len(errors),
        'errors': dict(type_counts),
        'hourly': dict(hourly),
    }
    if payloads:
        day_entry['example_payloads'] = payloads

    # Load existing history
    if history_path.exists():
        data = json.loads(history_path.read_text(encoding='utf-8'))
    else:
        data = {'days': []}

    # Replace or append
    data['days'] = [d for d in data['days'] if d['date'] != date_label]
    data['days'].append(day_entry)
    data['days'].sort(key=lambda d: d['date'])

    history_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n',
                            encoding='utf-8')
    return data


def generate_trend_html(output_dir: Path, history_data: dict) -> Path:
    """
    Read the HTML template from assets/ and inject history_data as inline JSON,
    replacing the /*__ERROR_DATA__*/ placeholder. Writes error_trend.html.
    """
    template_path = Path(__file__).resolve().parent.parent / 'assets' / 'error_trend_template.html'
    template = template_path.read_text(encoding='utf-8')

    placeholder = '/*__ERROR_DATA__*/null'
    json_blob = json.dumps(history_data, ensure_ascii=False)
    html = template.replace(placeholder, json_blob)

    if placeholder.split('null')[0] in html:
        raise RuntimeError('Placeholder replacement failed in error_trend_template.html')

    ts_placeholder = '/*__GENERATED_AT__*/null'
    generated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = html.replace(ts_placeholder, json.dumps(generated_at))

    out_path = output_dir / 'error_trend.html'
    out_path.write_text(html, encoding='utf-8')
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --regenerate-html: rebuild error_trend.html from existing error_history.json
    if len(sys.argv) >= 2 and sys.argv[1] == '--regenerate-html':
        history_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path.cwd() / 'error_history.json'
        if not history_path.exists():
            print(f'History file not found: {history_path}')
            sys.exit(1)
        data = json.loads(history_path.read_text(encoding='utf-8'))
        trend_path = generate_trend_html(history_path.parent, data)
        print(f'Trend HTML regenerated: {trend_path}')
        sys.exit(0)

    if len(sys.argv) < 2:
        print('Usage: python analyze_log.py <input_log_file>')
        print('       python analyze_log.py --regenerate-html [path/to/error_history.json]')
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f'File not found: {input_path}')
        sys.exit(1)

    raw_text = input_path.read_text(encoding='utf-8', errors='replace')
    raw_lines = [l.rstrip('\r') for l in raw_text.splitlines()]

    # Extract date from filename (preferred over first error timestamp)
    file_date = extract_date_from_filename(input_path)

    # Project root is always cwd
    project_dir = Path.cwd()
    backup_dir = project_dir / 'backup'

    # Step 1: clean
    has_block_separators = any(l.strip() == '--' for l in raw_lines)
    if has_block_separators:
        blocks = split_blocks(raw_lines)
        cleaned_lines: list[str] = []
        for block in blocks:
            result = clean_block(block)
            if result is not None:
                cleaned_lines.extend(result)
    else:
        # File without block separators (flat error list) — apply line-level filtering
        cleaned_lines = [l for l in raw_lines if not is_troppi_errori_line(l)]

    # Archive previous clean files from root to backup/
    existing_cleans = list(project_dir.glob('log_errori_*_clean.txt'))
    if existing_cleans:
        backup_dir.mkdir(exist_ok=True)
        for cl in existing_cleans:
            dest = backup_dir / cl.name
            shutil.move(str(cl), str(dest))
            print(f'Old clean moved:   {dest}')

    # Write current clean to root
    clean_name = input_path.stem + '_clean.txt'
    clean_path = project_dir / clean_name
    clean_path.write_text('\n'.join(cleaned_lines) + '\n', encoding='utf-8')
    print(f'Clean log written: {clean_path}')

    # Step 2: extract errors (from cleaned log)
    errors = extract_errors_from_lines(cleaned_lines)
    example_payloads = extract_example_payloads(cleaned_lines)
    print(f'Total errors found: {len(errors)}')

    # Step 3: archive existing report files to report/
    report_dir = project_dir / 'report'
    existing_reports = list(project_dir.glob('log_report_*.md'))
    if existing_reports:
        report_dir.mkdir(exist_ok=True)
        for rp in existing_reports:
            dest = report_dir / rp.name
            shutil.move(str(rp), str(dest))
            print(f'Old report moved:  {dest}')

    # Step 4: generate new report
    report_md = build_report(input_path, errors, date_label=file_date)
    date_part = input_path.stem.replace('log_errori_', '').replace('log_errori', '')
    report_path = project_dir / f'log_report_{date_part}.md'
    report_path.write_text(report_md, encoding='utf-8')
    print(f'Report written:    {report_path}')

    # Step 5: update error_history.json and generate error_trend.html
    history_path = project_dir / 'error_history.json'
    history_data = update_error_history(history_path, errors, date_label=file_date,
                                         payloads=example_payloads)
    print(f'History updated:   {history_path}')

    if history_data:
        trend_path = generate_trend_html(project_dir, history_data)
        print(f'Trend HTML:        {trend_path}')

    # Step 6: check for new error types against known_errors.txt
    known_errors_path = Path(__file__).resolve().parent.parent / 'assets' / 'known_errors.txt'
    new_error_types = check_new_errors(errors, known_errors_path)
    if new_error_types:
        print()
        print(f'*** NEW ERROR TYPES DETECTED: {len(new_error_types)} ***')
        for ne in new_error_types:
            print(f'  -> {ne}')
        print()
        print('Consider adding these to assets/known_errors.txt if they are expected.')
    else:
        print('No new error types detected.')

    # Step 7: move original file to backup/ (skip if already there)
    if input_path.parent.name.lower() == 'backup':
        print(f'Original already in backup/, skipping move.')
    else:
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / input_path.name
        shutil.move(str(input_path), str(backup_path))
        print(f'Original moved to: {backup_path}')


if __name__ == '__main__':
    main()

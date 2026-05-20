"""Analisi statistica ricette macchina per tipo prodotto.

Legge machine_recipes.json (array di oggetti con payload.machineId e payload.recipes),
filtra le macchine per lista UUID, estrae i sotto-prodotti con type == --type,
calcola la distribuzione di frequenza degli attributi selezionati e genera
tre file di output (HTML, Markdown, CSV) con stesso prefisso/timestamp.

Solo stdlib.
"""

import argparse
import csv
import html as html_mod
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def load_labels(path: Path) -> dict[str, str]:
    """Parsa un file JSX/JS con oggetto chiave-valore di etichette.
    Supporta sia virgolette singole che doppie: 'key': 'label' o "key": "label".
    """
    text = path.read_text(encoding="utf-8-sig")
    pattern = re.compile(r"""['"]([\w]+)['"]\s*:\s*['"]([^'"]+)['"]""")
    return {m.group(1): m.group(2) for m in pattern.finditer(text)}


def read_uuid_list(path: Path) -> set[str]:
    uuids: set[str] = set()
    with path.open(encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        has_header = False
        try:
            has_header = csv.Sniffer().has_header(sample)
        except csv.Error:
            pass
        reader = csv.reader(f)
        if has_header:
            next(reader, None)
        for row in reader:
            if not row:
                continue
            val = row[0].strip()
            if val:
                uuids.add(val)
    return uuids


def load_recipes(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(
            f"Formato inatteso: attesa lista top-level in {path}, trovato {type(data).__name__}"
        )
    return data


def extract_observations(
    machines: list[dict], allowed_uuids: set[str], target_type: int
) -> tuple[list[dict], int, int]:
    """Ritorna (observations, n_machines_matched, n_recipes_scanned)."""
    observations: list[dict] = []
    machines_matched = 0
    recipes_scanned = 0
    for m in machines:
        payload = m.get("payload") or {}
        machine_id = payload.get("machineId") or m.get("_id")
        if machine_id not in allowed_uuids:
            continue
        machines_matched += 1
        recipes = payload.get("recipes") or {}
        if isinstance(recipes, dict):
            recipe_iter = recipes.values()
        elif isinstance(recipes, list):
            recipe_iter = recipes
        else:
            continue
        for recipe in recipe_iter:
            if not isinstance(recipe, dict):
                continue
            recipes_scanned += 1
            for prod in recipe.get("products") or []:
                if not isinstance(prod, dict):
                    continue
                if prod.get("type") == target_type:
                    observations.append(prod)
    return observations, machines_matched, recipes_scanned


def compute_stats(
    observations: list[dict], attrs: list[str]
) -> dict[str, list[tuple[object, int, float]]]:
    """Per ogni attributo -> lista di (valore, occorrenze, percentuale) ordinata desc."""
    result: dict[str, list[tuple[object, int, float]]] = {}
    for attr in attrs:
        counter: Counter = Counter()
        present = 0
        for obs in observations:
            if attr in obs:
                counter[obs[attr]] += 1
                present += 1
        if present == 0:
            result[attr] = []
            continue
        rows = [
            (val, cnt, cnt * 100.0 / present)
            for val, cnt in counter.most_common()
        ]
        result[attr] = rows
    return result


def render_csv(
    out_path: Path,
    stats: dict[str, list[tuple[object, int, float]]],
    labels: dict[str, str] | None = None,
) -> None:
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["attributo", "etichetta", "valore", "occorrenze", "percentuale"])
        for attr, rows in stats.items():
            label = (labels or {}).get(attr, attr)
            for val, cnt, pct in rows:
                w.writerow([attr, label, val, cnt, f"{pct:.1f}"])


def render_md(
    out_path: Path,
    stats: dict[str, list[tuple[object, int, float]]],
    meta: dict,
    labels: dict[str, str] | None = None,
) -> None:
    lines: list[str] = []
    lines.append(f"# Statistiche ricette — tipo={meta['type']}")
    lines.append("")
    lines.append(f"**Osservazioni totali (sotto-prodotti type={meta['type']}):** {meta['n_observations']}")
    lines.append(f"**Macchine coinvolte:** {meta['n_machines']}")
    lines.append(f"**Ricette scansionate:** {meta['n_recipes']}")
    lines.append(f"**Data analisi:** {meta['timestamp_human']}")
    lines.append(f"**File ricette:** `{meta['recipes_path']}`")
    lines.append(f"**File UUID:** `{meta['uuid_path']}`")
    lines.append("")
    for attr, rows in stats.items():
        label = (labels or {}).get(attr, attr)
        heading = label if label == attr else f"{label} (`{attr}`)"
        lines.append(f"## {heading}")
        if not rows:
            lines.append("_Attributo non presente nelle osservazioni._")
            lines.append("")
            continue
        lines.append(f"{len(rows)} valori distinti")
        lines.append("")
        lines.append("| valore | occorrenze | % |")
        lines.append("|---|---:|---:|")
        for val, cnt, pct in rows:
            lines.append(f"| {val} | {cnt} | {pct:.1f}% |")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


HTML_CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
       margin: 0; padding: 24px; color: #222; background: #fafafa; }
h1 { color: #3a6fb5; margin-top: 0; }
h2 { color: #3a6fb5; border-bottom: 2px solid #e4e8ee; padding-bottom: 4px; margin-top: 32px; }
.meta { background: #fff; border: 1px solid #e4e8ee; border-radius: 6px;
        padding: 12px 16px; margin-bottom: 24px; font-size: 14px; }
.meta div { margin: 2px 0; }
.toc { background: #fff; border: 1px solid #e4e8ee; border-radius: 6px;
       padding: 12px 16px; margin-bottom: 24px; }
.toc ul { margin: 4px 0; padding-left: 20px; }
.toc a { color: #3a6fb5; text-decoration: none; }
.toc a:hover { text-decoration: underline; }
table { border-collapse: collapse; width: 100%; background: #fff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f4f6fa; font-weight: 600; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:nth-child(even) td { background: #fbfbfd; }
.bar { background: #e8eef7; border-radius: 3px; height: 10px;
       position: relative; overflow: hidden; }
.bar > span { display: block; height: 100%; background: #78b53e; }
.footer { margin-top: 48px; font-size: 12px; color: #888; }
@media print { body { background: #fff; } .bar > span { -webkit-print-color-adjust: exact; } }
"""


def render_html(
    out_path: Path,
    stats: dict[str, list[tuple[object, int, float]]],
    meta: dict,
    labels: dict[str, str] | None = None,
) -> None:
    esc = html_mod.escape
    parts: list[str] = []
    parts.append("<!doctype html><html lang='it'><head><meta charset='utf-8'>")
    parts.append(f"<title>Statistiche ricette tipo={meta['type']}</title>")
    parts.append(f"<style>{HTML_CSS}</style></head><body>")
    parts.append(f"<h1>Statistiche ricette — tipo={meta['type']}</h1>")
    parts.append("<div class='meta'>")
    parts.append(f"<div><strong>Osservazioni:</strong> {meta['n_observations']}</div>")
    parts.append(f"<div><strong>Macchine:</strong> {meta['n_machines']}</div>")
    parts.append(f"<div><strong>Ricette scansionate:</strong> {meta['n_recipes']}</div>")
    parts.append(f"<div><strong>Data analisi:</strong> {esc(meta['timestamp_human'])}</div>")
    parts.append(f"<div><strong>File ricette:</strong> <code>{esc(meta['recipes_path'])}</code></div>")
    parts.append(f"<div><strong>File UUID:</strong> <code>{esc(meta['uuid_path'])}</code></div>")
    parts.append("</div>")
    parts.append("<div class='toc'><strong>Attributi analizzati</strong><ul>")
    for attr in stats.keys():
        label = (labels or {}).get(attr, attr)
        toc_text = f"{esc(label)} <small>({esc(attr)})</small>" if label != attr else esc(attr)
        parts.append(f"<li><a href='#{esc(attr)}'>{toc_text}</a></li>")
    parts.append("</ul></div>")
    for attr, rows in stats.items():
        label = (labels or {}).get(attr, attr)
        if label != attr:
            h2_content = f"{esc(label)} <small style='color:#888;font-weight:normal'>({esc(attr)})</small>"
        else:
            h2_content = esc(attr)
        parts.append(f"<h2 id='{esc(attr)}'>{h2_content}</h2>")
        if not rows:
            parts.append("<p><em>Attributo non presente nelle osservazioni.</em></p>")
            continue
        parts.append(f"<p>{len(rows)} valori distinti</p>")
        parts.append("<table><thead><tr><th>valore</th><th class='num'>occorrenze</th>"
                     "<th class='num'>%</th><th>distribuzione</th></tr></thead><tbody>")
        for val, cnt, pct in rows:
            parts.append(
                f"<tr><td>{esc(str(val))}</td><td class='num'>{cnt}</td>"
                f"<td class='num'>{pct:.1f}%</td>"
                f"<td><div class='bar'><span style='width:{pct:.1f}%'></span></div></td></tr>"
            )
        parts.append("</tbody></table>")
    parts.append(f"<div class='footer'>Generato {esc(meta['timestamp_human'])}</div>")
    parts.append("</body></html>")
    out_path.write_text("".join(parts), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--recipes", required=True, type=Path,
                    help="Path a machine_recipes.json")
    ap.add_argument("--type", dest="ptype", required=True, type=int,
                    help="Codice type del sotto-prodotto (es. 3)")
    ap.add_argument("--uuid-file", type=Path, default=None,
                    help="CSV con UUID macchine da includere (default: "
                         "<recipes_dir>/data/silver_uuid.csv)")
    ap.add_argument("--attrs", default="all",
                    help="Lista attributi CSV, oppure 'all' per tutti (default: all)")
    ap.add_argument("--out-dir", type=Path, required=True,
                    help="Directory dove scrivere i tre file di output")
    ap.add_argument("--labels-file", type=Path, default=None,
                    help="File JSX/JS con etichette italiane (es. data/it.jsx)")
    args = ap.parse_args()

    labels: dict[str, str] | None = None
    if args.labels_file:
        lf = args.labels_file.resolve()
        if not lf.is_file():
            print(f"ATTENZIONE: file etichette non trovato: {lf}", file=sys.stderr)
        else:
            labels = load_labels(lf)

    recipes_path: Path = args.recipes.resolve()
    if not recipes_path.is_file():
        print(f"ERRORE: file ricette non trovato: {recipes_path}", file=sys.stderr)
        return 1

    uuid_path: Path = (args.uuid_file.resolve() if args.uuid_file
                       else recipes_path.parent / "data" / "silver_uuid.csv")
    if not uuid_path.is_file():
        print(f"ERRORE: file UUID non trovato: {uuid_path}", file=sys.stderr)
        return 1

    try:
        allowed_uuids = read_uuid_list(uuid_path)
    except Exception as e:
        print(f"ERRORE lettura UUID {uuid_path}: {e}", file=sys.stderr)
        return 1
    if not allowed_uuids:
        print(f"ERRORE: nessun UUID nel file {uuid_path}", file=sys.stderr)
        return 1

    try:
        machines = load_recipes(recipes_path)
    except Exception as e:
        print(f"ERRORE lettura ricette {recipes_path}: {e}", file=sys.stderr)
        return 1

    observations, n_machines, n_recipes = extract_observations(
        machines, allowed_uuids, args.ptype
    )
    if not observations:
        print(f"ATTENZIONE: nessuna osservazione trovata per type={args.ptype} "
              f"su {len(allowed_uuids)} UUID.", file=sys.stderr)
        return 1

    all_keys: set[str] = set()
    for obs in observations:
        all_keys.update(obs.keys())
    all_keys.discard("type")

    warnings_count = 0
    if args.attrs.strip().lower() in ("all", ""):
        attrs = sorted(all_keys)
    else:
        requested = [a.strip() for a in args.attrs.split(",") if a.strip()]
        valid = [a for a in requested if a in all_keys]
        missing = [a for a in requested if a not in all_keys]
        if missing:
            warnings_count += len(missing)
            print(f"ATTENZIONE: attributi non presenti (ignorati): "
                  f"{', '.join(missing)}", file=sys.stderr)
        if not valid:
            print("ERRORE: nessun attributo valido da analizzare.", file=sys.stderr)
            return 1
        attrs = valid

    stats = compute_stats(observations, attrs)

    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M")
    prefix = f"statistiche_tipo-{args.ptype}_{stamp}"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_dir = args.out_dir.resolve()

    meta = {
        "type": args.ptype,
        "n_observations": len(observations),
        "n_machines": n_machines,
        "n_recipes": n_recipes,
        "timestamp_human": now.strftime("%Y-%m-%d %H:%M"),
        "recipes_path": str(recipes_path),
        "uuid_path": str(uuid_path),
    }

    csv_path = out_dir / f"{prefix}.csv"
    md_path = out_dir / f"{prefix}.md"
    html_path = out_dir / f"{prefix}.html"
    render_csv(csv_path, stats, labels)
    render_md(md_path, stats, meta, labels)
    render_html(html_path, stats, meta, labels)

    print(f"CSV:  {csv_path}")
    print(f"MD:   {md_path}")
    print(f"HTML: {html_path}")
    print(f"Osservazioni: {len(observations)} | Macchine: {n_machines} | "
          f"Ricette scansionate: {n_recipes} | Attributi: {len(attrs)}")
    return 2 if warnings_count else 0


if __name__ == "__main__":
    sys.exit(main())

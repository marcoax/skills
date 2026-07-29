#!/usr/bin/env python3
"""Misura la discoverability-per-grep del codice eraCms.

Popolazioni misurate separatamente:
  - classi PHP (nome vincolato dal path in alcuni contesti)
  - metodi pubblici PHP (nome libero: il vero collo di bottiglia)
  - componenti/composables Vue+JS
"""
import re, os, sys, collections, json

ROOT = "/Users/marcoasperti/web/newEra/eraCms"
PHP_DIRS = ["app"]
JS_DIRS = ["resources/js"]
SKIP = ("vendor", "node_modules", "storage", "bootstrap/cache")

def walk(dirs, exts):
    for d in dirs:
        for base, subdirs, files in os.walk(os.path.join(ROOT, d)):
            if any(s in base for s in SKIP):
                continue
            for f in files:
                if f.endswith(exts):
                    yield os.path.join(base, f)

def words(name):
    """Numero di parole in un identificatore camelCase/PascalCase/snake_case."""
    name = re.sub(r'[_\-]', ' ', name)
    name = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', name)
    name = re.sub(r'(?<=[A-Z])(?=[A-Z][a-z])', ' ', name)
    return len([w for w in name.split() if w])

# ---------------- raccolta definizioni ----------------
class_defs = collections.defaultdict(list)   # nome -> [file]
method_defs = collections.defaultdict(list)  # nome -> [(file, class)]
php_files = list(walk(PHP_DIRS, (".php",)))
php_files = [f for f in php_files if not f.endswith(".blade.php")]

interpolated = []      # stringhe identificatore costruite per interpolazione
undocumented = []      # metodi pubblici senza docblock
error_no_prefix = []   # exception con messaggio che inizia per interpolazione

RE_CLASS = re.compile(r'^\s*(?:final\s+|abstract\s+)?(?:class|interface|trait|enum)\s+(\w+)', re.M)
RE_METHOD = re.compile(r'^([ \t]*)(?:(public|protected|private)\s+)?(?:static\s+)?function\s+(\w+)\s*\(', re.M)
RE_THROW = re.compile(r'throw new [\w\\]+\(\s*(["\'`])')

for path in php_files:
    src = open(path, encoding="utf8", errors="ignore").read()
    rel = os.path.relpath(path, ROOT)
    for m in RE_CLASS.finditer(src):
        class_defs[m.group(1)].append(rel)
    cur_class = None
    cm = RE_CLASS.search(src)
    if cm:
        cur_class = cm.group(1)
    lines = src.split("\n")
    for m in RE_METHOD.finditer(src):
        vis, name = m.group(2), m.group(3)
        if vis in ("private", "protected"):
            continue
        if name.startswith("__"):
            continue
        method_defs[name].append((rel, cur_class))
        # docblock immediatamente sopra?
        line_no = src[:m.start()].count("\n")
        prev = [l.strip() for l in lines[max(0, line_no - 4):line_no] if l.strip()]
        has_doc = any(p.startswith("*/") or p.startswith("/**") for p in prev)
        if not has_doc:
            undocumented.append((rel, name))

    # stringhe-identificatore costruite per interpolazione
    for m in re.finditer(r'''(?:event|dispatch|trans|__|view|config|Cache::(?:get|put|forget|remember\w*)|Log::\w+)\s*\(\s*"([^"]*\$\{?\w)''', src):
        interpolated.append((rel, m.group(0)[:70]))
    for m in re.finditer(r'''throw new [\w\\]+\(\s*"\s*\$''', src):
        error_no_prefix.append((rel, m.group(0)[:60]))

# ---------------- unicità per numero di parole ----------------
def uniqueness_table(defs, key=lambda v: v):
    buckets = collections.defaultdict(lambda: [0, 0])  # nwords -> [total, unique]
    for name, sites in defs.items():
        n = min(words(name), 4)
        distinct = len({key(s) for s in sites})
        buckets[n][0] += 1
        if distinct == 1:
            buckets[n][1] += 1
    return buckets

def show(title, buckets):
    print(f"\n== {title}")
    print(f"{'parole':>7} {'totale':>7} {'unici':>7} {'% unico':>8}")
    tot = uniq = 0
    for n in sorted(buckets):
        t, u = buckets[n]
        tot += t; uniq += u
        label = f"{n}+" if n == 4 else str(n)
        print(f"{label:>7} {t:>7} {u:>7} {100*u/t:>7.0f}%")
    print(f"{'TOT':>7} {tot:>7} {uniq:>7} {100*uniq/tot:>7.0f}%")

show("Classi PHP: nome globalmente unico?", uniqueness_table(class_defs))
show("Metodi pubblici PHP: nome unico nel repo?", uniqueness_table(method_defs, key=lambda s: s[0]))

# ---------------- worst offenders ----------------
print("\n== Metodi pubblici piu' ambigui (nome -> n. file di definizione)")
worst = sorted(((len({f for f, _ in v}), k) for k, v in method_defs.items()), reverse=True)[:20]
for n, name in worst:
    print(f"  {n:>3}x  {name}  ({words(name)} parola/e)")

print("\n== Classi con nome duplicato")
dups = {k: v for k, v in class_defs.items() if len(set(v)) > 1}
for k, v in sorted(dups.items(), key=lambda kv: -len(set(kv[1])))[:15]:
    print(f"  {len(set(v))}x {k}: {', '.join(sorted(set(v)))}")

print(f"\n== Metodi pubblici senza PHPDoc: {len(undocumented)} su {sum(len(v) for v in method_defs.values())}")
print(f"== Stringhe-identificatore costruite per interpolazione: {len(interpolated)}")
for rel, snip in interpolated[:15]:
    print(f"  {rel}: {snip}")
print(f"== Exception con messaggio che inizia per variabile: {len(error_no_prefix)}")
for rel, snip in error_no_prefix[:10]:
    print(f"  {rel}: {snip}")

# ---------------- frontend ----------------
js_files = list(walk(JS_DIRS, (".js", ".ts", ".vue")))
js_base = collections.defaultdict(list)
for p in js_files:
    js_base[os.path.basename(p)].append(os.path.relpath(p, ROOT))
jdups = {k: v for k, v in js_base.items() if len(v) > 1}
print(f"\n== Frontend: {len(js_files)} file, {len(jdups)} basename duplicati")
for k, v in sorted(jdups.items(), key=lambda kv: -len(kv[1]))[:15]:
    print(f"  {len(v)}x {k}: {', '.join(v[:4])}")

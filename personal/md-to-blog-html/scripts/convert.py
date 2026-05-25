#!/usr/bin/env python3
"""Convert a Markdown article into the Magutti blog HTML format.

Usage:
    python3 convert.py <input.md> [--no-clipboard] [--stdout]

Output:
    Writes <input>.html next to the source file.
    Default: also copies to macOS clipboard via pbcopy.
"""

import argparse
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

INTERNAL_HOSTS = {"magutti.com", "www.magutti.com"}

PLACEHOLDER = "\x00MD2HTML_{}\x00"


def escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_inline(text: str) -> str:
    """Render inline MD constructs to HTML.

    Order matters: inline code first (its content is protected from further
    passes via placeholders), then bold, links, em-dash, finally orphan-char escape.
    """
    placeholders: list[str] = []

    def stash(html: str) -> str:
        placeholders.append(html)
        return PLACEHOLDER.format(len(placeholders) - 1)

    def code_repl(m: re.Match) -> str:
        return stash(f"<code>{escape_html(m.group(1))}</code>")

    text = re.sub(r"`([^`]+)`", code_repl, text)

    def link_repl(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        label_html = render_inline_no_code(label)
        if url.startswith(("http://", "https://")):
            host = urlparse(url).hostname or ""
            external = host.lower() not in INTERNAL_HOSTS
        else:
            external = False
        attrs = f' href="{url}"'
        if external:
            attrs += ' target="_blank" rel="noopener"'
        return stash(f"<a{attrs}>{label_html}</a>")

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)

    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: stash(f"<strong>{escape_text(m.group(1))}</strong>"),
        text,
    )

    text = re.sub(
        r"(?<![A-Za-z0-9_])_([^_\n]+)_(?![A-Za-z0-9_])",
        lambda m: stash(f"<em>{escape_text(m.group(1))}</em>"),
        text,
    )
    text = re.sub(
        r"(?<![\*A-Za-z0-9])\*([^*\n]+)\*(?![\*A-Za-z0-9])",
        lambda m: stash(f"<em>{escape_text(m.group(1))}</em>"),
        text,
    )

    text = escape_text(text)
    text = text.replace("—", "&mdash;")

    for i, html in enumerate(placeholders):
        text = text.replace(PLACEHOLDER.format(i), html)

    return text


def render_inline_no_code(text: str) -> str:
    """Inline rendering for contexts that cannot contain code spans (link labels)."""
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: f"<strong>{escape_text(m.group(1))}</strong>",
        text,
    )
    return escape_text(text).replace("—", "&mdash;")


def escape_text(text: str) -> str:
    """Escape orphan &, <, > in plain text (not inside HTML we generated)."""
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "&":
            m = re.match(r"&(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);", text[i:])
            if m:
                out.append(m.group(0))
                i += len(m.group(0))
                continue
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def convert(md: str) -> str:
    lines = md.splitlines()
    blocks: list[str] = []
    h2_seen = False
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            if i < n:
                i += 1
            blocks.append(f"<pre><code>{escape_html(chr(10).join(buf))}</code></pre>")
            continue

        if stripped.startswith("# ") and not stripped.startswith("## "):
            i += 1
            continue

        if stripped.startswith("## "):
            if h2_seen:
                blocks.append("<hr />")
            h2_seen = True
            blocks.append(f"<h2>{render_inline(stripped[3:].strip())}</h2>")
            i += 1
            continue

        if stripped.startswith("### "):
            blocks.append(f"<h3>{render_inline(stripped[4:].strip())}</h3>")
            i += 1
            continue

        if stripped == "::: intro":
            i += 1
            buf = []
            while i < n and lines[i].strip() != ":::":
                buf.append(lines[i])
                i += 1
            if i < n:
                i += 1
            content = " ".join(l.strip() for l in buf if l.strip())
            blocks.append(f'<p class="article-intro">{render_inline(content)}</p>')
            continue

        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            content = " ".join(l.strip() for l in buf if l.strip())
            blocks.append(
                f'<div class="highlight-box">{render_inline(content)}</div>'
            )
            continue

        ul_match = re.match(r"^[-*]\s+", line)
        ol_match = re.match(r"^\d+\.\s+", line)
        if ul_match or ol_match:
            tag = "ul" if ul_match else "ol"
            pattern = r"^[-*]\s+" if ul_match else r"^\d+\.\s+"
            items = []
            while i < n and re.match(pattern, lines[i]):
                item_text = re.sub(pattern, "", lines[i])
                items.append(f"<li>{render_inline(item_text.strip())}</li>")
                i += 1
            blocks.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue

        para_lines = []
        while i < n and lines[i].strip() and not _is_block_start(lines[i]):
            para_lines.append(lines[i].strip())
            i += 1
        if para_lines:
            content = " ".join(para_lines)
            blocks.append(f"<p>{render_inline(content)}</p>")

    return "\n".join(blocks) + "\n"


def _is_block_start(line: str) -> bool:
    s = line.strip()
    if s.startswith(("# ", "## ", "### ", "```", ">", "::: intro")):
        return True
    if re.match(r"^[-*]\s+", line) or re.match(r"^\d+\.\s+", line):
        return True
    return False


def copy_to_clipboard(text: str) -> bool:
    if sys.platform != "darwin":
        return False
    try:
        p = subprocess.run(
            ["pbcopy"], input=text.encode("utf-8"), check=True
        )
        return p.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="MD → Magutti blog HTML")
    ap.add_argument("input", help="Path to source .md file")
    ap.add_argument("--no-clipboard", action="store_true", help="Skip pbcopy")
    ap.add_argument("--stdout", action="store_true", help="Also print HTML to stdout")
    args = ap.parse_args()

    src = os.path.abspath(args.input)
    if not os.path.isfile(src):
        print(f"error: file not found: {src}", file=sys.stderr)
        return 1

    with open(src, "r", encoding="utf-8") as f:
        md = f.read()

    html = convert(md)

    out_path = os.path.splitext(src)[0] + ".html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out_path}", file=sys.stderr)

    if not args.no_clipboard and copy_to_clipboard(html):
        print("copied to clipboard", file=sys.stderr)

    if args.stdout:
        sys.stdout.write(html)

    return 0


if __name__ == "__main__":
    sys.exit(main())

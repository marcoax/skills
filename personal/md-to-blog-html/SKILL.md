---
name: md-to-blog-html
description: >
  Converts a Markdown article into the exact HTML format used by the Magutti blog
  (News model description field). Produces <h2> sections separated by <hr />,
  <p class="article-intro"> for intro, <div class="highlight-box"> for callouts,
  external links with target="_blank" rel="noopener", and proper &mdash;/&amp;
  escaping. Use when the user asks to convert an MD file for the blog, prepare
  a News article HTML, paste-ready blog post, or mentions Magutti blog formatting.
---

# MD to Blog HTML

Converts a Markdown source file into the HTML format used in the `News.description` field on https://www.magutti.com/.

The canonical output format is documented by the reference at `reference/template.html` — consult it if you need to extend the converter for unsupported constructs.

## Quick start

```bash
python3 .claude/skills/md-to-blog-html/scripts/convert.py path/to/article.md
```

Writes `path/to/article.html` next to the source and copies the HTML to the macOS clipboard (ready to paste into the admin News form).

Flags:
- `--no-clipboard` — skip `pbcopy`
- `--stdout` — also print the HTML to stdout

## Source MD conventions

| Markdown | HTML output |
|---|---|
| `# Title` | **stripped** (title lives in `News.title`) |
| `## Section` | `<hr />` (between sections) + `<h2>…</h2>` |
| `### Sub` | `<h3>…</h3>` |
| `::: intro` … `:::` | `<p class="article-intro">…</p>` |
| `> line` (one or more contiguous lines) | `<div class="highlight-box">…</div>` |
| ` ```…``` ` | `<pre><code>…</code></pre>` (HTML-escaped) |
| `- item` / `* item` | `<ul><li>…</li></ul>` |
| `1. item` | `<ol><li>…</li></ol>` |
| Plain paragraph | `<p>…</p>` |
| `**bold**` | `<strong>…</strong>` |
| `` `code` `` | `<code>…</code>` |
| `[txt](url)` external | `<a href="url" target="_blank" rel="noopener">txt</a>` |
| `[txt](url)` magutti.com or relative | `<a href="url">txt</a>` |
| `—` (em-dash) | `&mdash;` |
| Orphan `&`, `<`, `>` | `&amp;`, `&lt;`, `&gt;` |

## Example

Input (`article.md`):

```markdown
# My Article Title

::: intro
This article explores **a real-world case** of debugging with AI.
:::

## The Problem

After migrating, this warning appeared:

`bson_append_array(): invalid array detected`

> **AI Conclusion:** None of the proposed solutions eliminated the warning.

## The Lesson

See the [StackOverflow thread](https://stackoverflow.com/questions/69670396) for details.
```

Output (`article.html`):

```html
<p class="article-intro">This article explores <strong>a real-world case</strong> of debugging with AI.</p>
<h2>The Problem</h2>
<p>After migrating, this warning appeared:</p>
<p><code>bson_append_array(): invalid array detected</code></p>
<div class="highlight-box"><strong>AI Conclusion:</strong> None of the proposed solutions eliminated the warning.</div>
<hr />
<h2>The Lesson</h2>
<p>See the <a href="https://stackoverflow.com/questions/69670396" target="_blank" rel="noopener">StackOverflow thread</a> for details.</p>
```

## Workflow

1. Marco writes the article in Markdown using the conventions above.
2. Run the converter — HTML lands in clipboard and on disk.
3. **Ask the user**: _"Do you also want SEO title and meta description?"_ (yes/no)
4. If **yes**: read the source MD, generate SEO fields, and print them in chat for copy-paste (see "SEO generation" below).
5. Paste the HTML into the `description` field of the News record in the admin (and the SEO fields if generated).
6. Save.

If a construct is missing, compare the actual blog output against `reference/template.html` and extend `scripts/convert.py` (the parser is line-based and easy to extend).

## SEO generation

Only after the user confirms in step 3. Produce **2–3 variants for each field** directly in chat (no file write — user copies and pastes the one they prefer):

- **SEO title** — 50–60 chars, includes the primary keyword/topic of the article.
- **SEO meta description** — 150–160 chars, summarises the article in one sentence, includes the primary keyword.

### Tone

Technical, restrained, factual. **No marketing emphasis**: avoid superlatives ("ultimate", "powerful", "amazing"), no clickbait ("you won't believe…"), no hype verbs ("master", "unlock", "transform"), no emoji, no hard CTAs. Describe what the article covers, not how exciting it is. Match the article's own register.

### Output format

```
SEO title variants:
1. <variant 1>   (NN chars)
2. <variant 2>   (NN chars)
3. <variant 3>   (NN chars)

SEO description variants:
1. <variant 1>   (NNN chars)
2. <variant 2>   (NNN chars)
3. <variant 3>   (NNN chars)
```

Each variant must include the character count to confirm it fits the range. Match the article's language — if the MD is in Italian, generate Italian SEO fields.

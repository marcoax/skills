---
name: discoverable-code-check
description: >
  Discoverability checkpoint on code just written: checks that every new symbol can be reached
  with a single text search. Invoke once implementation is finished, before code review. Do not
  use it while writing the code, and do not use it as a correctness, performance or security
  review — code-review, advanced-code-review and security-review cover those.
---

# Discoverability check

An agent finds code by searching for strings and reading the window around the match: no hover,
no jump-to-definition, no memory between sessions. Every identifier is a query, and every search
that misses its target costs wasted reads. This check verifies that the code just written answers
in a single search.

## Conventions win

Laravel and project conventions take precedence over every finding of this skill. When a name is
imposed, **the name stays and gets documented**:

- framework hooks — `render`, `handle`, `boot`, `register`, `index`, `show`, `store`, `rules`,
  `authorize`, `toArray`, `toMail`, `via`
- classes resolved by path — Blade components (`Website/News/Index.php` ↔ `<x-website.news.index>`),
  parallel Api/Website/Admin controllers, migrations, Facades next to their implementation
- contract methods implemented by many classes — `getFieldSpec`, the builders, the casts

Never propose a rename that breaks framework resolution or splits a pattern already used elsewhere
in the repo. When in doubt, look at the siblings and align: a name collision consistent with the
rest of the code is not a defect.

## Scope

Only the code touched in this work (`git diff` against the branch base). Pre-existing debt is not
the subject of the check — report it only if the new code makes it worse, for example by adding
the fifth silent `execute()` to a group that had four.

## The three checks

**1. The doc line where the search lands.** Every new public method and class needs one PHPDoc
line with two jobs: the constraint the signature cannot express (unit of measure, timezone,
ownership, ordering, side effect, which of the two dates) and the plain-words phrase someone would
search for. camelCase names are invisible to natural-language searches: `getFieldSpec` does not
match a grep for "field spec", `SessionExpiryChecker` does not match "session expired". The line
above the definition is the whole message that reaches the searcher. It is not a comment that
re-explains the code: if the signature already says everything and the name is searchable, skip it.

**2. Generic verbs without an object.** `execute`, `process`, `calculate`, `handle`, `get`, `run`
on new code in `Domain/`, `Tools/`, `Builders/` — where the name is free — need their object:
`calculateShippingCost`, not `calculate`. Qualify as much as needed to be unique, then stop; the
rest goes in the doc line. If the bare verb is imposed by an interface or by Laravel, the previous
section applies: it stays, and gets the doc line.

**3. A single definition site.** If this work moved or duplicated code, verify it disappeared from
the origin in the same commit. A helper copied to two places makes every future search land on
both, and one of them ages silently. Same for names that became lies: if the behavior changed, the
name changes now.

## Output

List findings as `file:line — what is missing`, ordered by cost to whoever will search,
separating those that fall under "Conventions win" (to document) from those where the name can be
improved. If there is nothing, say so in one line. Then ask which to apply before editing the
files: this is a checkpoint, not an automatic refactor.

Close with the six verification questions:

1. Is a single search for each new name enough to find its implementation?
2. Do the new generic verbs have their object, or a convention that justifies them?
3. Is what the caller must know but the signature does not say written at the definition?
4. Do the new log/error strings exist verbatim in the source, without leading interpolation?
5. Did anything change behavior without changing name?
6. Did moved code disappear from where it was?

## Why these three and not twenty others

The rules are cut to the measure of this repo, not to a generic list:
`reference/eracms-baseline.md`. Re-measure with `reference/measure_discoverability.py` to verify
they still hold.

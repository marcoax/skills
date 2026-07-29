---
name: opus5-skill-authoring
description: "Write, review, or migrate a skill or prompt for the Claude 5 generation (Opus 5, Sonnet 5, Fable 5). Use when the user wants to author a new SKILL.md, update an old skill for newer models, fix a bloated or over-constrained skill, or asks 'create a skill', 'migrate this skill to Opus 5', 'why is my skill flaky on Opus 5'. Applies the flipped context-engineering rules (judgment over rules, interfaces over examples, progressive disclosure, one home per rule, rich references) and validates the result with a binary eval rubric. Do not use for non-skill coding tasks or for optimizing via repeated automated eval loops; use autoresearch for that."
---

# Opus 5 Skill Authoring

Skills written for older models over-constrain the Claude 5 generation. The models now have better judgment, so the job shifted from writing more instructions to designing a clean, minimal context. This skill authors and migrates skills to that standard.

Do not skip understanding the target task before writing. Read the real workflow the skill must cover, then apply the rules below.

## The six flipped rules

Apply every one when writing or reviewing a skill.

| Old habit | Claude 5 rule |
|---|---|
| Rigid rules for every case | State the goal, let the model use judgment. Keep hard rules only at high stakes. |
| Examples to copy | Design expressive interfaces; examples set aesthetics, not the approach. |
| Everything up front | Progressive disclosure: keep `SKILL.md` compact, link the rest. |
| Repeat instructions | One clear description, in one place. |
| Memory hardcoded in files | Rely on auto-memory; store only durable, non-obvious rules. |
| Prose specs | Rich references: a test, a mockup, or real code beats a paragraph. |

## Authoring workflow

1. **Scope.** Name the exact task, its trigger conditions, and what "done" looks like. If vague, ask before writing.
2. **Trigger.** Write the `description` as the router: when to use it AND when not to. This is the highest-leverage part; most misfires are trigger failures.
3. **Draft `SKILL.md`.** Frontmatter (`name`, `description`) + a short instruction body. Describe behavior, not banned actions. Match the wording style of the surrounding skills.
4. **Progressive disclosure.** If it grows past ~1 screen of instructions, move examples, edge cases, and reference material into linked files loaded on demand. Keep the entry file lean.
5. **One home per rule.** Grep for the same instruction in `CLAUDE.md`, other skills, and the prompt. Delete duplicates; collisions make the model burn tokens resolving contradictions and cause flaky behavior.
6. **Safety stays rigid.** Never soften input validation at trust boundaries, destructive-action gates, or security rules into "judgment."
7. **Validate before shipping** (below).

## Validation rubric

Binary checks, run against real behavior, not the file text:

| Area | Check |
|---|---|
| Trigger | Fires on relevant prompts |
| Non-trigger | Stays quiet on similar out-of-scope prompts |
| Context | Loads only what's needed |
| Instructions | Direct, non-repetitive, no contradictions |
| Tools | Right tool, no superfluous calls |
| Scope | No unrequested files, deps, or work |
| Safety | Confirms before irreversible actions |
| Output | Matches format and completion criteria |
| Efficiency | No overthinking, double-checking, or verbose output |
| Robustness | Handles incomplete, ambiguous, adversarial input |

Minimum eval set: 5 positive cases, 5 negative (must-not-trigger), 3 edge cases, 2 adversarial (scope creep / safety bypass), 1 end-to-end with real files and tools.

```yaml
- id: minimal-change
  prompt: "Fix the typo in the title"
  checks:
    skill_triggered: true
    requested_file_changed: true
    unrelated_files_changed: false
    new_dependency_added: false
    tests_pass: true
```

A skill is valid only with correct instructions + observed behavior + verifiable result + no side effects. Text conformance alone is not enough.

## Migration mode (old skill → Opus 5)

When updating an existing skill:

- **Delete every "do not X" line** the model can now judge; keep only the gotchas and high-stakes rules. Add a rule back only when a bad output proves it earns its place.
- **Turn rigid style/tone/length rules into pointers** ("match the last 3 messages in the thread", "follow the most recent report in this folder") except at high stakes or in static contexts.
- **Split example handling**: keep examples for format, extract a plain-language standard for the approach so the example doesn't cap the model's intelligence.
- **Find and remove contradictions** across `SKILL.md`, `CLAUDE.md`, memory, and prompt.
- Caution on legacy codebases with strange conventions: stripping too much can move cost from tokens to review time. Test on real tasks.

## Output

Deliver the `SKILL.md` (and any linked reference files), then a short note: what rules you applied, what you cut, and the eval cases to run. If the explanation is longer than the skill, cut the explanation.

## Sources

Anthropic, *The new rules of context engineering for Claude 5 generation models* (Thariq); *Prompting Claude Opus 5*; *Effective context engineering for AI agents*.

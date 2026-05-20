---
title: "Claude Code Output Styles: What They Are and How to Bend Them to Your Workflow"
description: "A practical guide to Claude Code's output styles — from the four built-in styles to crafting your own custom one."
date: 2026-05-19
tags: [claude-code, ai, development, productivity]
---

# Claude Code Output Styles: What They Are and How to Bend Them to Your Workflow

There's a recurring moment for anyone who has used Claude Code for a few weeks: you catch yourself typing the same sentence at the start of every session. *"Explain what you're doing as you do it."* Or *"Don't ask me to confirm the obvious, just go."* Or maybe *"Always answer with a diagram before the code."*

Repeating the same instruction in every conversation is the symptom of a missing piece of configuration. And the configuration that solves exactly this problem is called an **output style**.

This article starts from scratch — what they are, why they exist — and goes all the way to building one of your own. Along the way there's also an argument: output styles aren't just a formatting convenience, they're a tool for deciding *how much* the AI should make you work. If you've never heard of them, the starting point is right below. If you already know them and want to jump straight to the custom part, skip to the second-to-last section.

## What they are, in one sentence

An output style changes **how** Claude responds, not **what** Claude knows.

It's a distinction worth pinning down right away, because it's the most common misconception. An output style doesn't teach Claude new facts about your project, doesn't give it access to documentation, doesn't change its capabilities. It works on a different plane: tone, role, response format. Technically, it does this by modifying the *system prompt* — the baseline instructions Claude receives at the start of every session.

If you want to teach Claude your codebase conventions, the tool is a different one (`CLAUDE.md`). An output style is what you reach for when the *content* is fine but the *form* isn't: too verbose, too quiet, too thin on teaching for your taste.

## The four built-in styles

Claude Code ships with four output styles ready to use. Three are designed for software work, one is simply the standard behavior.

### Default

This is the style Claude Code runs with if you touch nothing. The classic system prompt, tuned to complete development tasks efficiently. Lean, action-oriented, few unrequested explanations. For most day-to-day work it's the right choice — the other styles are targeted *deviations* from this baseline, not universal replacements.

### Proactive

The style for people who hate pauses. With Proactive, Claude executes right away, makes reasonable assumptions instead of stopping to ask about routine decisions, and generally prefers action over planning.

An important detail that often gets missed: Proactive applies the same logic as *auto mode* **without** changing your permission mode. In plain terms — Claude becomes more decisive in *reasoning and proposing*, but you still see permission prompts before tools actually run. It's not a surrender of control, it's a surrender of micro-hesitations.

When to use it: rapid prototyping, exploratory tasks, moments when you already know where you want to go and Claude's questions slow you down more than they help.

### Explanatory

Here we enter "Claude as a learning tool" territory. With Explanatory, while moving the development task forward, Claude inserts *Insights* — short, educational explanations of why it made a particular implementation choice, or how a codebase pattern works.

It's the style to switch on when you're working on a codebase you don't know, or when you want every change to leave you with something more than the change itself. It doesn't ask you for anything: it keeps doing the work, but comments on the *why* along the way.

### Learning

Learning is Explanatory taking one step further, and changing its nature. It doesn't just explain: it involves you.

On top of sharing Insights while it codes, Claude asks **you** to write small, strategic pieces of code yourself. Concretely, it places `TODO(human)` markers in the code — precise spots where it's your turn to get your hands dirty. It's a collaborative, learn-by-doing mode: you learn by doing, not by watching.

It's the most demanding of the four styles, and that's a deliberate choice. If you're using Claude Code to *learn* — a new language, a framework, a pattern — Learning turns the session from "watch the expert" into "let's work together." If you have a deadline, though, it's not the moment.

## An honest warning about cost

There's a trade-off the documentation states openly, and it's worth knowing before you grow attached to a style.

The Explanatory and Learning styles, **by design**, produce longer responses than Default. More Insights, more explanations, more text. That means more output tokens — and therefore higher consumption. It's not a bug, it's how they work: you're paying for the explanations you asked for.

On the input side, adding instructions to the system prompt increases input tokens, but here *prompt caching* softens the blow after the first request in a session.

The practical takeaway: Explanatory and Learning are excellent when the goal is to understand or to learn. They're wasteful if you leave them on for routine work, where Default does the same job with fewer words.

## A digression that isn't a digression: skill atrophy

So far Learning and Explanatory might look like two convenience options — Claude talking a bit more, for those in the mood to read. But there's a more serious reading, and it's the one that gives these two styles a weight the documentation alone doesn't hint at.

Addy Osmani — a well-known figure in the frontend and developer-experience community — gave a name to a phenomenon many developers feel but struggle to bring into focus: **skill atrophy**. The idea is simple and uncomfortable. When every problem gets solved by describing it to an AI and accepting the answer within seconds, you gain speed today and lose something tomorrow: the *mental map* of the codebase, the instinct for where a bug probably hides, the deep understanding of the system you're the one responsible for maintaining.

It's not just a feeling. There's research, cited in this debate, suggesting that developers who use AI to generate code score lower — around 17% — on comprehension tests, compared to those who wrote that code by hand. A single study isn't a verdict, but the intuition holds: there's a difference between someone who *understands* a system and someone who can merely *operate* it.

This is where output styles stop being a configuration detail and become a choice of method. Osmani himself has long argued that you're not obliged to accept the AI's default behavior: you can steer it. And his recurring advice is to treat AI as a learning tool, not a crutch — when the agent produces code you don't understand, that's the signal to stop and dig, not to push on.

Explanatory and Learning are exactly this: **friction reintroduced on purpose**. Explanatory forces you to walk past the *why* of every choice. Learning forces you to write the strategic pieces yourself, with its `TODO(human)` markers. They're slower than Default, they cost more tokens — and in this light, that's not a flaw but the explicit price of not losing the map.

The conclusion isn't "always use Learning." It's subtler: the speed of Default is right when you're executing something you already command, and the friction of Explanatory or Learning is right when you're working on something you should understand and don't yet. Knowing how to choose between the two, session by session, is a skill in itself.

## How to change your style

Two ways.

**The menu way.** Run `/config`, select *Output style* and pick from the menu. Your choice is saved to `.claude/settings.local.json`, at the local project level.

**The file way.** If you'd rather skip the menu, edit the `outputStyle` field directly in a settings file:

```json
{
  "outputStyle": "Explanatory"
}
```

Where you put this field depends on how "wide" you want the choice to apply:

- `~/.claude/settings.json` — applies to all your projects
- `.claude/settings.json` — applies to the project and can be shared with the team via git
- `.claude/settings.local.json` — applies to the project, but only for you (not versioned)

A detail about *timing* that prevents confusion: the output style is set in the system prompt at session start. If you change it while Claude Code is running, the change does **not** take effect immediately — you need to start a new session. It's a deliberate design: keeping the system prompt stable throughout the conversation lets prompt caching reduce latency and cost.

## Building a custom style

Here's where it gets interesting. The four built-in styles are starting points, but the real power is writing one of your own.

A custom style is simply a Markdown file: a block of *frontmatter* with metadata, followed by the instructions to add to the system prompt. You save it in one of three places, depending on scope:

- `~/.claude/output-styles` — user level
- `.claude/output-styles` — project level
- the *managed settings* directory — for policies managed at the organization level

The file name becomes the style name, unless you specify a `name` field in the frontmatter.

### A concrete example

Suppose you want a style that opens every explanation with a diagram, without giving up the way Claude writes code. The file might look like this:

```markdown
---
name: Diagrams first
description: Lead every explanation with a diagram
keep-coding-instructions: true
---

When explaining code, architecture, or data flow, start with
a Mermaid diagram showing the structure, then continue with
the explanation in prose.

## Diagram conventions

Use `flowchart TD` for control flow and `sequenceDiagram`
for request paths. Keep diagrams under 15 nodes.
```

### The field that makes the difference: `keep-coding-instructions`

There's a fundamental decision to make every time you create a custom style, and it's captured in a single frontmatter field.

By default, a custom style **removes** Claude Code's built-in software engineering instructions — the ones telling it how to scope changes, how to write comments, how to verify its work. This makes sense when Claude *isn't* doing development: if you're turning it into a writing assistant or a data analyst, those instructions are just noise.

But if you're only changing *how it communicates* — like in the diagram example — and you want it to keep coding exactly as before, you need to set `keep-coding-instructions: true`. Forgetting this is the most common mistake: you end up with a style that talks well but has lost its rigor on code.

The mnemonic: **are you changing the job, or just the voice?** If you're changing the job, leave the field at `false` (the default). If you're only changing the voice, set it to `true`.

### The other frontmatter fields

Beyond `name`, `description` and `keep-coding-instructions`, there's a fourth field that concerns those who distribute styles via plugins: `force-for-plugin`. When set, it applies the style automatically whenever the plugin is enabled, overriding the user's choice. It's a tool for people packaging configurations for others, not for everyday use.

## Output style, or something else?

Output styles are one tool among many for customizing Claude Code, and it's easy to use them in the wrong place. Here's the compass.

- **Output style** — you want a different role, tone, or response format on *every* turn. Modifies the system prompt.
- **`CLAUDE.md`** — you want Claude to *always* know your project's conventions and codebase context. Adds a message after the system prompt.
- **`--append-system-prompt`** — you want a one-off addition for a single invocation.
- **Agents** — you want a separate helper, with its own system prompt, model, and tools, for a focused task.
- **Skills** — you have a reusable workflow to load only when it's needed.

The summary: an output style is the right choice when the problem is *how Claude presents itself on every response*. For everything else — project context, one-off additions, workflows — there are better-suited tools.

## In closing

Output styles are one of those features that look like a detail until you use them. Their value isn't in the four built-in styles — as remarkable as Learning and Explanatory are — but in two underlying ideas. The first is practical: stop re-prompting the same thing, and encode it once. The second, more important: consciously choose how much speed and how much friction you want, instead of accepting the default. In an era where it's all too easy to let the AI do everything while you understand less and less, having an explicit lever on that trade-off is no small thing.

The advice for getting started is minimal. Try Explanatory for a few days on a project you don't know well, and observe whether the Insights actually help you or distract you. If you notice you want a recurring behavior that none of the four styles covers — that's the moment to write your own Markdown file.

The complete official documentation, with all the details on fields and debugging, is at `code.claude.com/docs/en/output-styles`.

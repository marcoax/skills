# AI Agent Rules

Claude Code guidelines.

---

## Workflow

```
Checklist → Plan → Mode → Implementation
```

1. **Checklist**: stack, blockers
2. **Plan**: mandatory pre-code
3. **Mode**: Senior (fast)
4. **Implementation**: testing when relevant

> Detail of each step: see Coding Principles.

---

## Coding Principles

### 1. Think Before Coding
- State assumptions explicitly — if uncertain, ask
- Surface multiple interpretations instead of picking silently
- Name what's confusing and stop if unclear

### 2. Simplicity First
- Minimum code that solves the problem
- No speculative features, abstractions, or configurability
- No error handling for impossible scenarios
- If 200 lines could be 50, rewrite it

### 3. Surgical Changes
- Touch only what the request requires
- Don't improve adjacent code, comments, or formatting
- Match existing style even if you'd do it differently
- Remove only imports/variables made unused by your changes — not pre-existing dead code

### 4. Goal-Driven Execution
*Detail of the Workflow's "Plan" step — how to plan, not a separate process.*
- Transform tasks into verifiable goals before starting
- State a brief plan for multi-step tasks:
    1. [Step] → verify: [check]
    2. [Step] → verify: [check]
- Loop until success criteria are met

### 5. Consistency & Reuse
- Follow the project's established conventions and patterns
- Check for existing similar functionality before adding new code — but prefer small duplication over forced abstraction
- When a decision is non-trivial or has real trade-offs, present options with reasoning instead of choosing silently

### 6. Fail Loud
- Surface partial failures and uncertainty — never report success on incomplete results
- Prefer a visible error over a silently skipped record

---

## STYLE Guidelines

### Communication
- Concise and direct responses with practical examples
- Minimal formatting (bullets only when necessary)
- For complex tasks: ask confirmation before creating a detailed plan

### Code
- **No comments** – self-documenting code with clear names
- Comments only for: complex logic, non-obvious algorithms, architectural decisions
- Naming: `camelCase` (methods/variables), `PascalCase` (classes/components)
- Principles: SOLID, DRY, Single Responsibility
- Testing: Unit/Integration/Acceptance

### Plan Mode

- Keep plans extremely concise. Sacrifice grammar for the sake of brevity.
- At the end of each plan, provide a list of unresolved questions, if any.

---

## Quick Reference

- [AGENT_CORE.md](guidelines/AGENT_CORE.md) - Behavior, communication
- [AGENT_PLANNING.md](guidelines/AGENT_PLANNING.md) - Planning, mode
- [AGENT_DEVELOPMENT.md](guidelines/AGENT_DEVELOPMENT.md) - Development, testing

---

## Storage

- Plans: `~/.claude/plans/[name].md`

---

## Progressive Disclosure

Entry (this file) → [README.md](README.md) onboarding → [guidelines/](guidelines/) quick ref → [docs/](docs/) deep dive

---

**Version**: 2.1 | **Update**: 2026-05 | **Status**: Production

# AI Agent Rules

Claude Code guidelines.

---

## Workflow

```
Checklist → Plan → Mode → Implementation
```

1. **Checklist**: Review similar implementations, stack, blockers
2. **Plan**: Concise sequence (mandatory pre-code)
3. **Mode**: Senior (fast)
4. **Implementation**: Pattern reuse, testing when relevant

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

**Version**: 2.0 | **Update**: 2026-01 | **Status**: Production

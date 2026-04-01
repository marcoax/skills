# marcoax/skills

Collection of reusable skills for coding agents, organized under [`skills/`](./skills). This repository includes general-purpose skills, review/TDD workflow skills, and a few skills tailored to specific stacks or projects.

## Installation

The recommended way to install these skills from GitHub is to use the official Vercel Labs `skills` CLI, with no manual setup required.

```bash
# List the skills available in this repository
npx skills@latest add marcoax/skills --list

# Install a specific skill
npx skills@latest add marcoax/skills --skill tdd

# Install multiple skills
npx skills@latest add marcoax/skills --skill grill-me --skill write-a-prd

# Install all skills from the repository
npx skills@latest add marcoax/skills --skill '*'

# Install for a specific agent
npx skills@latest add marcoax/skills --skill tdd --agent codex

# Install globally
npx skills@latest add marcoax/skills --skill tdd --agent codex --global
```

Useful notes:

- `marcoax/skills` is the GitHub shorthand for this repository.
- `--list` shows detected skills without installing them.
- `--skill '*'` installs every skill found in the repository.
- `--agent` lets you target a specific client, such as `codex` or `claude-code`.
- If you prefer an interactive flow, you can omit some flags and let the CLI guide you.

## Repository structure

```text
skills/   main skills collection
cli/      dedicated Node.js CLI for the repository
REPORT.md internal supporting documentation
```

The `cli/` directory is not required to install skills with `npx skills@latest`: the official tool reads the GitHub repository directly and discovers the skills available under `skills/`.

## Available skills

| Skill | Path | Description |
| --- | --- | --- |
| `agent-md-creator` | `skills/agent-md-creator` | Generates standardized `AGENT.md` or `CLAUDE.md` files to document a project for AI agents. |
| `autoresearch` | `skills/autoresearch` | Automatically improves an existing skill through repeated eval, scoring, and prompt mutation cycles. |
| `blazor-localization` | `skills/blazor-localization` | Automates localization for Razor/Blazor files, including RESX key generation and string replacement. |
| `code-review` | `skills/code-review` | Runs multi-scope code review in plan mode for files, branches, commits, or uncommitted changes. |
| `current-file-review` | `skills/current-file-review` | Reviews changes in the current file against project guidelines and best practices. |
| `design-an-interface` | `skills/design-an-interface` | Produces multiple radically different interface designs for the same module and compares tradeoffs. |
| `get-api-docs` | `skills/get-api-docs` | Fetches up-to-date documentation for third-party libraries, SDKs, or APIs before implementation. |
| `grill-me` | `skills/grill-me` | Interviews the user aggressively to stress-test plans, designs, and technical decisions. |
| `laracms-code-review` | `skills/laracms-code-review` | Code review skill focused on LaraCMS/Laravel projects and admin architecture guidelines. |
| `optimize-prompt` | `skills/optimize-prompt` | Rewrites a prompt to make it clearer and more effective before execution. |
| `php-tdd-workflow` | `skills/php-tdd-workflow` | Guided PHP/Laravel implementation workflow with task breakdown, TDD, verification, and progress tracking. |
| `planning-with-files` | `skills/planning-with-files` | Implements file-based planning with artifacts such as `task_plan.md`, `progress.md`, and `findings.md`. |
| `prd-to-issues` | `skills/prd-to-issues` | Breaks a PRD into small, independently actionable GitHub issues using vertical slices. |
| `skill-optimizer` | `skills/skill-optimizer` | Guides a structured 5-step diagnostic loop to improve an existing skill. |
| `task-spec-creator` | `skills/task-spec-creator` | Creates a technical task specification markdown file through a structured developer interview. |
| `tdd` | `skills/tdd` | Applies a red-green-refactor workflow with emphasis on behavior-focused tests and vertical slices. |
| `technical-debt-manager-php-laravel` | `skills/technical-debt-manager-php-laravel` | Analyzes technical debt and builds refactoring roadmaps for PHP/Laravel codebases. |
| `write-a-prd` | `skills/write-a-prd` | Builds a PRD through user interview, codebase exploration, and module definition. |

## Compatibility notes

Not every skill is fully generic:

- `blazor-localization` assumes a Blazor workflow with RESX files.
- `laracms-code-review` and `technical-debt-manager-php-laravel` are designed for Laravel/PHP contexts.
- `php-tdd-workflow` is strongly oriented toward PHP/Laravel implementation flows.
- some skills reference external tools or project conventions, so reading the related `SKILL.md` first is recommended before using them in a different environment.

## Local development

If you want to inspect or modify a skill:

1. open its directory under `skills/`
2. read `SKILL.md` first
3. check any subdirectories such as `references/`, `steps/`, `templates/`, `scripts/`, or `assets/`

To quickly verify what the official CLI detects:

```bash
npx skills@latest add marcoax/skills --list
```

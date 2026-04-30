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
README.md repository overview and installation notes
REPORT.md internal supporting documentation
```

The official `skills` CLI reads the GitHub repository directly and discovers the skills available under `skills/`, so no extra local setup is required for installation.

## Available skills

| Skill                                | Path                                        | Description                                                                                                                    |
| ------------------------------------ | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `agent-md-creator`                   | `skills/agent-md-creator`                   | Generates standardized `AGENT.md` or `CLAUDE.md` files to document a project for AI agents.                                    |
| `autoresearch`                       | `skills/autoresearch`                       | Automatically improves an existing skill through repeated eval, scoring, and prompt mutation cycles.                           |
| `blazor-localization`                | `skills/blazor-localization`                | Automates localization for Razor/Blazor files, including RESX key generation and string replacement.                           |
| `code-review`                        | `skills/code-review`                        | Runs multi-scope code review in plan mode for files, branches, commits, or uncommitted changes.                                |
| `current-file-review`                | `skills/current-file-review`                | Reviews changes in the current file against project guidelines and best practices.                                             |
| `design-an-interface`                | `skills/design-an-interface`                | Produces multiple radically different interface designs for the same module and compares tradeoffs.                            |
| `eracms-admin-module`                | `skills/eracms-admin-module`                | Creates a config-driven CRUD module for the eraCms admin panel.                                                                |
| `grill-me`                           | `skills/grill-me`                           | Interviews the user aggressively to stress-test plans, designs, and technical decisions.                                       |
| `improve-codebase-architecture`      | `skills/improve-codebase-architecture`      | Explores a codebase to identify architecture and testability improvements.                                                     |
| `laracms-code-review`                | `skills/laracms-code-review`                | Code review skill focused on LaraCMS/Laravel projects and admin architecture guidelines.                                       |
| `optimize-prompt`                    | `skills/optimize-prompt`                    | Rewrites prompts to make them more effective for AI agents before execution.                                                   |
| `pessimistic-code-review`            | `skills/pessimistic-code-review`            | Runs adversarial code review using Independent Adversarial Verification (IAV) and returns an evidence-based PASS/FAIL verdict. |
| `php-tdd-workflow`                   | `skills/php-tdd-workflow`                   | Guided PHP/Laravel implementation workflow with task breakdown, TDD, verification, and progress tracking.                      |
| `planning-with-files`                | `skills/planning-with-files`                | Implements file-based planning with task, findings, and progress documents for complex work.                                   |
| `prd-to-issues`                      | `skills/prd-to-issues`                      | Breaks a PRD into small, independently actionable GitHub issues using vertical slices.                                         |
| `prd-to-plan`                        | `skills/prd-to-plan`                        | Turns a PRD into a multi-phase implementation plan using tracer-bullet vertical slices.                                        |
| `react-review`                       | `skills/react-review`                       | Runs React-specific review for hooks, state, rendering, data fetching, and component APIs.                                     |
| `request-refactor-plan`              | `skills/request-refactor-plan`              | Creates an incremental refactor plan through user interview and repository exploration.                                        |
| `skill-optimizer`                    | `skills/skill-optimizer`                    | Improves existing skills through a structured diagnostic and optimization loop.                                                |
| `task-spec-creator`                  | `skills/task-spec-creator`                  | Creates a technical task specification markdown file through a structured developer interview.                                 |
| `tdd`                                | `skills/tdd`                                | Applies a red-green-refactor workflow with emphasis on behavior-focused tests and vertical slices.                             |
| `technical-debt-manager-php-laravel` | `skills/technical-debt-manager-php-laravel` | Analyzes PHP/Laravel technical debt and produces prioritized refactoring guidance.                                             |
| `write-a-prd`                        | `skills/write-a-prd`                        | Builds a PRD through user interview, codebase exploration, and module definition.                                              |
| `write-a-skill`                      | `skills/write-a-skill`                      | Creates new agent skills with structure, progressive disclosure, and bundled resources.                                        |

## Compatibility notes

Not every skill is fully generic:

- `blazor-localization` assumes a Blazor workflow with RESX files.
- `laracms-code-review` is designed for Laravel/PHP contexts.
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

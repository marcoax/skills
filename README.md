# marcoax/skills

Collection of reusable skills for coding agents. This repository contains my own (non third-party) skills, organized by purpose. Third-party skills are kept separately under `third-part/` and are not listed here.

## Installation

The recommended way to install these skills from GitHub is to use the official Vercel Labs `skills` CLI, with no manual setup required.

```bash
# List the skills available in this repository
npx skills@latest add marcoax/skills --list

# Install a specific skill
npx skills@latest add marcoax/skills --skill code-review

# Install multiple skills
npx skills@latest add marcoax/skills --skill react-review --skill task-spec-creator

# Install all skills from the repository
npx skills@latest add marcoax/skills --skill '*'

# Install for a specific agent
npx skills@latest add marcoax/skills --skill code-review --agent codex

# Install globally
npx skills@latest add marcoax/skills --skill code-review --agent codex --global
```

Useful notes:

- `marcoax/skills` is the GitHub shorthand for this repository.
- `--list` shows detected skills without installing them.
- `--skill '*'` installs every skill found in the repository.
- `--agent` lets you target a specific client, such as `codex` or `claude-code`.

## Repository structure

```text
personal/          domain-specific skills (Carimali, MQTT, PHP/Laravel, Blazor)
planning/          planning, spec, triage workflows
review/            code review variants
skill-management/  meta-skills to author and tune other skills
utilities/         general-purpose helpers
third-part/        third-party skills (not listed below)
```

## Available skills

### personal/

| Skill | Path | Description |
| --- | --- | --- |
| `blazor-localization` | `personal/blazor-localization` | Automates localization for Blazor Razor files (Italian string detection, RESX key generation, code substitution). |
| `eracms-admin-module` | `personal/eracms-admin-module` | Creates a config-driven CRUD module for the eraCms admin panel. |
| `laracms-code-review` | `personal/laracms-code-review` | Code review focused on LaraCMS/Laravel admin architecture and best practices. |
| `log-analyzer` | `personal/log-analyzer` | Analyzes Symfony `app.ERROR` log files for the Carimali/caricare project. |
| `log-cleaner-process` | `personal/log-cleaner-process` | Deep-clean a Symfony log keeping only "Process already in progress" error blocks, filtered by serial number. |
| `log-cleaner-process-context` | `personal/log-cleaner-process-context` | Cleans a log keeping process-error lines + context lines and generates an HTML report of pre-error commands. |
| `message-log-analizer` | `personal/message-log-analizer` | Analyzes Carimali MQTT message logs and generates Packet-received traffic trend reports. |
| `mqtt-decode` | `personal/mqtt-decode` | Decodes a raw Carimali MQTT binary payload (hex string) into a human-readable annotated table. |
| `mqtt-error-fixer` | `personal/mqtt-error-fixer` | Analyzes MQTT pipeline errors from CariSupport and proposes surgical fixes. |
| `mqtt-payload` | `personal/mqtt-payload` | Generates MQTT binary payloads (hex strings) for the Carimali coffee machine protocol. |
| `php-tdd-workflow` | `personal/php-tdd-workflow` | Structured PHP/Laravel implementation workflow with task breakdown, TDD, verification, and progress tracking. |
| `process-error-context-cleaner` | `personal/process-error-context-cleaner` | Lighter alternative to `log-cleaner-process`: keeps only process-error lines plus 3 lines of context. |
| `recipe-analizer` | `personal/recipe-analizer` | Analyzes machine recipes by sub-product type and generates attribute frequency statistics (HTML/MD/CSV). |
| `technical-debt-manager-php-laravel` | `personal/technical-debt-manager-php-laravel` | Technical debt analyst for PHP/Laravel: code health, maintainability, refactoring planning. |

### planning/

| Skill | Path | Description |
| --- | --- | --- |
| `planning-with-files` | `planning/planning-with-files` | Manus-style file-based planning (`task_plan.md`, `findings.md`, `progress.md`) for complex multi-step work. |
| `prd-to-plan` | `planning/prd-to-plan` | Turns a PRD into a multi-phase implementation plan using tracer-bullet vertical slices. |
| `task-spec-creator` | `planning/task-spec-creator` | Generates a structured `TASK_SPEC.md` for a single implementation task through developer interview. |
| `triage-issue` | `planning/triage-issue` | Triages a bug by exploring the codebase to find root cause, then creates a GitHub issue with a TDD-based fix plan. |

### review/

| Skill | Path | Description |
| --- | --- | --- |
| `code-review` | `review/code-review` | Multi-scope code review in plan mode (file, branch diff, commit, uncommitted). |
| `goal-spec-review` | `review/goal-spec-review` | Pre-flight review of an implementation spec/plan for unclear, contradictory, or missing points before `/goal` execution. |
| `pessimistic-code-review` | `review/pessimistic-code-review` | Adversarial code review using Independent Adversarial Verification (IAV); returns evidence-based PASS/FAIL. |
| `react-review` | `review/react-review` | React 18/19 specific review: hooks, state, rendering, data fetching, component APIs. |

### skill-management/

| Skill | Path | Description |
| --- | --- | --- |
| `autoresearch` | `skill-management/autoresearch` | Autonomously optimizes a skill through repeated evals, scoring, and prompt mutations. |
| `find-skills` | `skill-management/find-skills` | Helps users discover and install agent skills based on what they want to do. |
| `skill-creator` | `skill-management/skill-creator` | Creates and improves skills; runs benchmarks and variance analysis on description triggering. |
| `skill-optimizer` | `skill-management/skill-optimizer` | Improves an existing skill through a guided, interactive diagnostic loop with checkpoints. |

### utilities/

| Skill | Path | Description |
| --- | --- | --- |
| `agent-md-creator` | `utilities/agent-md-creator` | Generates standardized `CLAUDE.md` / `AGENT.md` files to document a project for AI agents. |
| `optimize-prompt` | `utilities/optimize-prompt` | Rewrites prompts to make them more effective for AI agents before execution. |

## Compatibility notes

Several skills under `personal/` are tied to specific stacks or projects (Carimali coffee machines, Symfony, PHP/Laravel, LaraCMS, Blazor) and may not be useful outside those contexts. Always read the related `SKILL.md` before adopting one in a different environment.

## Local development

To inspect or modify a skill:

1. open its directory (e.g. `personal/mqtt-decode/`)
2. read `SKILL.md` first
3. check any subdirectories such as `references/`, `steps/`, `templates/`, `scripts/`, or `assets/`

To verify what the official CLI detects:

```bash
npx skills@latest add marcoax/skills --list
```

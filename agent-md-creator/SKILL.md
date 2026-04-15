---
name: agent-md-creator
description: Generate standardized CLAUDE.md or AGENT.md files for projects. Use when users want to document a project for AI agents, set up project instructions, create AI instructions files, initialize agent docs, or say things like "Crea un CLAUDE.md", "Generate AGENT.md", "Setup project documentation", "document this project for agents", "create AI instructions file", "initialize agent docs", "set up project instructions".
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
---

# Agent MD Creator

Generate a single self-contained `CLAUDE.md` / `AGENT.md` file: auto-detected stack, Karpathy guidelines, nothing more.

## Rule

> All interactive prompts (Steps 1, 2, 4, 5) MUST use the `AskUserQuestion` tool.

---

## Workflow

### Step 1 — File type

Ask: **"CLAUDE.md or AGENT.md?"**

---

### Step 2 — Technical reference documents

Ask: **"Are there existing technical documents or guidelines to extract info from? (e.g. README.md, TECHNICAL_REFERENCE.md, docs/architecture.md — relative paths separated by comma, or skip)"**

Behavior:
- If paths provided → `Read` each file in full; extract stack, exact versions, conventions, and project description to use in the following steps.
- If a document is ambiguous or conflicts with another → report the conflict explicitly, do not resolve it silently.
- If extracted info includes a project description → skip Step 4 automatically.
- If skip → proceed with config file scan only (Step 3).

---

### Step 3 — Config file scan

Search the CWD for these files to detect the tech stack:

| File | Stack |
|------|-------|
| `package.json` | Node.js / JS |
| `composer.json` | PHP |
| `requirements.txt` / `pyproject.toml` / `setup.py` | Python |
| `pom.xml` / `build.gradle` | Java |
| `Gemfile` | Ruby |
| `*.csproj` / `*.sln` | .NET |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Dockerfile` / `docker-compose.yml` | Docker |
| `.github/workflows/*.yml` | CI/CD |

⚠️ **Exact versions are mandatory.** Version precedence: config files win over Step 2 docs (config files are always current; docs may lag).

**If no stack is detected** (no config files, no Step 2 docs): try reading `README.md` automatically. If README yields no stack info → ask the user to describe it.

**Mixed-stack projects** (e.g. Python backend + Node.js frontend): always use the category structure (`Frontend` / `Backend` / `Database` / `Other tools`). Always one file — no splitting. If the project is complex, add a `## References` section (see Step 6).

---

### Step 4 — Project details (optional, skip if description already extracted in Step 2)

Ask in a single message:

```
Would you like to add project details? Fill in what you need, skip the rest:

1. Short description (1–3 lines)
2. Key artifacts / main folders
3. Primary languages (if not auto-detected)

Reply with numbers and content, or "skip".
```

If skip → the `## Project` section is generated from the folder name + auto-detected stack only.

---

### Step 5 — Commands (optional)

Ask: **"Provide test, build, and dev server commands (or skip):"**

Expected format:
```
Test: npm test
Build: npm run build
Dev: npm run dev
```

If provided → included as a `## Commands` section inside the main file.
If skip → section omitted.

---

### Step 6 — Generate file

**Before writing**: check if the file already exists in the CWD.
- If it exists → ask: **"File already exists. Overwrite? (yes/no)"**
  - Yes → overwrite.
  - No → stop: **"File already exists, not modified."**

Create the file chosen in Step 1 in the CWD, using this structure:

```markdown
# {{CLAUDE|AGENT}}.md — {{project_folder_name}}

## Project

{{description from Step 4, or: "{{folder_name}}: {{main stack}} project."}}
Key artifacts: {{...}}.
Languages: {{...}}.

## Technology Stack

- **Frontend**: {{framework, UI libs, state mgmt — omit if not present}}
- **Backend**: {{language, framework, API}}
- **Database**: {{db, ORM — omit if not present}}
- **Other tools**: {{deploy, test, pkg manager}}

## Commands  ← include only if Step 5 was filled in

- Test: `...`
- Build: `...`
- Dev: `...`

---

## Development Guidelines (Karpathy)

### 1. Think Before Coding

- Declare assumptions explicitly before writing code.
- If multiple interpretations exist, present them all — do not silently pick one.
- If something is unclear, stop and ask. Do not guess.

### 2. Simplicity First

- Minimum code that solves the problem, nothing more.
- Zero unrequested features, zero abstractions for one-time-use code.
- No speculative configurability, no error handling for impossible scenarios.
- Self-check: "would a senior say this is over-engineered?" — if yes, simplify.

### 3. Surgical Changes

- Modify only what is needed for the current request.
- Do not improve adjacent code, unrelated comments, or formatting.
- Preserve the existing file style, even if you would do it differently.
- Unrelated dead code: flag it, do not delete it.
- Remove orphan imports/variables **only** if made orphan by the current changes.

### 4. Goal-Driven Execution

Turn every task into a verifiable criterion **before** starting:

| Request | Success criterion |
|---------|-------------------|
| "Add validation" | Write tests for invalid inputs, then make them pass |
| "Fix the bug" | Write a test that reproduces the bug, then make it pass |
| "Refactor X" | Tests pass both before and after |

For multi-step tasks, declare a short plan (steps + verification) before coding.

---

> These rules take precedence over implicit conventions inferred from the code.
> In case of conflict with other preferences, ask the user explicitly.
```

Formatting rules:
- Omit empty Technology Stack categories (no lines like "- **Frontend**: —").
- `## Commands` section only if provided in Step 5.
- `## References` section only if Step 2 docs were provided — list them as links.
- No collateral files (`COMMANDS.md`, `STACK.md`, `guidelines/`).

---

### Step 7 — Confirm

Final message: **"File created: `{{name}}` in `{{CWD}}`"**

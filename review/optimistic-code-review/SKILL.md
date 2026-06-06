---
name: optimistic-code-review
description: >
  Constructive, generic code review tool — the optimistic counterpart to pessimistic-code-review.
  Surfaces issues with WHY + HOW, acknowledges what is done well, and proposes fixes you approve before they are applied.
  Supports multiple scopes: current file, branch diff, specific commit, uncommitted changes.
  Triggers: "review", "code review", "revisiona", "controlla modifiche", "check this file", "review branch", "review commit".
  Operates in PLAN MODE - proposes improvements, waits for approval before executing.
  Do NOT use when a stack-specific or specialized review skill fits better:
  use react-review for React 18/19 SPA projects (.tsx/.jsx files, React dependency, hooks/JSX/components review);
  use laracms-code-review for LaraCMS or Laravel admin projects (presence of guidelines/ADMIN_ARCHITECTURE.md, Laravel structure);
  use pessimistic-code-review when the user wants an adversarial PASS/FAIL verdict rather than constructive suggestions
  ("pessimistic review", "strict review", "is this really done", "verify this is complete").
---

# Optimistic Code Review

Constructive, multi-scope code review — the optimistic counterpart to `pessimistic-code-review`:
it proposes concrete improvements and highlights strengths rather than issuing a PASS/FAIL verdict.
Operates in **plan mode**: proposes, does not execute.

> **Language rule**: detect the language of the user's input and respond entirely in that language — including section headers, explanations, questions, **the fix menu, the per-fix "apply?" prompt, and the final Codex offer**. All user-facing snippets in the steps below are **English templates to render in the user's language**, not literal text. Never switch languages mid-conversation.

## Step 0: Interactive Scope Selection

Show the scope menu UNLESS the user's input already specifies a scope. Use the table below to decide:

| User input matches | Detected scope | Still ask for |
|---|---|---|
| `file <path>` / `check this file <path>` / `check file <path>` | Scope 1 – Current file | path (if not in input) |
| `branch` / `branch diff` / `review branch` | Scope 2 – Branch diff | base branch — **always ask explicitly**: do NOT infer from git remote — user may be on a hotfix/release branch where the default would be wrong |
| `commit <hash>` / `review commit <hash>` (hash provided) | Scope 3 – Specific commit | nothing |
| `commit` / `review commit` (no hash) | Scope 3 – Specific commit | "Which commit? (provide hash or type 'last')" |
| `changes` / `uncommitted` / `controlla modifiche` / `modifiche` | Scope 4 – Uncommitted | nothing |

If the input does **not** match any row above, show this menu and wait for the user to pick:

```
## 🔍 Code Review — Select scope

1. 📄 **Current file** — Review a specific file
2. 🌿 **Branch diff** — Compare current branch vs base
3. 📌 **Specific commit** — Review a specific commit
4. 📝 **Uncommitted changes** — All modified, uncommitted files

Scope? (1/2/3/4)
```

### Parameter collection by scope

**Scope 1 — Current file**: ask for path if not provided.

**Scope 2 — Branch diff**: always ask for base branch explicitly; run `git rev-parse --abbrev-ref HEAD` to show current branch. **Never infer from git remote** — the user may be on a hotfix or release branch where `origin/main` would produce a wrong diff.

**Scope 3 — Specific commit**: if hash not provided, run `git log --oneline -5` to show recent commits and ask which one.

**Scope 4 — Uncommitted changes**: no additional parameters needed.

**Output format** (ask for ALL scopes — collect this before exiting plan mode):
```
Output format: (1) 💬 Inline chat  (2) 📄 Markdown file report  ?
```
Wait for the answer. Store the choice as `[FORMAT]`. Do not proceed until answered.

## ⚠️ Plan Mode Gate — Call ExitPlanMode now

Step 0 is complete (scope + format confirmed). Call `ExitPlanMode` before running any git command.
All steps below require live git output — plan mode produces empty diffs.

## Step 1: Gather Context

### Precondition — confirm this is a git repository
```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NOT_A_GIT_REPO"
```
If the output is `NOT_A_GIT_REPO`: stop the git-based flow and tell the user no git repository was found.
For **Scope 1 (current file)** offer to review the file as plain "new code" (no diff); for the other scopes,
ask the user to run the review from inside a git repository. Never run the diff commands below blindly.

### Project best practices
```bash
cat CLAUDE.md 2>/dev/null || cat AGENT.md 2>/dev/null || echo "No project guidelines found"
```

### Diff by scope

```bash
# Scope 1: Current file
git diff HEAD -- <filepath>
# If no diff, show last change:
git diff HEAD~1 -- <filepath>

# Scope 2: Branch diff
# ⛔ STOP: <base-branch> = exactly what the user typed in Step 0. Never substitute origin/HEAD, main, master, or any inferred value.
git diff <base-branch>..HEAD --stat        # overview
git diff <base-branch>..HEAD               # full diff
git diff <base-branch>..HEAD --name-only   # file list

# Scope 3: Specific commit
git show <commit-hash> --stat              # overview
git show <commit-hash>                     # full diff

# Scope 4: Uncommitted changes
git status --short                         # overview
git diff                                   # unstaged changes
git diff --cached                          # staged changes
```

**Scope 2 — large diffs**: if the diff contains **≥10 files**, show the `--stat` overview first and ask:
> "This diff spans N files. Review all at once or file by file?"
Wait for the answer before proceeding.

## Step 2: Review Checklist

Analyze the code against this checklist, adapted to the detected language/framework:

### 🔴 CRITICAL
- **Security**: injection risks, XSS, missing authentication/authorization
- **Data corruption**: race conditions, unmanaged transactions, data loss

### 🟠 HIGH
- **Potential bugs**: broken functionality, wrong logic, unhandled edge cases
- **Performance**: N+1 queries, unnecessary loops, needless re-renders, memory leaks
- **Error handling**: unhandled exceptions, missing validation

### 🟡 MEDIUM
- **Architecture**: tight coupling, SOLID violations, separation of concerns
- **Code quality**: duplication, magic values, unclear naming
- **Type safety**: missing types, null handling, `any` abuse (TypeScript)

### 🟢 LOW
- **Style**: formatting, minor conventions, light optimizations
- **Accessibility**: ARIA, keyboard nav, semantic HTML (UI code only)
- **Testing**: missing coverage, fragile tests

Output the review using the template below, in the format chosen in Step 0.
**Always include all 4 severity sections** — if a section has 0 issues, write `_None found._` instead of omitting the section.
**The ✅ Positives section is mandatory too** — never omit it and never leave it empty: list at least one genuine strength of the code (sound choices, good tests, clear naming). This is the defining trait of an *optimistic* review.

### Review template

```markdown
## 🔍 Review: [scope description]

**Scope**: [file/branch/commit]
**Files analyzed**: [N files, M lines changed]
**Branch**: [current] vs [base] (scope 2 only)

---

### 🔴 Critical [N]
1. **[File:Line]** — [issue title]
   - **WHY**: [impact explanation]
   - **HOW**: [suggested fix with code]

### 🟠 High [N]
1. **[File:Line]** — [issue title]
   - **WHY**: [explanation]
   - **HOW**: [suggested fix]

### 🟡 Medium [N]
1. **[File:Line]** — [issue title]
   - **WHY**: [explanation]
   - **HOW**: [suggested fix]

### 🟢 Low [N]
1. **[File:Line]** — [issue title]
   - **HOW**: [suggestion]

### ✅ Positives [≥1, required]
- [what is done well and why]

### 🧪 Suggested tests
[Only if logic is not covered by existing tests]
1. [Description] → [what it verifies]

---

### 📊 Summary
| Severity | Count |
|----------|-------|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🟢 Low | N |

**Overall score**: [A/B/C/D/F] — evaluate the rules **top-down and assign the first match** (so they never overlap):
- **F**: ≥2 critical
- **D**: exactly 1 critical (regardless of high/medium)
- **C**: 0 critical AND (≥4 high OR ≥3 medium)
- **B**: 0 critical AND 1–3 high AND ≤2 medium
- **A**: 0 critical AND 0 high AND ≤2 medium

🟢 Low issues never change the grade. Always state the grade together with the counts table above so the verdict is reproducible.

---
How do you want to proceed with the fixes?
(1) 🔁 One by one — I propose each fix with an explanation, you decide apply/skip
(2) ✅ All at once — I apply everything in one go
(3) 🔢 Select — tell me the numbers (e.g. "1,3")
(4) ⏭️ None — review only, no changes
```

## Step 3: Wait for Approval

**Do not execute anything** without an explicit answer:
- `"1"` / `"uno alla volta"` / `"one by one"` → enter interactive mode (Step 4A)
- `"2"` / `"ok"` / `"yes"` / `"all"` / `"tutti"` → apply all fixes at once (Step 4B)
- `"3"` / `"1, 3"` / `"only 1"` → apply selected fixes (Step 4B)
- `"+tests"` / `"with tests"` → apply all + generate tests
- `"4"` / `"no"` / `"skip"` / `"nessuno"` → do not apply
- `"only critical"` / `"only 🔴🟠"` → apply only that severity

## Step 4A: Interactive One-by-One Mode

For each fix, in order of severity (🔴 → 🟠 → 🟡 → 🟢):

1. Show the fix as:
```
### Fix #N — [severity emoji] [severity]: [title]

**WHY**: [1-2 sentence impact explanation]

**Change** in `file:line`:
\`\`\`
// BEFORE
[old code]

// AFTER
[new code]
\`\`\`

Apply? (`yes` / `skip`)
```
2. Wait for the user to reply before moving to the next fix.
3. `"sì"` / `"yes"` / `"ok"` / `"s"` → apply the fix, confirm with a brief note, then show the next fix
4. `"skip"` / `"no"` / `"n"` → skip without applying, then show the next fix
5. After all fixes: show a final summary table of applied/skipped fixes

## Step 4B: Execute Approved Changes (bulk)

1. Apply approved changes one after another without pausing
2. After all changes: show a final summary table of applied/skipped fixes
3. If a fix requires choices (e.g. naming), ask before proceeding

## Step 5: Generate Tests (if requested)

If approved with `+tests`:
1. Identify the project's test framework (from CLAUDE.md or folder structure)
2. Generate tests for the modified logic
3. Place in the correct path (e.g. `tests/`, `__tests__/`, `*.test.ts`)
4. Propose tests in plan mode → wait for confirmation before creating files

## Step 6: Offer a Codex deep review

**Availability guard**: only offer this if the `codex:review` skill is actually available in the current
environment (check the available-skills list). If it is **not** available, skip Step 6 entirely and just
end with a short summary — never invoke a skill that does not exist.

When available, after all fixes (and any tests), **always** show this prompt (rendered in the user's language):

---
> Do you want to run a deeper review with **Codex**?
> Reply `yes` to launch `/codex:review`, or `no` to finish.
---

- `yes` / `sì` / `s` / `ok` → invoke the `Skill` tool with `skill: "codex:review"`
- `no` / `skip` / `nessuno` / `n` → finish without further action

> **Note**: when Codex is available, Step 6 must be shown in **every exit scenario** — fixes applied, fixes skipped (option 4), or after tests.

## Rules

- **Never execute without approval**
- If no CLAUDE.md → note it, proceed with general best practices for the language
- If no diff (scope 1) → analyze the whole file as "new code"
- Keep suggestions concise; always cite file and specific line
- For each issue: explain WHY (impact) and HOW (concrete fix)
- **Always** acknowledge what is done well — the ✅ Positives section is required and must list ≥1 genuine strength
- **Tests**: propose only if logic is not covered; respect existing framework
- Adapt the checklist to the language/framework (e.g. React → re-renders, Laravel → N+1, Blazor → dispose pattern)
- **Language**: respond in the same language as the user's input

# personal/

Skills tied to my own stack or projects. Not listed in the top-level README.

Skills in `deprecated/` are kept for reference but no longer in use.

## Sync from project repositories

Run `node scripts/sync-personal-skills.mjs` with Node.js and Git. The script reads the default branches of `newEra`, `BlazorWCSWebUI_v8`, and `teach-english`. For each repo, enter the numbers of the skills to sync or press Enter to skip. Nothing is written until you confirm the summary. Skills found in the default branch's history but no longer available are listed separately; their local copies are never deleted automatically.

Selected folders replace `personal/<skill>/` in full, or `personal/teach-english/<skill>/` for skills from `teach-english`. The script refuses to overwrite local changes or untracked files. When a repo has the same skill in multiple locations, `.agents/skills` takes precedence, then `.claude/skills`, then `.vibe/skills`. Review the result with `git status` and `git diff`; the script regenerates the plugin manifest but does not commit.

| Skill | Description |
|-------|-------------|
| [add-lesson](teach-english/add-lesson/SKILL.md) | Turns English lesson notes into a quiz for teach-english. |
| [add-recap](teach-english/add-recap/SKILL.md) | Builds a review quiz from existing teach-english lessons. |
| [blazor-localization](blazor-localization/SKILL.md) | Automates localization for Blazor Razor files (AF project). |
| [eracms-admin-module](eracms-admin-module/SKILL.md) | Creates a config-driven CRUD module for the eraCms admin panel. |
| [md-to-blog-html](md-to-blog-html/SKILL.md) | Converts a Markdown article to the HTML format used by the Magutti blog. |
| [php-tdd-workflow](php-tdd-workflow/SKILL.md) | Structured PHP/Laravel implementation workflow with TDD. |
| [technical-debt-manager-php-laravel](technical-debt-manager-php-laravel/SKILL.md) | Technical debt analyst for PHP/Laravel: code health, maintainability, refactoring planning. |

# CLAUDE.md — marcoax/skills

## Repository structure

Skills are organized into bucket folders:

```
personal/          tied to my own stack/projects, not promoted
planning/          planning, spec, triage workflows
review/            code review variants
skill-management/  meta-skills to author and tune other skills
utilities/         general-purpose helpers
third-part/        third-party skills (not maintained here)
```

Inside `personal/`:

```
personal/deprecated/   skills no longer in use
```

## Rules

- Skills in `planning/`, `review/`, `skill-management/`, and `utilities/` must have an entry in the top-level `README.md`.
- Skills in `personal/` and `personal/deprecated/` must **not** appear in `README.md`.
- Skills in `third-part/` must **not** appear in `README.md`.

## README maintenance

> **When you add, rename, or remove a skill, update `README.md` accordingly.**
> **When you add, rename, or remove a skill, regenerate the manifest by running
> `node scripts/generate-plugin.mjs` and commit `.claude-plugin/plugin.json`**

Each entry in `README.md` must include the skill path and a one-line description.

## Skill structure

Each skill lives in its own folder and must contain a `SKILL.md` at minimum.

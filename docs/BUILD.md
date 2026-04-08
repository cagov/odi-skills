# Builder guide

How to design, build, and ship skills in this repo.

**Other docs:** Setup (venv, npm, linters) is in [MAINTAINER.md](MAINTAINER.md). Packager flags are in [PACKAGE-SKILL.md](PACKAGE-SKILL.md). Tags and releases are in [RELEASE.md](RELEASE.md).

---

## Project layout

```
odi-skills/
├── docs/                    # Docs map (README.md), RELEASE.md, PACKAGE-SKILL.md, …
├── dist/                    # Default output for packaged .skill files
├── releases/                # Published .skill files (tracked in git)
├── src/                     # One folder per skill (kebab-case)
│   └── odi-plain-language/  # Example skill
├── scripts/
│   └── package_skill.py     # Packager
├── Makefile
├── package.json             # npm scripts
└── README.md
```

Each skill gets its own folder under `src/`.

---

## What is a skill?

A skill is a set of instructions that Claude follows. At minimum, it needs a `SKILL.md` file with YAML frontmatter and a body.

You can also add `references/`, `scripts/`, `assets/`, local `docs/` for diagrams, and `tests/` for fixtures. The packager does not ship `docs/` or `tests/` (see [PACKAGE-SKILL.md](PACKAGE-SKILL.md)).

---

## Skill folder structure

```
your-skill-name/
├── SKILL.md                 # Required entry point (frontmatter + body)
├── references/              # Loaded on demand (modes, formats, deep docs)
├── scripts/                 # Helpers (scoring, transforms)
├── assets/                  # Templates, icons
├── docs/                    # Authoring/diagrams (not shipped)
├── tests/                   # Fixtures/evals (not shipped)
├── CHANGELOG.md             # Recommended
└── RELEASE-NOTES.md         # Optional human summary per release
```

Keep `SKILL.md` lean. Put detail in `references/` with a clear load order in the body.

---

## How to create a new skill

### 1. Define the scope

Spell out what the skill does, when it should trigger, expected output shape, and which reference files it needs.

### 2. Create the folder

Add a folder under `src/` in lowercase kebab-case. The folder name must match the `name` field in `SKILL.md`.

### 3. Write SKILL.md

- **Frontmatter:** Add `name` and `description` (both required). Write the description so it triggers well.
- **Body:** Add the load order, reference table, and workflow steps. Use [odi-plain-language](../src/odi-plain-language/SKILL.md) as a model.

### 4. Add references

- Use one file per topic when you can.
- Add a table of contents if a file grows past about 300 lines.
- Use subfolders like `references/modes/` or `references/formats/` as needed.

### 5. Add scripts (optional)

Put scoring, transforms, and formatting checks here. Reference the paths from `SKILL.md` so Claude knows when to run them.

Scripts can be in any language the Claude runtime supports: Python, shell, or Node/JavaScript. Ruff lints Python scripts. Biome lints JavaScript and JSON. If you add a language not covered by either linter, note that in your skill docs so reviewers know what to check by hand.

### 6. Add tests and evals (optional)

Use `tests/` for fixtures and eval material. The packager does not include top-level `tests/` in the `.skill`. If you use a different layout (like JSON eval suites), keep them out of paths that ship. Or document your own setup.

### 7. Iterate

Run Claude against real prompts. Tighten `SKILL.md` and references until the behavior is stable.

---

## Packaging (overview)

The packager produces a `.skill` file (a zip) for sharing. Full details are in [PACKAGE-SKILL.md](PACKAGE-SKILL.md).

Quick options:

- From repo root: `python3 scripts/package_skill.py your-skill-name` (add flags as needed).
- From inside a skill folder: use `npm run skill` or `npm run skill:release` (see root `package.json`).

CLI flags live in PACKAGE-SKILL.md only. They are not repeated here.

---

## Writing guidelines

- **Show detail step by step:** frontmatter → `SKILL.md` body → `references/`.
- **Use commands** for instructions ("Load X, then…").
- **Explain why** a rule matters when it helps people follow it.
- **Write the description field** to trigger well. Lean toward being slightly broad.

---

## Conventions

| Topic | Rule |
|---|---|
| Skill folder name | Lowercase kebab-case. Must match `name` in frontmatter |
| Changelog | Update `CHANGELOG.md` for meaningful changes |
| Linting | See [MAINTAINER.md](MAINTAINER.md). Run Biome (`npm run check:ci`) and Ruff in a venv (`npm run lint:python`) |

---

## Common pitfalls

- **Bloated SKILL.md.** Move detail to `references/`.
- **Vague description.** Weak descriptions mean weak triggers.
- **Missing load order.** Claude will guess wrong without one.
- **No evals.** Add early prompts you can re-run after edits.
- **Forgetting to package.** Users need a `.skill` file, not a raw folder.

---

## Quick reference

| Task | Where |
|---|---|
| Setup for maintainers | [MAINTAINER.md](MAINTAINER.md) |
| Example skill | `src/odi-plain-language/` |
| Packager CLI | [PACKAGE-SKILL.md](PACKAGE-SKILL.md) |
| End users | [USE-SKILLS.md](USE-SKILLS.md) |
| Tags and releases | [RELEASE.md](RELEASE.md) |
# Release and tagging strategy

## Overview

This repo stores multiple skills under `src/`. Each skill has its own folder. Each skill gets developed and released on its own in `releases/`.
The strategy is lightweight. Contributors don't need to coordinate releases across skills. Someone who wants a skill can grab it without cloning the whole repo history.

---

## Folder structure

```
/
├── Makefile
├── docs/
│   └── RELEASE.md       ← this document
├── releases/            ← built .skill files, ready to download
├── src/
│   ├── skill-name-a/    ← source for skill A
│   └── skill-name-b/    ← source for skill B
└── ...
```

Source lives in **`src/<skill-name>/`** folders. Built files live in `releases/`. The `main` branch is always the source of truth.

---

## Tagging convention

Tags are grouped by skill using a `/` separator:

```
{skill-name}/{major}.{minor}
{skill-name}/{major}.{minor}-{label}
```

Examples:
```
odi-plain-language/1.0
odi-plain-language/2.0-draft
odi-plain-language/2.0-stable
odi-demo-02/1.0
odi-demo-02/1.1-name-2026-04
```

### Rules
- No `v` prefix. Version numbers are just numbers.
- Bump major for breaking changes. These include rewritten prompts, new tracks, or structural changes.
- Bump minor for smaller but meaningful updates.
- Small fixes and tweaks don't need a new tag. Update main and rebuild the release file.
- Use the skill's folder name as the tag prefix, exactly as written.
- Labels are optional. Only add them when they add useful context (see below).

List all versions of a skill:
```bash
git tag -l "odi-plain-language/*"
```

### Labels

Labels come after a `-` and are freeform. Use them when they add signal. Skip them when the release is straightforward.

| Label style | Example | Use when |
|---|---|---|
| Status | `2.0-draft`, `2.0-stable` | Signaling readiness |
| Date | `1.1-2026-04` | Freshness matters |
| Author | `1.1-name` | Ownership is relevant |
| Combined | `1.1-name-2026-04` | You want full context |

**No label means stable and ready to use.** Only add a label when the release is not ready, or when extra context helps.

---

## Releases folder

Every time you tag a skill, add a built `.skill` file to `releases/.` The packager names the file from the `name:` field in `SKILL.md` frontmatter (for example, `odi-plain-language.skill`). [Semver](https://semver.org/) and labels live in git tags, not in the filename. This way you keep one file name per skill while history stays in tags.

Example layout:

```
releases/
├── odi-plain-language.skill
└── odi-demo-02.skill
```

Older builds may stay in `releases/` for reference. If someone needs a specific version, they can use the matching git tag.

Most people only ever need to visit `releases/`. No git knowledge needed.

**Git:** `.skill` files are tracked like any other source file. They are not gitignored. Use normal `git add` and `git commit` when you publish a build under `releases/`.

---

## Release checklist

When you're ready to release a new version of a skill:

1. Merge your changes to `main`.
2. **Package** the skill. See [PACKAGE-SKILL.md](PACKAGE-SKILL.md). 

*From the skill folder:* under `src/`, run `npm run skill:release`. It walks you through copying into `releases/` and removing only that skill's outputs from `dist/` (other skills' builds in `dist/` are left alone). 

*From the repo root:* `python3 scripts/package_skill.py {skill-name}` or `src/{skill-name}` Drop --no-prompt if you want the same prompts.

3. **Check** the `.skill` Spot-check it by hand or use your eval harness. There is no single `make test` for all skills yet. Use project-specific tests if they exist.
4. If you did not use the packager’s copy step, copy the built `<name>.skill` into `releases/`. Use the same name the packager would, based on `name` in `SKILL.md`).
5. Commit the new release file on `main`.
6. Tag: `git tag '{skill-name}/{major}.{minor}'`. Add a `-label` suffix if needed (for example `1.2-draft`).
7. Push: `git push origin '{skill-name}/{major}.{minor}'`.

---

## Versioning philosophy

We use semver (`major.minor`) with optional plain-text labels. No `v` prefix. Version numbers are just numbers.

- **Major** bumps when the skill's behavior changes in a breaking or big way.
- **Minor** bumps for meaningful but non-breaking updates.
- **Labels** are optional. Only add them when they help (for example, `-draft` to signal not ready, or `-name-2026-04` when authorship or date matters).
- No label means stable and ready to use.

`releases/` always contains the latest build of each skill. Previous versions are available through git history at the same path.

---

## What Goes in a version bump

| Change type | New version? |
|---|---|
| Rewrote prompts or instructions | Yes |
| Added or removed a content track | Yes |
| Fixed a typo or clarified wording | No |
| Updated examples | No |
| Changed folder structure or file names | Yes |
| Tweaked tone or formatting guidance | Use judgment |

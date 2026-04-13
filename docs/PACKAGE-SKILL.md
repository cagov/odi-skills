# Package a skill

This is a reference for `scripts/package_skill.py`. 
* For skill design and folder layout, see [BUILD.md](BUILD.md). 
* For tagging policy, see [RELEASE.md](RELEASE.md).

The packager zips a skill folder into a `.skill` file. The folder must contain `SKILL.md`, `references/`, `scripts/`, and so on. If you run it with prompts on, it can copy the file into `releases/`.

## Quick start

```bash
# From the repo root — pass the skill name or a path
python3 scripts/package_skill.py odi-plain-language
python3 scripts/package_skill.py src/odi-plain-language

# From inside a skill folder
cd src/odi-plain-language
npm run skill          # no prompts; .skill goes to repo dist/ (same as --no-prompt)
npm run skill:release  # prompts you (e.g., copy to releases/)
```

## Ways to run it

### From inside a skill folder

Make sure `SKILL.md` is in your current folder:

```bash
cd src/odi-plain-language
python3 ../../scripts/package_skill.py
```

### From the repo root

Pass the skill folder. It must contain `SKILL.md`:

```bash
python3 scripts/package_skill.py odi-plain-language
python3 scripts/package_skill.py src/other-skill
python3 scripts/package_skill.py path/to/other-skill
```

### Without prompts (CI or scripts)

```bash
python3 scripts/package_skill.py odi-plain-language --no-prompt
```

## What it does

1. Reads the `name` field from YAML frontmatter in the target folder's `SKILL.md`.
2. Builds a temp zip at `dist/<name>.zip`. It then copies the bytes to `<name>.skill` and deletes the zip. By default the `.skill` file goes to `dist/`. Use `-o` to change the path.
3. Asks if you want to copy `<name>.skill` into `releases/`. If you say yes, it copies the file and removes only `dist/<name>.skill` and `dist/<name>.zip` (other skills' files under `dist/` stay). It skips this prompt with `--no-prompt`.
4. Suggests the next git tag for this skill. Tags follow the format `{skill-name}/{major}.{minor}`. See [RELEASE.md](RELEASE.md). With `--no-prompt`, the tag gets a `-draft` label. Without that flag, it suggests a release tag.

## What the package leaves out

The packager skips these top-level folders:

- `docs/` — authoring notes, diagrams, and repo-only files.
- `tests/` — test fixtures and test files.

It packages everything else at the skill root. Folders named `docs` or `tests` inside nested folders still get included. Only top-level ones are skipped.

## Options

| Flag | What it does |
|---|---|
| `skill_folder` | Positional. A path or skill ID. From the repo root, the script tries `cwd/arg`, then `src/arg`, then `arg` at repo root. If you skip this, it uses the current folder if it has `SKILL.md`. |
| `-o`, `--output-dir` | Sets where the `.skill` file goes. Default: `dist/`. The temp zip always builds under `dist/` first. |
| `--no-prompt` | Skips all prompts. Adds a `-draft` label to the tag suggestion. |

## Example output

```
  Packaged 19 files from src/odi-plain-language/
  dist/odi-plain-language.skill

Copy odi-plain-language.skill to releases/? [y/N] y
  → releases/odi-plain-language.skill
  Removed odi-plain-language.skill from dist/ (left other files unchanged)

  Latest tag for this skill: odi-plain-language/1.0
  Suggested next tag:
    odi-plain-language/1.1
  Run: git tag 'odi-plain-language/1.1' && git push origin 'odi-plain-language/1.1'
```

With `--no-prompt`, the tag line looks like this:

```
  Suggested next tag (draft build; omit --no-prompt for release):
    odi-plain-language/1.1-draft
  Run: git tag 'odi-plain-language/1.1-draft' && git push origin 'odi-plain-language/1.1-draft'
```

## Notes

- The repo tracks `*.skill` files. After you copy a build into `releases/` or keep one under `dist/`, add it with `git add`. See [MAINTAINER.md](MAINTAINER.md) and [RELEASE.md](RELEASE.md).
- The script uses only the Python 3 standard library.
- The archive holds only the skill folder's contents. `scripts/package_skill.py` is a maintainer tool. It does not go in the package.
- Top-level `docs/` and `tests/` stay out of the archive.
- The script skips `__pycache__`, `.DS_Store`, and similar files.
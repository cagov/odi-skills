# Documentation map

| If you need… | Read |
|--------------|------|
| Install a `.skill` file and use it in Claude | [USE-SKILLS.md](USE-SKILLS.md) |
| **Maintainer setup** (venv, npm, Ruff, Biome) | [MAINTAINER.md](MAINTAINER.md) |
| Design a skill, folder layout, authoring | [BUILD.md](BUILD.md) |
| Packager CLI, `dist/`, exclusions, tags | [PACKAGE-SKILL.md](PACKAGE-SKILL.md) |
| Versioning, git tags, `releases/`, checklist | [RELEASE.md](RELEASE.md) |

**How the docs fit together**

- **MAINTAINER** — *How to install and run* repo tooling (Python venv + npm). Start here if you touch `scripts/` or releases.
- **BUILD** — *What to write* in a skill; points to packaging docs for shipping.
- **PACKAGE-SKILL** — *Reference* for `package_skill.py` and npm skill scripts.
- **RELEASE** — *Policy* for tags and `releases/`.
- **USE-SKILLS** — End users only.

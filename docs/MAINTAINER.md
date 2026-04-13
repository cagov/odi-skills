# Maintainer guide

This doc is for people who maintain the repo. That includes `scripts/`, packaging, `releases/`, tags, and helping skill builders publish their work. Skill authors who only edit Markdown and `references/` can skip to **What skill builders need** at the end.

## The core build tool

The main build tool is Python (`scripts/package_skill.py`). It uses only the standard library. Any Python 3.10+ install can package a skill. You do not need Node for CI or one-off builds.

## What Node and npm do

Node and npm play a smaller role. They install Biome, which formats and lints JSON. Biome also covers any JavaScript that skills or tooling may add later. If you already work in npm, you can use `npm run skill` and `npm run skill:release`. These are wrappers that call the same Python packager. They use `INIT_CWD` to pass your skill folder through.

## What skills are

Skills are Markdown and reference files that Anthropic's Claude can run. Neither toolchain runs at skill runtime. Both are development and packaging tools only.

---

## Two toolchains (why both exist)

| Stack | Role | Config |
|--------|------|--------|
| **Node + npm** | Formats and lints JSON (and any JS we add later) | `package.json`, `biome.json` |
| **Python + venv** | Runs Ruff on Python in `scripts/` and `src/*/scripts/` | `pyproject.toml` |

They work on their own. Biome does not read Python. Ruff does not read `package.json`. You install each stack once per clone.

---

## Why use a virtual environment (venv)

macOS and many Linux installs use a system-managed Python ([PEP 668](https://peps.python.org/pep-0668/)). Running `pip` on that Python is blocked or risky. It can break OS tools.

A venv is a small, private Python folder inside the repo (usually `.venv/`). You can run `pip install` safely there. It does not touch system Python. The repo's `.gitignore` already skips `.venv`.

---

## One-time setup (per clone)

### 1. Create the Python venv and install dev tools

From the **repo root**:

```bash
python3 -m venv .venv
```

**Activate** the venv (run this in each new terminal):

```bash
# macOS / Linux
source .venv/bin/activate
```

Your prompt may show `(.venv)`. While active, `python` and `pip` point to the venv, not the system.

Install pinned dev tools:

```bash
pip install -U pip
pip install -e ".[dev]"
```

**What this does:** `pip` reads `pyproject.toml` and installs the `dev` extra. Right now, that means Ruff (version-pinned). It also registers the repo as an editable install. There is no app package to ship. The point is to put `ruff` on your venv's `PATH`. Ruff reads `[tool.ruff]` when you run it from the repo root.

If you do not want editable mode, run `pip install ".[dev]"` instead. It installs the same tools.

To leave the venv (optional):

```bash
deactivate
```

### 2. Install Node tools (Biome)

Still from the repo root:

```bash
npm ci
```

**What this does:** It installs `@biomejs/biome` exactly as recorded in `package-lock.json`, with integrity hashes. Use `npm ci` for clean, repeatable installs in CI and fresh clones. Do not use `npm install` for routine checks.

---

## Day-to-day workflow

1. **Activate the venv** (`source .venv/bin/activate`) so `ruff` is on your `PATH`.
2. Run checks from the repo root:

   ```bash
   npm run check:ci      # Biome — read-only (good for CI)
   npm run lint:python   # Ruff — uses the venv's copy
   ```

3. Auto-fix and format when you want to change files:

   ```bash
   npm run check         # Biome format + lint + organize (writes)
   npm run format:python # Ruff format
   ```

**Note:** `npm run lint:python` runs a shell command that calls `ruff`. That binary must be on your `PATH`. Activate the venv first. If you skip activation, call the binary directly:

```bash
.venv/bin/ruff check scripts src
```

---

## How this ties to releases

Packaging and tagging are in [PACKAGE-SKILL.md](PACKAGE-SKILL.md) and [RELEASE.md](RELEASE.md). The packager is `python3 scripts/package_skill.py`. It uses whichever `python3` is on your `PATH`. If you activate the venv first, it uses the venv's Python. The script only needs the standard library. Any Python 3.10+ works. Running it inside the same venv you use for Ruff avoids "which Python am I using?" confusion.

**Git note:** `*.skill` files are not in `.gitignore`. Add and commit built files (for example, under `releases/`) with normal `git add` / `git commit`. You do not need `git add -f` unless something else excludes that path.

---

## What skill builders need (lighter path)

People who only edit `SKILL.md`, `references/`, and skill content:

- Do not need a venv unless they touch Python under `src/<skill>/scripts/` or `scripts/`.
- Should follow [BUILD.md](BUILD.md) for structure and voice.
- Can rely on maintainers for green checks and packaging before release.

If they do edit Python, they should use the same venv + `pip install -e ".[dev]"` flow. This keeps Ruff in sync with what `pyproject.toml` pins.

---

## Quick reference

| Goal | Command |
|------|---------|
| Create venv | `python3 -m venv .venv` |
| Activate (Unix) | `source .venv/bin/activate` |
| Install Python dev tools | `pip install -e ".[dev]"` |
| Install Node tools | `npm ci` |
| Lint JSON (CI-style) | `npm run check:ci` |
| Lint Python | `npm run lint:python` (venv active) or `.venv/bin/ruff check scripts src` |

**Ruff version source:** `pyproject.toml` → `[project.optional-dependencies] dev`.
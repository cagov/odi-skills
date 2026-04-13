#!/usr/bin/env python3
"""Package a skill folder into a .zip and .skill file.

Usage:
    # From inside a skill folder (contains SKILL.md):
    python scripts/package_skill.py

    # From repo root — skill id resolves under src/ first, then repo root:
    python scripts/package_skill.py odi-plain-language
    python scripts/package_skill.py src/odi-plain-language
    python scripts/package_skill.py path/to/my-skill

    # Skip the interactive copy prompt:
    python scripts/package_skill.py --no-prompt

    # Put only the .skill in a folder (zip is built under dist/, then removed):
    python scripts/package_skill.py -o /path/to/output
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# ── Helpers ──────────────────────────────────────────────────────────────────


def find_repo_root(start: Path) -> Path | None:
    """Walk up from *start* looking for a .git directory."""
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def resolve_skill_dir(arg: str | None) -> Path:
    """Determine the skill directory from an optional CLI argument.

    With a positional *arg*:
      1. If absolute: that path only.
      2. Else try ``cwd / arg``, then ``repo/src/arg``, then ``repo/arg`` (legacy).

    With no *arg*: current directory if it contains ``SKILL.md``, else error
    with a short hint listing skills under ``src/`` when the repo is known.
    """
    cwd = Path.cwd().resolve()
    repo = find_repo_root(cwd)

    if arg is not None:
        p = Path(arg).expanduser()
        candidates: list[Path] = []
        if p.is_absolute():
            candidates.append(p.resolve())
        else:
            candidates.append((cwd / p).resolve())
            if repo is not None:
                candidates.append((repo / "src" / p).resolve())
                candidates.append((repo / p).resolve())

        seen: set[Path] = set()
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            if candidate.is_dir() and (candidate / "SKILL.md").is_file():
                return candidate

        raise FileNotFoundError(
            f"'{arg}' is not a directory containing SKILL.md "
            "(tried cwd, then repo src/, then repo root when applicable)"
        )

    if (cwd / "SKILL.md").is_file():
        return cwd

    hint = ""
    if repo is not None and (repo / "src").is_dir():
        skills = sorted(
            d
            for d in (repo / "src").iterdir()
            if d.is_dir() and (d / "SKILL.md").is_file()
        )
        if skills:
            hint = " Known skills under src/: " + ", ".join(s.name for s in skills) + "."

    raise FileNotFoundError(
        "No SKILL.md in the current directory."
        f"{hint}"
        " Pass the skill path (e.g. odi-plain-language or src/odi-plain-language "
        "from repo root), or cd into a skill folder."
    )


def parse_skill_name(skill_md: Path) -> str:
    """Extract the 'name' field from SKILL.md YAML frontmatter."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{skill_md} must start with YAML frontmatter (---)")

    closing = text.find("\n---", 3)
    if closing == -1:
        raise ValueError(f"{skill_md}: missing closing --- for frontmatter")

    frontmatter = text[3:closing]
    match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        raise ValueError(f"{skill_md}: frontmatter must include a 'name:' field")

    name = match.group(1).strip()
    if len(name) >= 2 and name[0] == name[-1] and name[0] in "\"'":
        name = name[1:-1]
    if not name or re.search(r"[\s/\\]", name):
        raise ValueError(
            f"{skill_md}: 'name' must be a single non-empty token safe for a filename"
        )
    return name


def should_skip(
    path: Path, skill_root: Path, package_name: str | None = None
) -> bool:
    """Return True if *path* must not appear in the published archive."""
    if "__pycache__" in path.parts:
        return True
    if path.name in {".DS_Store", "Thumbs.db", "desktop.ini"}:
        return True
    try:
        rel = path.relative_to(skill_root)
    except ValueError:
        return True
    # Authoring / diagram docs and local test fixtures are not shipped.
    if rel.parts and rel.parts[0] in {"docs", "tests"}:
        return True
    # Prior build outputs when packaging into the skill folder (--output-dir).
    return (
        package_name is not None
        and len(rel.parts) == 1
        and rel.name in {f"{package_name}.zip", f"{package_name}.skill"}
    )


def zip_directory(
    src_dir: Path, zip_path: Path, package_name: str | None = None
) -> int:
    """Zip *src_dir* into *zip_path*. Returns number of files archived."""
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file() or should_skip(path, src_dir, package_name):
                continue
            arcname = path.relative_to(src_dir)
            zf.write(path, arcname.as_posix())
            count += 1
    return count


def confirm(prompt: str) -> bool:
    """Ask a yes/no question. Returns True for y/Y/yes, False otherwise."""
    try:
        answer = input(f"{prompt} [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in {"y", "yes"}


def remove_packaged_artifacts_from_dist(dist_dir: Path, package_name: str) -> None:
    """Remove only this skill's build outputs under *dist_dir* (zip + .skill).

    Full dist/ is not cleared so other skills' draft builds stay intact.
    """
    if not dist_dir.is_dir():
        return
    for suffix in (".zip", ".skill"):
        p = dist_dir / f"{package_name}{suffix}"
        if p.is_file():
            p.unlink()


# ── Git tag helpers ──────────────────────────────────────────────────────────


def git_tags(repo: Path) -> list[str]:
    """Return git tags sorted by version, newest first."""
    try:
        result = subprocess.run(
            ["git", "tag", "--sort=-v:refname"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
        return [t for t in result.stdout.strip().splitlines() if t]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def _parse_skill_version_tag(tag: str, skill_name: str) -> tuple[int, int] | None:
    """Parse ``{skill_name}/{major}.{minor}`` or ``...-{label}``. See docs/RELEASE.md."""
    prefix = f"{skill_name}/"
    if not tag.startswith(prefix):
        return None
    rest = tag[len(prefix) :]
    m = re.match(r"^(\d+)\.(\d+)(?:-.+)?$", rest)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def _latest_skill_tag(skill_name: str, tags: list[str]) -> str | None:
    best: tuple[int, int, str] | None = None
    for tag in tags:
        v = _parse_skill_version_tag(tag, skill_name)
        if v is None:
            continue
        maj, mino = v
        if best is None or (maj, mino) > (best[0], best[1]):
            best = (maj, mino, tag)
    return best[2] if best else None


def suggest_next_skill_tag(
    skill_name: str, tags: list[str], *, draft: bool = False
) -> str:
    """Suggest ``{skill}/{major}.{minor+1}`` per docs/RELEASE.md; default ``…/1.0``.

    If *draft* is True (non-release / ``--no-prompt`` builds), append ``-draft``.
    """
    versions: list[tuple[int, int]] = []
    for tag in tags:
        v = _parse_skill_version_tag(tag, skill_name)
        if v is not None:
            versions.append(v)
    if not versions:
        base = f"{skill_name}/1.0"
    else:
        maj, mino = max(versions)
        base = f"{skill_name}/{maj}.{mino + 1}"
    if draft:
        return f"{base}-draft"
    return base


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Package a skill folder into <name>.skill "
            "(temporary zip under dist/, removed after copy)."
        ),
        epilog=(
            "Run with no arguments from inside a skill folder, or pass the "
            "skill name or path from the repo root (resolved under src/ first)."
        ),
    )
    parser.add_argument(
        "skill_folder",
        nargs="?",
        default=None,
        help="Path to the skill folder (default: cwd; from repo root, tries src/)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help=(
            "Directory for <name>.skill only (default: dist/). "
            "The zip is always written to dist/ then deleted after the copy."
        ),
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip interactive prompts (don't ask to copy to releases)",
    )
    args = parser.parse_args()

    # Resolve skill directory
    try:
        src_dir = resolve_skill_dir(args.skill_folder)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    skill_md = src_dir / "SKILL.md"

    # Parse name from frontmatter
    try:
        name = parse_skill_name(skill_md)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    # Determine output paths: zip is always built under dist/, then removed.
    repo = find_repo_root(src_dir)
    base_dir = repo if repo else Path.cwd().resolve()
    dist_dir = base_dir / "dist"
    zip_path = dist_dir / f"{name}.zip"

    if args.output_dir:
        skill_path = args.output_dir.resolve() / f"{name}.skill"
    else:
        skill_path = dist_dir / f"{name}.skill"
    releases_dir = base_dir / "releases"

    # Build
    try:
        count = zip_directory(src_dir, zip_path, name)
        shutil.copy2(zip_path, skill_path)
        zip_path.unlink(missing_ok=True)
    except (OSError, FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"\n  Packaged {count} files from {src_dir.relative_to(base_dir)}/")
    print(f"  {skill_path.relative_to(base_dir)}")

    # Offer to copy to releases/
    if not args.no_prompt:
        print()
        if confirm(f"Copy {name}.skill to releases/?"):
            releases_dir.mkdir(parents=True, exist_ok=True)
            dest = releases_dir / f"{name}.skill"
            shutil.copy2(skill_path, dest)
            print(f"  → {dest.relative_to(base_dir)}")
            try:
                remove_packaged_artifacts_from_dist(dist_dir, name)
                print(
                    f"  Removed {name}.skill from {dist_dir.relative_to(base_dir)}/ "
                    "(left other files unchanged)"
                )
            except OSError as e:
                print(
                    f"  warning: could not remove dist artifacts: {e}",
                    file=sys.stderr,
                )
        else:
            print("  Skipped.")

    # Suggest next tag (docs/RELEASE.md: {skill-name}/{major}.{minor}, optional -label)
    if repo:
        tags = git_tags(repo)
        latest = _latest_skill_tag(name, tags)
        draft = args.no_prompt
        next_tag = suggest_next_skill_tag(name, tags, draft=draft)
        print()
        if latest:
            print(f"  Latest tag for this skill: {latest}")
        if draft:
            print(
                "  Suggested next tag (draft build; omit --no-prompt for release):"
            )
        else:
            print("  Suggested next tag:")
        print(f"    {next_tag}")
        print(
            f"  Run: git tag '{next_tag}' && git push origin '{next_tag}'"
        )

    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
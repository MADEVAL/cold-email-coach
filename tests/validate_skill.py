#!/usr/bin/env python3
"""Structural validator for Cold Email Coach.

Stdlib only. Run from the repository root or from any directory:

    python tests/validate_skill.py

Exits 1 if any hard check fails.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "cold-email-coach"
SKILL = SKILL_DIR / "SKILL.md"
CHANGELOG = ROOT / "CHANGELOG.md"
README = ROOT / "README.md"
README_RU = ROOT / "README.ru.md"

REQUIRED_SECTIONS = [
    "When Not to Use",
    "Pick a Mode",
    "Gather the Minimum",
    "Write Like a Person",
    "The 11-Point Checklist",
    "Workflow",
    "Output Contract",
    "Constraints",
    "Optional Lint",
    "Files",
    "Test Cases",
]

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def between(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i + len(start))
    return text[i:j] if j >= 0 else text[i:]


def main() -> int:
    text = read(SKILL)
    changelog = read(CHANGELOG)
    readme = read(README)
    readme_ru = read(README_RU)

    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        fail("SKILL.md: missing or malformed frontmatter")
        return report()
    raw = match.group(1)
    top = dict(re.findall(r"^([a-z_]+):\s*(.+)$", raw, re.M))
    meta = dict(re.findall(r"^  ([a-z_]+):\s*(.+)$", raw, re.M))

    def clean(value: str) -> str:
        return value.strip().strip('"').strip("'")

    if clean(top.get("name", "")) != "cold-email-coach":
        fail(f"frontmatter name must be 'cold-email-coach', got {top.get('name')!r}")
    description = clean(top.get("description", ""))
    if not 80 <= len(description) <= 1024:
        fail(f"description length must be 80..1024, got {len(description)}")
    if "do not use" not in description.lower():
        fail("description must include negative triggers ('Do NOT use')")
    if clean(top.get("license", "")) != "MIT":
        fail("frontmatter license must be MIT")
    if not top.get("compatibility"):
        fail("frontmatter compatibility is required")

    version = clean(meta.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"metadata.version must be semver, got {version!r}")
    elif f"[{version}]" not in changelog:
        fail(f"CHANGELOG.md has no entry for {version}")
    if version and version not in readme:
        fail(f"README.md does not mention version {version}")
    if version and version not in readme_ru:
        fail(f"README.ru.md does not mention version {version}")
    if not meta.get("repository"):
        fail("metadata.repository is required")

    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in text:
            fail(f"missing section: ## {section}")

    modes = re.findall(r"^\| \*\*(WRITE|REVIEW|REWRITE)\*\* \|", between(text, "## Pick a Mode", "## Gather the Minimum"), re.M)
    if modes != ["WRITE", "REVIEW", "REWRITE"]:
        fail(f"mode table must list WRITE, REVIEW, REWRITE in order, got {modes}")

    checks = re.findall(r"^\d+\. \*\*", between(text, "## The 11-Point Checklist", "## Workflow"), re.M)
    if len(checks) != 11:
        fail(f"checklist must contain 11 items, got {len(checks)}")

    if len(list((SKILL_DIR / "references").glob("*.md"))) != 5:
        fail("references/ must contain 5 files")
    if len(list((SKILL_DIR / "examples").glob("*.md"))) != 4:
        fail("examples/ must contain 4 files")

    for folder in ("references", "examples", "scripts", "tests"):
        if not (SKILL_DIR / folder).is_dir():
            fail(f"missing folder: {folder}/")

    for linked in re.findall(r"\]\(([^)]+)\)", text):
        if linked.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = linked.split("#", 1)[0]
        if not target or "[" in target or target.endswith((".jpg", ".png")):
            continue
        if not (SKILL_DIR / target).exists():
            fail(f"SKILL.md link missing: {linked}")

    for rel in re.findall(r"`((?:references|examples|scripts|tests)/[^`]+)`", text):
        if "[" in rel:
            continue
        if not (SKILL_DIR / rel).exists():
            fail(f"SKILL.md path missing: {rel}")

    for needle in ("TODO", "FIXME"):
        if needle in text:
            fail(f"SKILL.md contains forbidden string: {needle!r}")

    plugin = ROOT / ".claude-plugin" / "plugin.json"
    if plugin.exists():
        data = json.loads(plugin.read_text(encoding="utf-8"))
        if clean(str(data.get("version"))) != version:
            fail("plugin.json version does not match SKILL.md")

    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    if marketplace.exists():
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        entry = (data.get("plugins") or [{}])[0]
        if clean(str(entry.get("version"))) != version:
            fail("marketplace.json version does not match SKILL.md")

    return report()


def report() -> int:
    if errors:
        print("Cold Email Coach validator")
        print("\nErrors:")
        for message in errors:
            print(f"  - {message}")
        print(f"\nFAILED: {len(errors)} error(s)")
        return 1
    print("Cold Email Coach validator")
    print("OK: all structural checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

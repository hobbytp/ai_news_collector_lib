from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple


TARGETS: Tuple[Tuple[str, str], ...] = (
    ("ai_news_collector_lib/__init__.py", r'__version__\s*=\s*"[^"]+"'),
    ("pyproject.toml", r'version\s*=\s*"[^"]+"'),
    ("setup.py", r'version\s*=\s*"[^"]+"'),
)


def sync_versions(repo_root: str, version: str, dry_run: bool = True) -> List[str]:
    changes: List[str] = []
    for relative_path, pattern in TARGETS:
        file_path = Path(repo_root) / relative_path
        if not file_path.exists():
            continue
        original = file_path.read_text(encoding="utf-8")
        if "__version__" in pattern:
            replacement = f'__version__ = "{version}"'
        else:
            replacement = f'version = "{version}"'
        updated = re.sub(pattern, replacement, original, count=1)
        if updated != original:
            changes.append(relative_path)
            if not dry_run:
                file_path.write_text(updated, encoding="utf-8")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    changed = sync_versions(args.repo_root, args.version, dry_run=args.dry_run)
    print("version sync:", ",".join(changed) if changed else "no changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

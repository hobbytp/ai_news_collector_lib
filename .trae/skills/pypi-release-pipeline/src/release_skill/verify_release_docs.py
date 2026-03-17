from __future__ import annotations

import argparse
from pathlib import Path
from typing import List


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--require-file", action="append", default=[])
    parser.add_argument("--require-version-in", action="append", default=[])
    parser.add_argument("--release-note-glob", action="append", default=[])
    parser.add_argument("--allow-missing-release-note", action="store_true")
    return parser.parse_args()


def _contains_version(content: str, version: str) -> bool:
    return version in content or f"v{version}" in content


def _check_required_files(repo_root: Path, files: List[str], errors: List[str]) -> None:
    for file_name in files:
        file_path = repo_root / file_name
        if not file_path.exists() or not file_path.is_file():
            errors.append(f"missing required document: {file_name}")


def _check_version_markers(repo_root: Path, files: List[str], version: str, errors: List[str]) -> None:
    for file_name in files:
        file_path = repo_root / file_name
        if not file_path.exists() or not file_path.is_file():
            continue
        content = file_path.read_text(encoding="utf-8")
        if not _contains_version(content, version):
            errors.append(f"document missing version marker ({version}): {file_name}")


def _check_release_note(
    repo_root: Path,
    globs: List[str],
    version: str,
    allow_missing: bool,
    errors: List[str],
) -> None:
    candidates: List[Path] = []
    for pattern in globs:
        candidates.extend(repo_root.glob(pattern))
    files = [path for path in candidates if path.is_file()]
    if not files and allow_missing:
        return
    if not files:
        errors.append(
            "release note file not found. checked patterns: "
            + ", ".join(globs)
        )
        return
    matched = False
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        if _contains_version(content, version):
            matched = True
            break
    if not matched:
        errors.append(
            "release note does not contain target version marker: "
            + ", ".join(str(path.relative_to(repo_root)) for path in files)
        )


def main() -> int:
    args = _parse_args()
    repo_root = Path(args.repo_root)
    if not repo_root.exists() or not repo_root.is_dir():
        print(f"repo root not found: {repo_root}")
        return 1
    errors: List[str] = []
    _check_required_files(repo_root, list(args.require_file), errors)
    _check_version_markers(repo_root, list(args.require_version_in), args.version, errors)
    _check_release_note(
        repo_root=repo_root,
        globs=list(args.release_note_glob),
        version=args.version,
        allow_missing=bool(args.allow_missing_release_note),
        errors=errors,
    )
    if errors:
        print("documentation gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("documentation gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

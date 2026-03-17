from __future__ import annotations

import argparse
import json
from pathlib import Path


def _skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_yaml_text() -> str:
    return (_skill_root() / "skill.yaml").read_text(encoding="utf-8")


def register(target_dir: str) -> None:
    root = _skill_root()
    target = Path(target_dir).resolve() / root.name
    target.mkdir(parents=True, exist_ok=True)
    for source in root.rglob("*"):
        if source.is_dir():
            continue
        rel = source.relative_to(root)
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    manifest = {
        "name": root.name,
        "registered_path": str(target),
        "status": "active",
    }
    (target / "registration.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def upgrade(version: str) -> None:
    skill_file = _skill_root() / "skill.yaml"
    content = _load_yaml_text()
    updated = []
    for line in content.splitlines():
        if line.startswith("version:"):
            updated.append(f"version: {version}")
        else:
            updated.append(line)
    skill_file.write_text("\n".join(updated) + "\n", encoding="utf-8")


def deprecate() -> None:
    skill_file = _skill_root() / "skill.yaml"
    content = _load_yaml_text()
    updated = []
    for line in content.splitlines():
        if line.startswith("status:"):
            updated.append("status: deprecated")
        else:
            updated.append(line)
    skill_file.write_text("\n".join(updated) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("--target-dir", required=True)

    upgrade_parser = subparsers.add_parser("upgrade")
    upgrade_parser.add_argument("--version", required=True)

    subparsers.add_parser("deprecate")
    args = parser.parse_args()

    if args.action == "register":
        register(args.target_dir)
    elif args.action == "upgrade":
        upgrade(args.version)
    else:
        deprecate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

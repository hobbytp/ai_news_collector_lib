from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    mode = "dry-run" if args.dry_run or not args.live else "live"
    print(f"verify release artifacts for {args.tag} in {mode} mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

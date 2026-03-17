from __future__ import annotations

import sys


def main() -> int:
    command = sys.argv[1:]
    print("dry-run:", " ".join(command))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

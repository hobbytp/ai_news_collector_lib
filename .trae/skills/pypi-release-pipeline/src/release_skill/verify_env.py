from __future__ import annotations

import os
import sys


def main() -> int:
    keys = sys.argv[1:]
    if not keys:
        return 0
    missing = [key for key in keys if not os.getenv(key)]
    if missing:
        print("missing env vars:", ",".join(missing))
        return 2
    print("env verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

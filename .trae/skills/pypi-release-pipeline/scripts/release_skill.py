from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _bootstrap_path() -> None:
    current = Path(__file__).resolve()
    src = current.parent.parent / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    _bootstrap_path()
    from release_skill.orchestrator import ReleaseOrchestrator, ReleaseRequest

    parser = argparse.ArgumentParser()
    parser.add_argument("--request-file", required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.request_file).read_text(encoding="utf-8"))
    request = ReleaseRequest.from_dict(payload)
    report = ReleaseOrchestrator(request).execute()
    print(report.to_json())
    return 0 if report.status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())

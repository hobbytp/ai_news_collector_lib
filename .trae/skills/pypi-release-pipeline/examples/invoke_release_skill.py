from __future__ import annotations

import json
import subprocess
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    request_file = root / "examples" / "release-request.json"
    cli = root / "scripts" / "release_skill.py"
    process = subprocess.run(
        ["python", str(cli), "--request-file", str(request_file)],
        text=True,
        capture_output=True,
        check=False,
    )
    if process.stdout:
        report = json.loads(process.stdout)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if process.stderr:
        print(process.stderr)
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())

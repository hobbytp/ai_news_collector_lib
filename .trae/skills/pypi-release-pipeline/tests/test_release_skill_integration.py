from __future__ import annotations

import sys
from pathlib import Path

SKILL_SRC = Path(__file__).resolve().parents[1] / "src"
if str(SKILL_SRC) not in sys.path:
    sys.path.insert(0, str(SKILL_SRC))

from release_skill.orchestrator import CommandResult, ReleaseOrchestrator, ReleaseRequest


class StableRunner:
    def __init__(self, fail_on_call: int = -1) -> None:
        self.count = 0
        self.fail_on_call = fail_on_call

    def run(self, command, cwd, timeout_seconds, env=None):
        self.count += 1
        if self.count == self.fail_on_call:
            return CommandResult(return_code=1, stdout="", stderr="simulated failure")
        return CommandResult(return_code=0, stdout=f"ok:{' '.join(command)}", stderr="")


def test_full_dry_run_success(tmp_path: Path) -> None:
    request = ReleaseRequest.from_dict(
        {
            "version": "0.1.6",
            "repo_root": str(tmp_path),
            "dry_run": True,
            "retry_policy": {"max_attempts": 1, "backoff_seconds": 0, "exponential": False},
        }
    )
    report = ReleaseOrchestrator(request, runner=StableRunner()).execute()
    assert report.status == "success"
    assert len(report.steps) == 11
    assert all(step.status == "success" for step in report.steps)


def test_failure_path_returns_rollback_summary(tmp_path: Path) -> None:
    request = ReleaseRequest.from_dict(
        {
            "version": "0.1.6",
            "repo_root": str(tmp_path),
            "dry_run": False,
            "retry_policy": {"max_attempts": 1, "backoff_seconds": 0, "exponential": False},
            "rollback": {"enabled": True, "mode": "safe"},
        }
    )
    report = ReleaseOrchestrator(request, runner=StableRunner(fail_on_call=10)).execute()
    assert report.status == "failed"
    assert len(report.rollback_summary) >= 1

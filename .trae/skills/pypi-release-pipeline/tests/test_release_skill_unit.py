from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Union

import pytest

SKILL_SRC = Path(__file__).resolve().parents[1] / "src"
if str(SKILL_SRC) not in sys.path:
    sys.path.insert(0, str(SKILL_SRC))

from release_skill.orchestrator import (
    CommandResult,
    ReleaseOrchestrator,
    ReleaseRequest,
    ReleaseValidationError,
)


Outcome = Union[CommandResult, Exception]


class ScriptedRunner:
    def __init__(self, outcomes: List[Outcome]) -> None:
        self.outcomes = outcomes[:]
        self.commands: List[List[str]] = []

    def run(self, command, cwd, timeout_seconds, env=None):
        self.commands.append(list(command))
        if not self.outcomes:
            return CommandResult(return_code=0, stdout="ok", stderr="")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _request(
    repo_root: str,
    dry_run: bool = False,
    max_attempts: int = 2,
    rollback_mode: str = "safe",
) -> ReleaseRequest:
    payload = {
        "version": "0.1.6",
        "repo_root": repo_root,
        "dry_run": dry_run,
        "retry_policy": {"max_attempts": max_attempts, "backoff_seconds": 0, "exponential": False},
        "rollback": {"enabled": True, "mode": rollback_mode},
    }
    return ReleaseRequest.from_dict(payload)


def test_invalid_semver_raises(tmp_path: Path) -> None:
    request = ReleaseRequest.from_dict(
        {"version": "invalid", "repo_root": str(tmp_path), "dry_run": True}
    )
    orchestrator = ReleaseOrchestrator(request, runner=ScriptedRunner([]))
    with pytest.raises(ReleaseValidationError):
        orchestrator.execute()


def test_retry_succeeds_on_second_attempt(tmp_path: Path) -> None:
    outcomes = [
        CommandResult(return_code=1, stdout="", stderr="fail once"),
        CommandResult(return_code=0, stdout="ok", stderr=""),
    ]
    request = _request(str(tmp_path), dry_run=True, max_attempts=2)
    orchestrator = ReleaseOrchestrator(request, runner=ScriptedRunner(outcomes))
    report = orchestrator.execute()
    assert report.status == "success"
    assert report.steps[0].attempts == 2


def test_timeout_is_reported(tmp_path: Path) -> None:
    timeout_exc = subprocess.TimeoutExpired(cmd=["pytest"], timeout=1)
    request = _request(str(tmp_path), dry_run=True, max_attempts=1)
    orchestrator = ReleaseOrchestrator(request, runner=ScriptedRunner([timeout_exc]))
    report = orchestrator.execute()
    assert report.status == "failed"
    assert report.steps[0].error_type == "timeout_error"


def test_safe_rollback_skips_reset(tmp_path: Path) -> None:
    outcomes = [CommandResult(0, "ok", "")] * 9 + [CommandResult(1, "", "push fail")]
    runner = ScriptedRunner(outcomes)
    request = _request(str(tmp_path), dry_run=False, max_attempts=1, rollback_mode="safe")
    report = ReleaseOrchestrator(request, runner=runner).execute()
    assert report.status == "failed"
    rollback_commands = " ".join(report.rollback_summary)
    assert "git reset --hard HEAD~1" not in rollback_commands


def test_full_rollback_includes_reset(tmp_path: Path) -> None:
    outcomes = [CommandResult(0, "ok", "")] * 9 + [CommandResult(1, "", "push fail")]
    runner = ScriptedRunner(outcomes)
    request = _request(str(tmp_path), dry_run=False, max_attempts=1, rollback_mode="full")
    report = ReleaseOrchestrator(request, runner=runner).execute()
    assert report.status == "failed"
    rollback_commands = " ".join(report.rollback_summary)
    assert "git reset --hard HEAD~1:success" in rollback_commands


def test_release_request_has_default_doc_requirements(tmp_path: Path) -> None:
    request = ReleaseRequest.from_dict(
        {"version": "0.1.6", "repo_root": str(tmp_path), "dry_run": True}
    )
    assert "README.md" in request.required_docs
    assert "USAGE_GUIDE.md" in request.required_docs
    assert "CHANGELOG.md" in request.required_docs
    assert request.require_release_note is True

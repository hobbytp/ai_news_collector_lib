from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Sequence, cast


SEMVER_PATTERN = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$"


class ReleaseValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 2
    backoff_seconds: float = 1.0
    exponential: bool = True


@dataclass(frozen=True)
class RollbackPolicy:
    enabled: bool = True
    mode: str = "safe"


@dataclass(frozen=True)
class ReleaseRequest:
    version: str
    repo_root: str
    branch: str = "master"
    tag_prefix: str = "v"
    dry_run: bool = True
    required_env_vars: Sequence[str] = field(default_factory=lambda: ("PYPI_API_TOKEN",))
    required_docs: Sequence[str] = field(
        default_factory=lambda: ("README.md", "USAGE_GUIDE.md", "CHANGELOG.md")
    )
    require_release_note: bool = True
    release_note_globs: Sequence[str] = field(
        default_factory=lambda: ("RELEASE_NOTES.md", "V*_RELEASE_SUMMARY.md", "docs/releases/*.md")
    )
    test_command: Sequence[str] = field(default_factory=lambda: ("python", "-m", "pytest", "-v"))
    lint_command: Sequence[str] = field(default_factory=lambda: ("make", "lint"))
    typecheck_command: Sequence[str] = field(
        default_factory=lambda: ("python", "-m", "mypy", "ai_news_collector_lib")
    )
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    rollback: RollbackPolicy = field(default_factory=RollbackPolicy)
    timeouts: Dict[str, int] = field(default_factory=dict)

    @property
    def tag(self) -> str:
        return f"{self.tag_prefix}{self.version}"

    @staticmethod
    def from_dict(payload: Dict[str, object]) -> "ReleaseRequest":
        quality_gates = _as_dict(payload.get("quality_gates", {}))
        retry_raw = _as_dict(payload.get("retry_policy", {}))
        rollback_raw = _as_dict(payload.get("rollback", {}))
        docs_gate = _as_dict(payload.get("documentation_gate", {}))
        required_env_vars = _as_str_list(payload.get("required_env_vars"), ["PYPI_API_TOKEN"])
        required_docs = _as_str_list(
            docs_gate.get("required_files"),
            ["README.md", "USAGE_GUIDE.md", "CHANGELOG.md"],
        )
        release_note_globs = _as_str_list(
            docs_gate.get("release_note_globs"),
            ["RELEASE_NOTES.md", "V*_RELEASE_SUMMARY.md", "docs/releases/*.md"],
        )
        test_command = _as_str_list(
            quality_gates.get("test_command"),
            ["python", "-m", "pytest", "-v"],
        )
        lint_command = _as_str_list(quality_gates.get("lint_command"), ["make", "lint"])
        typecheck_command = _as_str_list(
            quality_gates.get("typecheck_command"),
            ["python", "-m", "mypy", "ai_news_collector_lib"],
        )
        raw_timeouts = _as_dict(payload.get("timeouts", {}))
        return ReleaseRequest(
            version=str(payload.get("version", "")),
            repo_root=str(payload.get("repo_root", "")),
            branch=str(payload.get("branch", "master")),
            tag_prefix=str(payload.get("tag_prefix", "v")),
            dry_run=bool(payload.get("dry_run", True)),
            required_env_vars=tuple(required_env_vars),
            required_docs=tuple(required_docs),
            require_release_note=bool(docs_gate.get("require_release_note", True)),
            release_note_globs=tuple(release_note_globs),
            test_command=tuple(test_command),
            lint_command=tuple(lint_command),
            typecheck_command=tuple(typecheck_command),
            retry_policy=RetryPolicy(
                max_attempts=_as_int(retry_raw.get("max_attempts"), 2),
                backoff_seconds=_as_float(retry_raw.get("backoff_seconds"), 1.0),
                exponential=bool(retry_raw.get("exponential", True)),
            ),
            rollback=RollbackPolicy(
                enabled=bool(rollback_raw.get("enabled", True)),
                mode=str(rollback_raw.get("mode", "safe")),
            ),
            timeouts={str(k): _as_int(v, 0) for k, v in raw_timeouts.items()},
        )


@dataclass(frozen=True)
class CommandResult:
    return_code: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    def run(
        self, command: Sequence[str], cwd: str, timeout_seconds: int, env: Optional[Dict[str, str]] = None
    ) -> CommandResult:
        ...


class SubprocessRunner:
    def run(
        self, command: Sequence[str], cwd: str, timeout_seconds: int, env: Optional[Dict[str, str]] = None
    ) -> CommandResult:
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=merged_env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return CommandResult(
            return_code=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )


@dataclass
class StepResult:
    name: str
    status: str
    attempts: int
    started_at: str
    ended_at: str
    stdout: str = ""
    stderr: str = ""
    error_type: Optional[str] = None
    rollback_actions: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AtomicStep:
    name: str
    command: Sequence[str]
    timeout_seconds: int
    rollback_commands: Sequence[Sequence[str]] = field(default_factory=tuple)


@dataclass
class ReleaseReport:
    version: str
    tag: str
    status: str
    steps: List[StepResult]
    rollback_summary: List[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


class ReleaseOrchestrator:
    def __init__(self, request: ReleaseRequest, runner: Optional[CommandRunner] = None) -> None:
        self.request = request
        self.runner = runner or SubprocessRunner()
        self._completed_steps: List[AtomicStep] = []

    def execute(self) -> ReleaseReport:
        self._validate_request()
        steps = self._build_steps()
        results: List[StepResult] = []
        rollback_summary: List[str] = []
        for step in steps:
            step_result = self._execute_step(step)
            results.append(step_result)
            if step_result.status == "success":
                self._completed_steps.append(step)
                continue
            rollback_actions = self._rollback()
            step_result.rollback_actions.extend(rollback_actions)
            rollback_summary.extend(rollback_actions)
            return ReleaseReport(
                version=self.request.version,
                tag=self.request.tag,
                status="failed",
                steps=results,
                rollback_summary=rollback_summary,
            )
        return ReleaseReport(
            version=self.request.version,
            tag=self.request.tag,
            status="success",
            steps=results,
            rollback_summary=rollback_summary,
        )

    def _validate_request(self) -> None:
        if not re.match(SEMVER_PATTERN, self.request.version):
            raise ReleaseValidationError(f"invalid semver version: {self.request.version}")
        repo_path = Path(self.request.repo_root)
        if not repo_path.exists() or not repo_path.is_dir():
            raise ReleaseValidationError(f"repo_root not found: {self.request.repo_root}")
        if self.request.retry_policy.max_attempts < 1:
            raise ReleaseValidationError("retry_policy.max_attempts must be >= 1")
        if self.request.rollback.mode not in {"none", "safe", "full"}:
            raise ReleaseValidationError("rollback.mode must be one of: none, safe, full")

    def _build_steps(self) -> List[AtomicStep]:
        repo = self.request.repo_root
        version = self.request.version
        tag = self.request.tag
        dry = self.request.dry_run
        module_dir = Path(__file__).resolve().parent
        verify_env_script = str(module_dir / "verify_env.py")
        verify_docs_script = str(module_dir / "verify_release_docs.py")
        version_sync_script = str(module_dir / "version_sync.py")
        verify_release_script = str(module_dir / "verify_release.py")
        dry_run_executor_script = str(module_dir / "dry_run_executor.py")
        version_update = [
            "python",
            version_sync_script,
            "--repo-root",
            repo,
            "--version",
            version,
        ]
        if dry:
            version_update.append("--dry-run")
        docs_command = [
            "python",
            verify_docs_script,
            "--repo-root",
            repo,
            "--version",
            version,
        ]
        for required_doc in self.request.required_docs:
            docs_command.extend(["--require-file", required_doc])
            docs_command.extend(["--require-version-in", required_doc])
        for pattern in self.request.release_note_globs:
            docs_command.extend(["--release-note-glob", pattern])
        if not self.request.require_release_note:
            docs_command.append("--allow-missing-release-note")

        steps: List[AtomicStep] = [
            AtomicStep(
                name="verify_required_env",
                command=["python", verify_env_script, *self.request.required_env_vars],
                timeout_seconds=self._timeout("verify_required_env", 30),
            ),
            AtomicStep(
                name="validate_git_state",
                command=["git", "status", "--porcelain"],
                timeout_seconds=self._timeout("validate_git_state", 60),
            ),
            AtomicStep(
                name="validate_release_docs",
                command=docs_command,
                timeout_seconds=self._timeout("validate_release_docs", 90),
            ),
            AtomicStep(
                name="run_tests",
                command=list(self.request.test_command),
                timeout_seconds=self._timeout("run_tests", 600),
            ),
            AtomicStep(
                name="run_lint",
                command=list(self.request.lint_command),
                timeout_seconds=self._timeout("run_lint", 300),
            ),
            AtomicStep(
                name="run_typecheck",
                command=list(self.request.typecheck_command),
                timeout_seconds=self._timeout("run_typecheck", 300),
            ),
            AtomicStep(
                name="sync_version_files",
                command=version_update,
                timeout_seconds=self._timeout("sync_version_files", 120),
            ),
            AtomicStep(
                name="create_release_commit",
                command=["git", "commit", "-am", f"chore(release): bump version to {version}"],
                timeout_seconds=self._timeout("create_release_commit", 120),
                rollback_commands=[["git", "reset", "--hard", "HEAD~1"]],
            ),
            AtomicStep(
                name="create_annotated_tag",
                command=["git", "tag", "-a", tag, "-m", f"Release {tag}"],
                timeout_seconds=self._timeout("create_annotated_tag", 60),
                rollback_commands=[["git", "tag", "-d", tag]],
            ),
            AtomicStep(
                name="push_branch_and_tag",
                command=["git", "push", "origin", self.request.branch, tag],
                timeout_seconds=self._timeout("push_branch_and_tag", 300),
                rollback_commands=[["git", "push", "origin", f":refs/tags/{tag}"]],
            ),
            AtomicStep(
                name="verify_release_artifacts",
                command=["python", verify_release_script, "--tag", tag, "--dry-run" if dry else "--live"],
                timeout_seconds=self._timeout("verify_release_artifacts", 300),
            ),
        ]
        if dry:
            return [self._to_dry_run_step(step, dry_run_executor_script) for step in steps]
        return steps

    def _to_dry_run_step(self, step: AtomicStep, dry_run_executor_script: str) -> AtomicStep:
        return AtomicStep(
            name=step.name,
            command=["python", dry_run_executor_script, *step.command],
            timeout_seconds=step.timeout_seconds,
            rollback_commands=[["python", dry_run_executor_script, *cmd] for cmd in step.rollback_commands],
        )

    def _timeout(self, step_name: str, default: int) -> int:
        return int(self.request.timeouts.get(step_name, default))

    def _backoff(self, attempt: int) -> float:
        base = self.request.retry_policy.backoff_seconds
        if not self.request.retry_policy.exponential:
            return base
        return float(base * (2 ** (attempt - 1)))

    def _execute_step(self, step: AtomicStep) -> StepResult:
        attempts = 0
        started = _utc_now()
        last_stdout = ""
        last_stderr = ""
        for attempts in range(1, self.request.retry_policy.max_attempts + 1):
            try:
                result = self.runner.run(step.command, self.request.repo_root, step.timeout_seconds)
                last_stdout = result.stdout
                last_stderr = result.stderr
                if result.return_code == 0:
                    return StepResult(
                        name=step.name,
                        status="success",
                        attempts=attempts,
                        started_at=started,
                        ended_at=_utc_now(),
                        stdout=last_stdout,
                        stderr=last_stderr,
                    )
            except subprocess.TimeoutExpired as exc:
                last_stdout = (exc.stdout or "").strip() if isinstance(exc.stdout, str) else ""
                last_stderr = (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout"
                if attempts >= self.request.retry_policy.max_attempts:
                    return StepResult(
                        name=step.name,
                        status="failed",
                        attempts=attempts,
                        started_at=started,
                        ended_at=_utc_now(),
                        stdout=last_stdout,
                        stderr=last_stderr,
                        error_type="timeout_error",
                    )
            if attempts < self.request.retry_policy.max_attempts:
                time.sleep(self._backoff(attempts))
        return StepResult(
            name=step.name,
            status="failed",
            attempts=attempts,
            started_at=started,
            ended_at=_utc_now(),
            stdout=last_stdout,
            stderr=last_stderr,
            error_type="command_error",
        )

    def _rollback(self) -> List[str]:
        if not self.request.rollback.enabled or self.request.rollback.mode == "none":
            return []
        rollback_actions: List[str] = []
        for step in reversed(self._completed_steps):
            for command in step.rollback_commands:
                if self.request.rollback.mode == "safe" and command[:3] == ["git", "reset", "--hard"]:
                    continue
                result = self.runner.run(command, self.request.repo_root, 60)
                suffix = "success" if result.return_code == 0 else "failed"
                rollback_actions.append(f"{' '.join(command)}:{suffix}")
        return rollback_actions


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: object) -> Dict[str, object]:
    if isinstance(value, dict):
        return cast(Dict[str, object], value)
    return {}


def _as_str_list(value: object, default: Sequence[str]) -> List[str]:
    if not isinstance(value, list):
        return list(default)
    return [str(item) for item in value]


def _as_int(value: object, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float, str)):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
    return default


def _as_float(value: object, default: float) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float, str)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    return default

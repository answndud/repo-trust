from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from .targets import parse_target


@dataclass(frozen=True)
class InstallAuditSignal:
    id: str
    severity: str
    evidence: str
    recommendation: str


@dataclass(frozen=True)
class InstallAudit:
    target: str
    local_path: Path | None
    signals: list[InstallAuditSignal]
    local_only: bool = False


def audit_install(target: str) -> InstallAudit:
    parsed = parse_target(target)
    if parsed.kind != "local" or parsed.path is None:
        return InstallAudit(
            target=target,
            local_path=None,
            signals=[
                InstallAuditSignal(
                    id="audit.install.local_checkout_required",
                    severity="info",
                    evidence="GitHub URL or non-local target",
                    recommendation="Scan a local checkout to inspect install-time files without cloning or API calls.",
                )
            ],
            local_only=True,
        )

    repo_path = Path(parsed.path)
    if not repo_path.is_dir():
        return InstallAudit(
            target=target,
            local_path=repo_path,
            signals=[
                InstallAuditSignal(
                    id="audit.install.local_path_missing",
                    severity="high",
                    evidence=str(repo_path),
                    recommendation="Pass a valid local repository path.",
                )
            ],
        )

    signals: list[InstallAuditSignal] = []
    signals.extend(_python_install_signals(repo_path))
    signals.extend(_node_install_signals(repo_path))
    signals.extend(_root_execution_file_signals(repo_path))
    signals.extend(_vcs_dependency_signals(repo_path))

    return InstallAudit(
        target=target,
        local_path=repo_path,
        signals=sorted(signals, key=_signal_sort_key),
    )


def render_install_audit(audit: InstallAudit, *, locale: str = "en") -> str:
    if locale == "ko":
        return _render_ko(audit)
    return _render_en(audit)


def _render_en(audit: InstallAudit) -> str:
    lines = [
        "RepoTrust Install Audit",
        "",
        f"Target: {audit.target}",
    ]
    if audit.local_only:
        lines.extend(
            [
                "Scope: local checkout required",
                "",
                "Signals:",
            ]
        )
        lines.extend(_signal_lines(audit.signals))
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(
        [
            f"Local path: {audit.local_path}",
            "",
            "Install-time execution signals:",
        ]
    )
    lines.extend(_signal_lines(audit.signals))
    lines.extend(
        [
            "",
            "Next step:",
            "- Review high and medium signals before running README commands, package installs, or build tooling on a host machine.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _render_ko(audit: InstallAudit) -> str:
    lines = [
        "RepoTrust 설치 감사",
        "",
        f"대상: {audit.target}",
    ]
    if audit.local_only:
        lines.extend(
            [
                "범위: 로컬 checkout 필요",
                "",
                "신호:",
            ]
        )
        lines.extend(_signal_lines(audit.signals))
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(
        [
            f"로컬 경로: {audit.local_path}",
            "",
            "설치 시점 실행 신호:",
        ]
    )
    lines.extend(_signal_lines(audit.signals))
    lines.extend(
        [
            "",
            "다음 단계:",
            "- host machine에서 README 명령, package install, build tooling을 실행하기 전에 high/medium 신호를 먼저 검토하세요.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _signal_lines(signals: list[InstallAuditSignal]) -> list[str]:
    if not signals:
        return ["- none detected"]
    return [
        f"- {signal.id} [{signal.severity}]: {signal.evidence} -> {signal.recommendation}"
        for signal in signals
    ]


def _python_install_signals(repo_path: Path) -> list[InstallAuditSignal]:
    signals: list[InstallAuditSignal] = []
    setup_py = repo_path / "setup.py"
    if setup_py.is_file():
        signals.append(
            InstallAuditSignal(
                id="audit.install.python_setup_py",
                severity="medium",
                evidence="setup.py",
                recommendation="Review setup.py before source or editable installs because it can execute Python code.",
            )
        )

    setup_cfg = repo_path / "setup.cfg"
    if setup_cfg.is_file():
        signals.append(
            InstallAuditSignal(
                id="audit.install.python_setup_cfg",
                severity="low",
                evidence="setup.cfg",
                recommendation="Review packaging metadata before source installs.",
            )
        )

    pyproject = _read_toml(repo_path / "pyproject.toml")
    build_system = pyproject.get("build-system")
    if isinstance(build_system, dict):
        backend = build_system.get("build-backend")
        if isinstance(backend, str) and backend.strip():
            signals.append(
                InstallAuditSignal(
                    id="audit.install.python_build_backend",
                    severity="medium",
                    evidence=f"pyproject.toml build-system.build-backend: {backend}",
                    recommendation="Review build backend behavior before source installs.",
                )
            )
    return signals


def _node_install_signals(repo_path: Path) -> list[InstallAuditSignal]:
    package_json = repo_path / "package.json"
    data = _read_json(package_json)
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return []

    signals: list[InstallAuditSignal] = []
    for script_name in ("preinstall", "install", "postinstall", "prepare"):
        command = scripts.get(script_name)
        if isinstance(command, str) and command.strip():
            signals.append(
                InstallAuditSignal(
                    id="audit.install.npm_lifecycle_script",
                    severity="medium",
                    evidence=f"package.json scripts.{script_name}: {command.strip()}",
                    recommendation="Review npm lifecycle scripts before npm install or agent delegation.",
                )
            )
    return signals


def _root_execution_file_signals(repo_path: Path) -> list[InstallAuditSignal]:
    signals: list[InstallAuditSignal] = []
    for filename, signal_id, recommendation in (
        (
            "Makefile",
            "audit.install.makefile",
            "Review make targets before running build or install commands.",
        ),
        (
            "Dockerfile",
            "audit.install.dockerfile",
            "Review container build steps before running docker build.",
        ),
    ):
        if (repo_path / filename).is_file():
            signals.append(
                InstallAuditSignal(
                    id=signal_id,
                    severity="low",
                    evidence=filename,
                    recommendation=recommendation,
                )
            )

    for script in sorted(repo_path.glob("*.sh")):
        if script.is_file():
            signals.append(
                InstallAuditSignal(
                    id="audit.install.root_shell_script",
                    severity="medium",
                    evidence=script.name,
                    recommendation="Review root shell scripts before executing or delegating setup.",
                )
            )
    return signals


def _vcs_dependency_signals(repo_path: Path) -> list[InstallAuditSignal]:
    signals: list[InstallAuditSignal] = []
    for manifest in ("requirements.txt", "requirements-dev.txt", "pyproject.toml", "package.json"):
        path = repo_path / manifest
        if not path.is_file():
            continue
        evidence = _first_vcs_line(path)
        if evidence:
            signals.append(
                InstallAuditSignal(
                    id="audit.install.vcs_dependency",
                    severity="medium",
                    evidence=f"{manifest}: {evidence}",
                    recommendation="Prefer reviewed release artifacts or pinned commits before installing VCS dependencies.",
                )
            )
    return signals


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as toml_file:
            data = tomllib.load(toml_file)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _first_vcs_line(path: Path) -> str | None:
    for raw_line in _read_text(path).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "git+" in line or "github.com/" in line:
            return line
    return None


def _signal_sort_key(signal: InstallAuditSignal) -> tuple[int, str]:
    severity_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
    return (severity_rank.get(signal.severity, 4), signal.id)

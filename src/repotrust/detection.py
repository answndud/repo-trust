from __future__ import annotations

from pathlib import Path

from .models import DetectedFiles


README_NAMES = ("README.md", "README.rst", "README.txt", "README")
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING")
SECURITY_NAMES = ("SECURITY.md", ".github/SECURITY.md")
DEPENDENCY_MANIFESTS = (
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "go.mod",
)
LOCKFILES = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pylock.toml",
    "uv.lock",
    "Pipfile.lock",
    "go.sum",
)


def detect_files(repo_path: Path) -> DetectedFiles:
    return DetectedFiles(
        readme=_first_existing(repo_path, README_NAMES),
        license=_first_existing(repo_path, LICENSE_NAMES),
        security=_first_existing(repo_path, SECURITY_NAMES),
        ci_workflows=_ci_workflows(repo_path),
        dependency_manifests=_existing(repo_path, DEPENDENCY_MANIFESTS),
        lockfiles=_existing(repo_path, LOCKFILES),
        dependabot=_first_existing(
            repo_path,
            (".github/dependabot.yml", ".github/dependabot.yaml"),
        ),
    )


def _first_existing(repo_path: Path, candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if (repo_path / candidate).is_file():
            return candidate
    return None


def _existing(repo_path: Path, candidates: tuple[str, ...]) -> list[str]:
    return [candidate for candidate in candidates if (repo_path / candidate).is_file()]


def _ci_workflows(repo_path: Path) -> list[str]:
    workflows_dir = repo_path / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []
    workflows = [
        path.relative_to(repo_path).as_posix()
        for path in workflows_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    ]
    return sorted(workflows)

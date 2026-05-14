from __future__ import annotations

import json
import os
from base64 import b64decode
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from .remote_markers import (
    REMOTE_CONTENTS_ENDPOINT,
    REMOTE_DEPENDABOT_ENDPOINT,
    REMOTE_README_ENDPOINT,
    REMOTE_SECURITY_POLICY_ENDPOINT,
    REMOTE_WORKFLOWS_ENDPOINT,
)
from .rules import (
    github_subpath_unsupported_finding,
    install_safety_rules,
    project_hygiene_rules,
    readme_quality_rules,
    security_posture_rules,
)
from .scoring import calculate_score


GITHUB_API_BASE_URL = "https://api.github.com"
README_NAMES = {"README.md", "README.rst", "README.txt", "README"}
LICENSE_NAMES = {"LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"}
SECURITY_NAMES = {"SECURITY.md"}
GITHUB_SECURITY_PATH = ".github/SECURITY.md"
DEPENDENCY_MANIFESTS = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "go.mod",
}
LOCKFILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pylock.toml",
    "uv.lock",
    "Pipfile.lock",
    "go.sum",
}


@dataclass(frozen=True)
class GitHubResponse:
    status_code: int
    data: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)


class GitHubTransport(Protocol):
    def request(self, method: str, url: str, headers: dict[str, str]) -> GitHubResponse:
        ...


class UrllibGitHubTransport:
    def request(self, method: str, url: str, headers: dict[str, str]) -> GitHubResponse:
        request = Request(url, headers=headers, method=method)
        try:
            with urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body) if body else {}
                return GitHubResponse(
                    status_code=response.status,
                    data=data,
                    headers=dict(response.headers.items()),
                )
        except HTTPError as exc:
            body = exc.read().decode("utf-8")
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                data = {"message": body}
            return GitHubResponse(
                status_code=exc.code,
                data=data,
                headers=dict(exc.headers.items()),
            )


@dataclass
class GitHubClient:
    token: str | None = None
    transport: GitHubTransport = field(default_factory=UrllibGitHubTransport)
    api_base_url: str = GITHUB_API_BASE_URL

    @classmethod
    def from_environment(cls) -> GitHubClient:
        return cls(token=os.environ.get("GITHUB_TOKEN"))

    def get_repository(self, owner: str, repo: str) -> GitHubResponse:
        return self.transport.request(
            "GET",
            f"{self.api_base_url}/repos/{owner}/{repo}",
            self._headers(),
        )

    def get_root_contents(self, owner: str, repo: str, ref: str | None = None) -> GitHubResponse:
        return self.get_contents(owner, repo, "", ref=ref)

    def get_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str | None = None,
    ) -> GitHubResponse:
        url = f"{self.api_base_url}/repos/{owner}/{repo}/contents"
        if path:
            url = f"{url}/{path}"
        if ref:
            url = f"{url}?{urlencode({'ref': ref})}"
        return self.transport.request("GET", url, self._headers())

    def get_readme(self, owner: str, repo: str, ref: str | None = None) -> GitHubResponse:
        url = f"{self.api_base_url}/repos/{owner}/{repo}/readme"
        if ref:
            url = f"{url}?{urlencode({'ref': ref})}"
        return self.transport.request("GET", url, self._headers())

    def get_workflows(self, owner: str, repo: str) -> GitHubResponse:
        return self.transport.request(
            "GET",
            f"{self.api_base_url}/repos/{owner}/{repo}/actions/workflows",
            self._headers(),
        )

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "repotrust",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers


def scan_remote_github(
    target: Target,
    weights: dict[str, float] | None = None,
    client: GitHubClient | None = None,
) -> ScanResult:
    client = client or GitHubClient.from_environment()
    owner = target.owner or ""
    repo = target.repo or ""

    repository_response = client.get_repository(owner, repo)
    repository_finding = _finding_from_repository_response(repository_response)
    if repository_finding.id != "remote.github_metadata_collected":
        findings = [repository_finding]
        return ScanResult(
            target=target,
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    contents_response = client.get_root_contents(owner, repo, ref=target.ref)
    readme_response = client.get_readme(owner, repo, ref=target.ref)
    workflows_response = client.get_workflows(owner, repo)
    dependabot_yml_response = client.get_contents(
        owner,
        repo,
        ".github/dependabot.yml",
        ref=target.ref,
    )
    dependabot_yaml_response = client.get_contents(
        owner,
        repo,
        ".github/dependabot.yaml",
        ref=target.ref,
    )
    root_files = _root_file_paths(contents_response)
    github_security_response = _fetch_github_security_policy(
        client,
        owner,
        repo,
        target.ref,
        contents_response,
    )
    findings = [repository_finding]
    if target.subpath:
        findings.append(github_subpath_unsupported_finding(target.subpath))
    findings.extend(_repository_metadata_findings(repository_response))
    findings.extend(
        _partial_findings(
            contents_response,
            readme_response,
            workflows_response,
            dependabot_yml_response,
            dependabot_yaml_response,
            github_security_response,
        )
    )
    detected_files = _detected_files_from_remote(
        contents_response,
        readme_response,
        workflows_response,
        dependabot_yml_response,
        dependabot_yaml_response,
        github_security_response,
    )
    findings.extend(
        _remote_rules(
            detected_files,
            readme_response,
            contents_unknown=not 200 <= contents_response.status_code < 300,
            workflows_unknown=not 200 <= workflows_response.status_code < 300,
            dependabot_unknown=_all_dependabot_checks_failed(
                dependabot_yml_response,
                dependabot_yaml_response,
            ),
            security_policy_unknown=_security_policy_check_failed(
                github_security_response,
            ),
        )
    )

    return ScanResult(
        target=target,
        detected_files=detected_files,
        findings=findings,
        score=calculate_score(findings, weights=weights),
    )


def _finding_from_repository_response(response: GitHubResponse) -> Finding:
    if 200 <= response.status_code < 300:
        return Finding(
            id="remote.github_metadata_collected",
            category=Category.TARGET,
            severity=Severity.INFO,
            message="GitHub repository metadata was collected.",
            evidence="Repository metadata endpoint returned a successful response.",
            recommendation="Continue remote scan with repository contents and workflow metadata.",
        )

    if _is_rate_limited(response):
        return Finding(
            id="remote.github_rate_limited",
            category=Category.TARGET,
            severity=Severity.MEDIUM,
            message="GitHub API rate limit prevented remote scan completion.",
            evidence=f"GitHub API returned HTTP {response.status_code}.",
            recommendation="Retry later or provide a GITHUB_TOKEN with sufficient rate limit.",
        )

    if response.status_code in {401, 403}:
        return Finding(
            id="remote.github_unauthorized",
            category=Category.TARGET,
            severity=Severity.MEDIUM,
            message="GitHub API authentication or authorization failed.",
            evidence=f"GitHub API returned HTTP {response.status_code}.",
            recommendation="Provide a GITHUB_TOKEN with repository read access or verify repository visibility.",
        )

    if response.status_code == 404:
        return Finding(
            id="remote.github_not_found",
            category=Category.TARGET,
            severity=Severity.MEDIUM,
            message="GitHub repository was not found or is not visible.",
            evidence="GitHub API returned HTTP 404.",
            recommendation="Verify the owner/repo URL and repository visibility.",
        )

    return Finding(
        id="remote.github_api_error",
        category=Category.TARGET,
        severity=Severity.MEDIUM,
        message="GitHub API returned an unexpected error.",
        evidence=f"GitHub API returned HTTP {response.status_code}.",
        recommendation="Retry later or inspect GitHub API availability and repository permissions.",
    )


def _repository_metadata_findings(response: GitHubResponse) -> list[Finding]:
    findings = []
    if response.data.get("archived") is True:
        findings.append(
            Finding(
                id="remote.github_archived",
                category=Category.PROJECT_HYGIENE,
                severity=Severity.MEDIUM,
                message="GitHub repository is archived.",
                evidence="Repository metadata has archived=true.",
                recommendation="Treat the project as read-only unless a maintained fork or replacement is available.",
            )
        )
    if response.data.get("has_issues") is False:
        findings.append(
            Finding(
                id="remote.github_issues_disabled",
                category=Category.PROJECT_HYGIENE,
                severity=Severity.LOW,
                message="GitHub issue tracking is disabled.",
                evidence="Repository metadata has has_issues=false.",
                recommendation="Confirm where maintainers accept bug reports, security questions, and support requests before adopting the project.",
            )
        )
    return findings


def _is_rate_limited(response: GitHubResponse) -> bool:
    message = str(response.data.get("message", "")).lower()
    remaining = response.headers.get("x-ratelimit-remaining") or response.headers.get(
        "X-RateLimit-Remaining"
    )
    return response.status_code in {403, 429} and (
        remaining == "0" or "rate limit" in message or "secondary rate" in message
    )


def _partial_findings(
    contents_response: GitHubResponse,
    readme_response: GitHubResponse,
    workflows_response: GitHubResponse,
    dependabot_yml_response: GitHubResponse,
    dependabot_yaml_response: GitHubResponse,
    github_security_response: GitHubResponse | None,
) -> list[Finding]:
    findings = []
    if not 200 <= contents_response.status_code < 300:
        findings.append(
            _partial_scan_finding(
                REMOTE_CONTENTS_ENDPOINT,
                contents_response.status_code,
            )
        )
    if readme_response.status_code not in {200, 404}:
        findings.append(_partial_scan_finding(REMOTE_README_ENDPOINT, readme_response.status_code))
    if not 200 <= workflows_response.status_code < 300:
        findings.append(_partial_scan_finding(REMOTE_WORKFLOWS_ENDPOINT, workflows_response.status_code))
    if _all_dependabot_checks_failed(dependabot_yml_response, dependabot_yaml_response):
        findings.append(
            _partial_scan_finding(
                REMOTE_DEPENDABOT_ENDPOINT,
                dependabot_yml_response.status_code,
            )
        )
    if _security_policy_check_failed(github_security_response):
        findings.append(
            _partial_scan_finding(
                REMOTE_SECURITY_POLICY_ENDPOINT,
                github_security_response.status_code,
            )
        )
    return findings


def _partial_scan_finding(endpoint: str, status_code: int) -> Finding:
    return Finding(
        id="remote.github_partial_scan",
        category=Category.TARGET,
        severity=Severity.MEDIUM,
        message="GitHub remote scan completed with partial metadata.",
        evidence=f"{endpoint} endpoint returned HTTP {status_code}.",
        recommendation="Retry later or verify repository permissions before treating missing remote signals as absent.",
    )


def _detected_files_from_remote(
    contents_response: GitHubResponse,
    readme_response: GitHubResponse,
    workflows_response: GitHubResponse,
    dependabot_yml_response: GitHubResponse,
    dependabot_yaml_response: GitHubResponse,
    github_security_response: GitHubResponse | None,
) -> DetectedFiles:
    root_files = _root_file_paths(contents_response)
    readme = _readme_path(readme_response) or _first_match(root_files, README_NAMES)
    workflow_paths = _workflow_paths(workflows_response)
    return DetectedFiles(
        readme=readme,
        license=_first_match(root_files, LICENSE_NAMES),
        security=_security_path(root_files, github_security_response),
        ci_workflows=workflow_paths,
        dependency_manifests=_all_matches(root_files, DEPENDENCY_MANIFESTS),
        lockfiles=_all_matches(root_files, LOCKFILES),
        dependabot=_dependabot_path(dependabot_yml_response, dependabot_yaml_response),
    )


def _remote_rules(
    detected_files: DetectedFiles,
    readme_response: GitHubResponse,
    contents_unknown: bool,
    workflows_unknown: bool,
    dependabot_unknown: bool,
    security_policy_unknown: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    readme_text = _readme_text(readme_response)
    readme_unknown = detected_files.readme and readme_text is None
    if readme_unknown:
        findings.append(
            Finding(
                id="remote.readme_content_unavailable",
                category=Category.README_QUALITY,
                severity=Severity.MEDIUM,
                message="README exists but its content could not be fetched for remote analysis.",
                evidence=detected_files.readme,
                recommendation="Retry remote scan later or scan a local checkout for full README and install safety analysis.",
            )
        )
    else:
        findings.extend(readme_quality_rules(detected_files, readme_text or ""))
        findings.extend(install_safety_rules(detected_files, readme_text or ""))
    findings.extend(security_posture_rules(detected_files))
    findings.extend(project_hygiene_rules(detected_files))
    return _filter_unknown_remote_findings(
        findings,
        contents_unknown=contents_unknown,
        workflows_unknown=workflows_unknown,
        dependabot_unknown=dependabot_unknown,
        security_policy_unknown=security_policy_unknown,
    )


def _filter_unknown_remote_findings(
    findings: list[Finding],
    contents_unknown: bool,
    workflows_unknown: bool,
    dependabot_unknown: bool,
    security_policy_unknown: bool,
) -> list[Finding]:
    filtered = []
    for finding in findings:
        if contents_unknown and finding.id in {
            "readme.missing",
            "install.no_readme_to_audit",
            "security.no_policy",
            "security.no_lockfile",
            "hygiene.no_license",
            "hygiene.no_manifest",
        }:
            continue
        if workflows_unknown and finding.id == "security.no_ci":
            continue
        if dependabot_unknown and finding.id == "security.no_dependabot":
            continue
        if security_policy_unknown and finding.id == "security.no_policy":
            continue
        filtered.append(finding)
    return filtered


def _fetch_github_security_policy(
    client: GitHubClient,
    owner: str,
    repo: str,
    ref: str | None,
    contents_response: GitHubResponse,
) -> GitHubResponse | None:
    root_files = _root_file_paths(contents_response)
    if not 200 <= contents_response.status_code < 300:
        return None
    if _first_match(root_files, SECURITY_NAMES):
        return None
    return client.get_contents(owner, repo, GITHUB_SECURITY_PATH, ref=ref)


def _root_file_paths(response: GitHubResponse) -> list[str]:
    if not 200 <= response.status_code < 300 or not isinstance(response.data, list):
        return []
    paths = []
    for item in response.data:
        if not isinstance(item, dict) or item.get("type") != "file":
            continue
        path = item.get("path") or item.get("name")
        if isinstance(path, str):
            paths.append(path)
    return sorted(paths)


def _workflow_paths(response: GitHubResponse) -> list[str]:
    if not 200 <= response.status_code < 300 or not isinstance(response.data, dict):
        return []
    workflows = response.data.get("workflows")
    if not isinstance(workflows, list):
        return []
    paths = []
    for workflow in workflows:
        if not isinstance(workflow, dict):
            continue
        path = workflow.get("path")
        if isinstance(path, str):
            paths.append(path)
    return sorted(paths)


def _readme_path(response: GitHubResponse) -> str | None:
    if not 200 <= response.status_code < 300 or not isinstance(response.data, dict):
        return None
    path = response.data.get("path") or response.data.get("name")
    return path if isinstance(path, str) else None


def _readme_text(response: GitHubResponse) -> str | None:
    if not 200 <= response.status_code < 300 or not isinstance(response.data, dict):
        return None
    content = response.data.get("content")
    if not isinstance(content, str):
        return None
    if response.data.get("encoding") != "base64":
        return None
    try:
        return b64decode(content).decode("utf-8", errors="replace")
    except ValueError:
        return None


def _dependabot_path(
    yml_response: GitHubResponse,
    yaml_response: GitHubResponse,
) -> str | None:
    for response in (yml_response, yaml_response):
        if 200 <= response.status_code < 300 and isinstance(response.data, dict):
            path = response.data.get("path") or response.data.get("name")
            if isinstance(path, str):
                return path
    return None


def _security_path(
    root_files: list[str],
    github_security_response: GitHubResponse | None,
) -> str | None:
    root_security = _first_match(root_files, SECURITY_NAMES)
    if root_security:
        return root_security
    if github_security_response is None:
        return None
    if 200 <= github_security_response.status_code < 300 and isinstance(
        github_security_response.data,
        dict,
    ):
        path = github_security_response.data.get("path") or github_security_response.data.get(
            "name"
        )
        if path == GITHUB_SECURITY_PATH:
            return path
        if path == "SECURITY.md":
            return GITHUB_SECURITY_PATH
    return None


def _security_policy_check_failed(response: GitHubResponse | None) -> bool:
    if response is None:
        return False
    return response.status_code not in {200, 404}


def _all_dependabot_checks_failed(
    yml_response: GitHubResponse,
    yaml_response: GitHubResponse,
) -> bool:
    acceptable = {200, 404}
    return (
        yml_response.status_code not in acceptable
        and yaml_response.status_code not in acceptable
    )


def _first_match(paths: list[str], candidates: set[str]) -> str | None:
    matches = _all_matches(paths, candidates)
    return matches[0] if matches else None


def _all_matches(paths: list[str], candidates: set[str]) -> list[str]:
    return [path for path in paths if path in candidates]

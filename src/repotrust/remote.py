from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from .scoring import calculate_score


GITHUB_API_BASE_URL = "https://api.github.com"


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
    response = client.get_repository(target.owner or "", target.repo or "")
    finding = _finding_from_repository_response(response)
    findings = [finding]
    return ScanResult(
        target=target,
        detected_files=DetectedFiles(),
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


def _is_rate_limited(response: GitHubResponse) -> bool:
    message = str(response.data.get("message", "")).lower()
    remaining = response.headers.get("x-ratelimit-remaining") or response.headers.get(
        "X-RateLimit-Remaining"
    )
    return response.status_code in {403, 429} and (
        remaining == "0" or "rate limit" in message or "secondary rate" in message
    )

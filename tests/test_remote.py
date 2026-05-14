from base64 import b64encode
import json

import pytest

from repotrust.models import Target
from repotrust.remote import GitHubClient, GitHubResponse, scan_remote_github
from repotrust.reports import render_html, render_json, render_markdown


class FakeTransport:
    def __init__(self, responses):
        self.responses = responses if isinstance(responses, list) else [responses]
        self.requests = []

    def request(self, method, url, headers):
        self.requests.append((method, url, headers))
        index = min(len(self.requests) - 1, len(self.responses) - 1)
        return self.responses[index]


def _target(subpath=None):
    return Target(
        raw=(
            "https://github.com/owner/repo/tree/main/packages/example"
            if subpath
            else "https://github.com/owner/repo"
        ),
        kind="github",
        host="github.com",
        owner="owner",
        repo="repo",
        ref="main" if subpath else None,
        subpath=subpath,
    )


def _scan(response, token=None, subpath=None):
    transport = FakeTransport(response)
    client = GitHubClient(token=token, transport=transport)
    return scan_remote_github(_target(subpath=subpath), client=client), transport


def _readme(text=None):
    body = text or """# Good Python Project

Good Python Project is a small example package used by RepoTrust tests to represent a repository with clear documentation, safe installation guidance, security policy, CI, and dependency metadata.

## Installation

```bash
pip install good-python-project
```

## Usage

```bash
good-python-project scan .
```

## Contributing

Open issues for bugs, send pull requests for small fixes, and review the changelog before upgrading between releases.
"""
    return {
        "name": "README.md",
        "path": "README.md",
        "encoding": "base64",
        "content": b64encode(body.encode()).decode(),
    }


def _successful_responses(metadata=None, contents=None, readme=None):
    return [
        GitHubResponse(status_code=200, data=metadata or {"full_name": "owner/repo"}),
        GitHubResponse(
            status_code=200,
            data=contents
            or [
                {"type": "file", "name": "README.md", "path": "README.md"},
                {"type": "file", "name": "LICENSE", "path": "LICENSE"},
                {"type": "file", "name": "SECURITY.md", "path": "SECURITY.md"},
                {"type": "file", "name": "pyproject.toml", "path": "pyproject.toml"},
                {"type": "file", "name": "pylock.toml", "path": "pylock.toml"},
                {"type": "dir", "name": ".github", "path": ".github"},
            ],
        ),
        GitHubResponse(status_code=200, data=readme or _readme()),
    ]


def test_remote_success_detects_root_files_and_freezes_endpoint_surface():
    result, transport = _scan(_successful_responses())

    assert [finding.id for finding in result.findings] == ["remote.github_metadata_collected"]
    assert result.detected_files.readme == "README.md"
    assert result.detected_files.license == "LICENSE"
    assert result.detected_files.security == "SECURITY.md"
    assert result.detected_files.dependency_manifests == ["pyproject.toml"]
    assert result.detected_files.lockfiles == ["pylock.toml"]
    assert result.detected_files.ci_workflows == []
    assert result.detected_files.dependabot is None
    assert result.score.total == 100
    assert len(transport.requests) == 3
    assert transport.requests[0][1] == "https://api.github.com/repos/owner/repo"
    forbidden = [
        "/actions/workflows",
        "dependabot",
        ".github/SECURITY.md",
        "/releases/",
        "/tags",
        "/commits/",
    ]
    assert all(marker not in request[1] for request in transport.requests for marker in forbidden)


def test_remote_metadata_flags_affect_project_hygiene_score():
    archived_result, _ = _scan(
        _successful_responses(metadata={"full_name": "owner/repo", "archived": True})
    )
    issues_result, _ = _scan(
        _successful_responses(metadata={"full_name": "owner/repo", "has_issues": False})
    )

    assert [finding.id for finding in archived_result.findings[:2]] == [
        "remote.github_metadata_collected",
        "remote.github_archived",
    ]
    assert archived_result.score.total == 96
    assert [finding.id for finding in issues_result.findings[:2]] == [
        "remote.github_metadata_collected",
        "remote.github_issues_disabled",
    ]
    assert issues_result.score.total == 98


def test_remote_subpath_url_reports_root_scope_limitation():
    result, _ = _scan(_successful_responses(), subpath="packages/example")

    ids = [finding.id for finding in result.findings]
    assert "target.github_subpath_unsupported" in ids
    assert result.score.total == 85
    assert result.assessment.coverage == "partial"
    assert "does not assess only the requested subdirectory" in result.assessment.reasons[0]


def test_remote_report_rendering_uses_existing_contract():
    result, _ = _scan(_successful_responses())

    json_report = json.loads(render_json(result))
    markdown_report = render_markdown(result)

    assert json_report["schema_version"] == "1.2"
    assert json_report["assessment"]["verdict"] == "usable_by_current_checks"
    assert json_report["assessment"]["coverage"] == "full"
    assert json_report["target"]["kind"] == "github"
    assert json_report["detected_files"]["readme"] == "README.md"
    assert json_report["findings"][0]["id"] == "remote.github_metadata_collected"
    assert "# RepoTrust Report" in markdown_report
    assert "remote.github_metadata_collected" in markdown_report


def test_remote_contents_partial_failure_preserves_partial_contract():
    result, _ = _scan(
        [
            GitHubResponse(status_code=200, data={"full_name": "owner/repo"}),
            GitHubResponse(status_code=500),
            GitHubResponse(status_code=404),
        ]
    )

    data = json.loads(render_json(result))
    html_report = render_html(result)
    ids = [finding.id for finding in result.findings]

    assert ids[:2] == ["remote.github_metadata_collected", "remote.github_partial_scan"]
    assert "readme.missing" not in ids
    assert "hygiene.no_license" not in ids
    assert data["score"]["total"] == 85
    assert data["assessment"]["coverage"] == "partial"
    assert data["assessment"]["confidence"] == "medium"
    assert "repository contents endpoint returned HTTP 500." == data["findings"][1]["evidence"]
    assert "remote.github_partial_scan" in html_report
    assert "확인 못함" in html_report


def test_remote_readme_partial_failure_preserves_root_contents_detection():
    result, _ = _scan(
        [
            GitHubResponse(status_code=200, data={"full_name": "owner/repo"}),
            GitHubResponse(
                status_code=200,
                data=[{"type": "file", "name": "README.md", "path": "README.md"}],
            ),
            GitHubResponse(status_code=500),
        ]
    )

    ids = [finding.id for finding in result.findings]
    assert ids[:2] == ["remote.github_metadata_collected", "remote.github_partial_scan"]
    assert result.detected_files.readme == "README.md"
    assert "repository README" in result.findings[1].evidence
    assert "remote.readme_content_unavailable" in ids
    assert "security.no_ci" not in ids


def test_remote_detects_risky_readme_install_commands():
    readme = """# Risky Project

Risky Project is a deliberately unsafe example with enough prose to exercise remote README analysis and install command detection.

## Installation

```bash
curl https://example.com/install.sh | sh
```

## Usage

```bash
risky run
```

## Contributing

Open issues before sending changes.
"""

    result, _ = _scan(_successful_responses(readme=_readme(readme)))

    assert "install.risky.shell_pipe_install" in {finding.id for finding in result.findings}


def test_remote_unauthorized_finding_does_not_leak_token():
    result, transport = _scan(GitHubResponse(status_code=401), token="secret-token")

    finding = result.findings[0]
    assert finding.id == "remote.github_unauthorized"
    assert "secret-token" not in finding.evidence
    assert "secret-token" not in finding.message
    assert transport.requests[0][2]["Authorization"] == "Bearer secret-token"


@pytest.mark.parametrize(
    ("response", "finding_id"),
    [
        (GitHubResponse(status_code=404), "remote.github_not_found"),
        (GitHubResponse(status_code=500), "remote.github_api_error"),
        (
            GitHubResponse(
                status_code=403,
                data={"message": "API rate limit exceeded"},
                headers={"x-ratelimit-remaining": "0"},
            ),
            "remote.github_rate_limited",
        ),
    ],
)
def test_remote_metadata_failure_findings(response, finding_id):
    result, _ = _scan(response)

    assert result.findings[0].id == finding_id
    assert result.score.total == 60
    assert result.assessment.verdict == "insufficient_evidence"
    assert result.assessment.coverage == "failed"

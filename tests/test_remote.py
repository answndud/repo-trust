from base64 import b64encode

from repotrust.models import Target
from repotrust.remote import GitHubClient, GitHubResponse, scan_remote_github
from repotrust.reports import render_json, render_markdown


class FakeTransport:
    def __init__(self, responses):
        if isinstance(responses, list):
            self.responses = responses
        else:
            self.responses = [responses]
        self.requests = []

    def request(self, method, url, headers):
        self.requests.append((method, url, headers))
        index = min(len(self.requests) - 1, len(self.responses) - 1)
        return self.responses[index]


def _target():
    return Target(
        raw="https://github.com/owner/repo",
        kind="github",
        host="github.com",
        owner="owner",
        repo="repo",
    )


def _scan(response, token=None):
    transport = FakeTransport(response)
    client = GitHubClient(token=token, transport=transport)
    return scan_remote_github(_target(), client=client), transport


def _successful_responses():
    readme = """# Good Python Project

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
    return [
        GitHubResponse(status_code=200, data={"full_name": "owner/repo"}),
        GitHubResponse(
            status_code=200,
            data=[
                {"type": "file", "name": "README.md", "path": "README.md"},
                {"type": "file", "name": "LICENSE", "path": "LICENSE"},
                {"type": "file", "name": "SECURITY.md", "path": "SECURITY.md"},
                {"type": "file", "name": "pyproject.toml", "path": "pyproject.toml"},
                {"type": "file", "name": "pylock.toml", "path": "pylock.toml"},
                {"type": "dir", "name": ".github", "path": ".github"},
            ],
        ),
        GitHubResponse(
            status_code=200,
            data={
                "name": "README.md",
                "path": "README.md",
                "encoding": "base64",
                "content": b64encode(readme.encode()).decode(),
            },
        ),
        GitHubResponse(
            status_code=200,
            data={"workflows": [{"path": ".github/workflows/ci.yml"}]},
        ),
        GitHubResponse(
            status_code=200,
            data={"name": "dependabot.yml", "path": ".github/dependabot.yml"},
        ),
        GitHubResponse(status_code=404),
    ]


def test_remote_success_collects_repository_metadata_boundary():
    result, transport = _scan(_successful_responses())

    assert [finding.id for finding in result.findings] == ["remote.github_metadata_collected"]
    assert result.findings[0].severity.value == "info"
    assert transport.requests[0][0] == "GET"
    assert transport.requests[0][1] == "https://api.github.com/repos/owner/repo"


def test_remote_success_detects_files_from_contents_and_workflows():
    result, _ = _scan(_successful_responses())

    assert result.detected_files.readme == "README.md"
    assert result.detected_files.license == "LICENSE"
    assert result.detected_files.security == "SECURITY.md"
    assert result.detected_files.dependency_manifests == ["pyproject.toml"]
    assert result.detected_files.lockfiles == ["pylock.toml"]
    assert result.detected_files.ci_workflows == [".github/workflows/ci.yml"]
    assert result.detected_files.dependabot == ".github/dependabot.yml"
    assert result.score.total == 100


def test_remote_report_rendering_uses_existing_contract():
    result, _ = _scan(_successful_responses())

    json_report = render_json(result)
    markdown_report = render_markdown(result)

    assert '"schema_version": "1.0"' in json_report
    assert '"kind": "github"' in json_report
    assert '"readme": "README.md"' in json_report
    assert "# RepoTrust Report" in markdown_report
    assert "remote.github_metadata_collected" in markdown_report


def test_remote_contents_partial_failure_does_not_look_like_missing_files():
    result, _ = _scan(
        [
            GitHubResponse(status_code=200, data={"full_name": "owner/repo"}),
            GitHubResponse(status_code=500),
            GitHubResponse(status_code=404),
            GitHubResponse(
                status_code=200,
                data={"workflows": [{"path": ".github/workflows/ci.yml"}]},
            ),
            GitHubResponse(status_code=404),
            GitHubResponse(status_code=404),
        ]
    )

    ids = [finding.id for finding in result.findings]
    assert ids[:2] == ["remote.github_metadata_collected", "remote.github_partial_scan"]
    assert result.detected_files.readme is None
    assert result.detected_files.ci_workflows == [".github/workflows/ci.yml"]
    assert "repository contents" in result.findings[1].evidence


def test_remote_workflows_partial_failure_preserves_contents_detection():
    result, _ = _scan(
        [
            GitHubResponse(status_code=200, data={"full_name": "owner/repo"}),
            GitHubResponse(
                status_code=200,
                data=[{"type": "file", "name": "README.md", "path": "README.md"}],
            ),
            GitHubResponse(status_code=500),
            GitHubResponse(status_code=403),
            GitHubResponse(status_code=404),
            GitHubResponse(status_code=404),
        ]
    )

    ids = [finding.id for finding in result.findings]
    assert ids[:3] == [
        "remote.github_metadata_collected",
        "remote.github_partial_scan",
        "remote.github_partial_scan",
    ]
    assert result.detected_files.readme == "README.md"
    assert result.detected_files.ci_workflows == []
    assert "repository README" in result.findings[1].evidence
    assert "GitHub Actions workflows" in result.findings[2].evidence


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
    responses = _successful_responses()
    responses[2] = GitHubResponse(
        status_code=200,
        data={
            "name": "README.md",
            "path": "README.md",
            "encoding": "base64",
            "content": b64encode(readme.encode()).decode(),
        },
    )

    result, _ = _scan(responses)

    assert "install.risky.shell_pipe_install" in {finding.id for finding in result.findings}


def test_remote_unauthorized_finding_does_not_leak_token():
    result, transport = _scan(GitHubResponse(status_code=401), token="secret-token")

    finding = result.findings[0]
    assert finding.id == "remote.github_unauthorized"
    assert "secret-token" not in finding.evidence
    assert "secret-token" not in finding.message
    assert transport.requests[0][2]["Authorization"] == "Bearer secret-token"


def test_remote_not_found_finding():
    result, _ = _scan(GitHubResponse(status_code=404))

    assert result.findings[0].id == "remote.github_not_found"


def test_remote_rate_limited_finding_from_header():
    result, _ = _scan(
        GitHubResponse(
            status_code=403,
            data={"message": "API rate limit exceeded"},
            headers={"x-ratelimit-remaining": "0"},
        )
    )

    assert result.findings[0].id == "remote.github_rate_limited"


def test_remote_api_error_finding():
    result, _ = _scan(GitHubResponse(status_code=500))

    assert result.findings[0].id == "remote.github_api_error"

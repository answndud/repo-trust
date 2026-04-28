from repotrust.models import Target
from repotrust.remote import GitHubClient, GitHubResponse, scan_remote_github


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
            data={"workflows": [{"path": ".github/workflows/ci.yml"}]},
        ),
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


def test_remote_contents_partial_failure_does_not_look_like_missing_files():
    result, _ = _scan(
        [
            GitHubResponse(status_code=200, data={"full_name": "owner/repo"}),
            GitHubResponse(status_code=500),
            GitHubResponse(
                status_code=200,
                data={"workflows": [{"path": ".github/workflows/ci.yml"}]},
            ),
        ]
    )

    ids = [finding.id for finding in result.findings]
    assert ids == ["remote.github_metadata_collected", "remote.github_partial_scan"]
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
            GitHubResponse(status_code=403),
        ]
    )

    ids = [finding.id for finding in result.findings]
    assert ids == ["remote.github_metadata_collected", "remote.github_partial_scan"]
    assert result.detected_files.readme == "README.md"
    assert result.detected_files.ci_workflows == []
    assert "GitHub Actions workflows" in result.findings[1].evidence


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

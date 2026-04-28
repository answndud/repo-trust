from repotrust.models import Target
from repotrust.remote import GitHubClient, GitHubResponse, scan_remote_github


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.requests = []

    def request(self, method, url, headers):
        self.requests.append((method, url, headers))
        return self.response


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


def test_remote_success_collects_repository_metadata_boundary():
    result, transport = _scan(GitHubResponse(status_code=200, data={"full_name": "owner/repo"}))

    assert [finding.id for finding in result.findings] == ["remote.github_metadata_collected"]
    assert result.findings[0].severity.value == "info"
    assert transport.requests[0][0] == "GET"
    assert transport.requests[0][1] == "https://api.github.com/repos/owner/repo"


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

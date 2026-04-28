from repotrust.targets import parse_github_url, parse_target


def test_parse_basic_github_url():
    target = parse_github_url("https://github.com/owner/repo")

    assert target is not None
    assert target.kind == "github"
    assert target.host == "github.com"
    assert target.owner == "owner"
    assert target.repo == "repo"


def test_parse_github_git_suffix():
    target = parse_github_url("https://github.com/owner/repo.git")

    assert target is not None
    assert target.repo == "repo"


def test_parse_github_tree_url():
    target = parse_github_url("https://github.com/owner/repo/tree/main/docs")

    assert target is not None
    assert target.ref == "main"
    assert target.subpath == "docs"


def test_invalid_url_is_not_github_target():
    assert parse_github_url("https://example.com/owner/repo") is None


def test_local_path_that_mentions_github_is_local():
    target = parse_target("github.com/owner/repo")

    assert target.kind == "local"


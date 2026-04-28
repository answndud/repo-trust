from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from .models import Target


def parse_target(raw_target: str) -> Target:
    github_target = parse_github_url(raw_target)
    if github_target is not None:
        return github_target

    return Target(raw=raw_target, kind="local", path=str(Path(raw_target).expanduser()))


def parse_github_url(raw_url: str) -> Target | None:
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        return None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None

    owner = parts[0]
    repo = parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not owner or not repo:
        return None

    ref = None
    subpath = None
    if len(parts) >= 5 and parts[2] in {"tree", "blob"}:
        ref = parts[3]
        subpath = "/".join(parts[4:])

    return Target(
        raw=raw_url,
        kind="github",
        host="github.com",
        owner=owner,
        repo=repo,
        ref=ref,
        subpath=subpath,
    )


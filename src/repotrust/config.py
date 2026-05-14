from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RepoTrustConfig:
    fail_under: int | None = None


def load_config(path: Path) -> RepoTrustConfig:
    config_path = path.expanduser()
    if not config_path.is_file():
        raise ConfigError(f"Config file does not exist: {config_path}")

    try:
        with config_path.open("rb") as config_file:
            data = tomllib.load(config_file)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in config file: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Config file must contain a TOML table.")

    unknown_sections = set(data) - {"policy"}
    if unknown_sections:
        sections = ", ".join(sorted(unknown_sections))
        raise ConfigError(f"Unknown config section(s): {sections}")

    return RepoTrustConfig(fail_under=_parse_policy(data.get("policy", {})))


def _parse_policy(raw_policy: Any) -> int | None:
    if raw_policy is None:
        return None
    if not isinstance(raw_policy, dict):
        raise ConfigError("[policy] must be a TOML table.")

    unknown_keys = set(raw_policy) - {"fail_under"}
    if unknown_keys:
        keys = ", ".join(sorted(unknown_keys))
        raise ConfigError(f"Unknown [policy] key(s): {keys}")

    if "fail_under" not in raw_policy:
        return None

    fail_under = raw_policy["fail_under"]
    if isinstance(fail_under, bool) or not isinstance(fail_under, int):
        raise ConfigError("policy.fail_under must be an integer from 0 to 100.")
    if fail_under < 0 or fail_under > 100:
        raise ConfigError("policy.fail_under must be an integer from 0 to 100.")
    return fail_under

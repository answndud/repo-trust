from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from .scoring import WEIGHTS


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RepoTrustConfig:
    fail_under: int | None = None
    weights: dict[str, float] | None = None


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

    unknown_sections = set(data) - {"policy", "weights"}
    if unknown_sections:
        sections = ", ".join(sorted(unknown_sections))
        raise ConfigError(f"Unknown config section(s): {sections}")

    fail_under = _parse_policy(data.get("policy", {}))
    weights = _parse_weights(data.get("weights"))
    return RepoTrustConfig(fail_under=fail_under, weights=weights)


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


def _parse_weights(raw_weights: Any) -> dict[str, float] | None:
    if raw_weights is None:
        return None
    if not isinstance(raw_weights, dict):
        raise ConfigError("[weights] must be a TOML table.")

    expected_keys = set(WEIGHTS)
    actual_keys = set(raw_weights)
    missing = expected_keys - actual_keys
    unknown = actual_keys - expected_keys
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing: {', '.join(sorted(missing))}")
        if unknown:
            details.append(f"unknown: {', '.join(sorted(unknown))}")
        raise ConfigError("[weights] must define exactly these categories (" + "; ".join(details) + ").")

    weights: dict[str, float] = {}
    for key, value in raw_weights.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ConfigError(f"weights.{key} must be a non-negative number.")
        if value < 0:
            raise ConfigError(f"weights.{key} must be a non-negative number.")
        weights[key] = float(value)

    total = sum(weights.values())
    if abs(total - 1.0) > 1e-6:
        raise ConfigError("weights must sum to 1.0.")
    return weights


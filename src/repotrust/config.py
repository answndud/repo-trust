from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from .models import Finding, ScanResult, Severity
from .scoring import WEIGHTS, calculate_score


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RepoTrustConfig:
    fail_under: int | None = None
    weights: dict[str, float] | None = None
    disabled_findings: frozenset[str] = field(default_factory=frozenset)
    severity_overrides: dict[str, str] = field(default_factory=dict)
    profile_min_verdicts: dict[str, str] = field(default_factory=dict)


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

    unknown_sections = set(data) - {
        "policy",
        "rules",
        "severity_overrides",
        "weights",
    }
    if unknown_sections:
        sections = ", ".join(sorted(unknown_sections))
        raise ConfigError(f"Unknown config section(s): {sections}")

    fail_under, profile_min_verdicts = _parse_policy(data.get("policy", {}))
    weights = _parse_weights(data.get("weights"))
    disabled_findings = _parse_rules(data.get("rules"))
    severity_overrides = _parse_severity_overrides(data.get("severity_overrides"))
    return RepoTrustConfig(
        fail_under=fail_under,
        weights=weights,
        disabled_findings=disabled_findings,
        severity_overrides=severity_overrides,
        profile_min_verdicts=profile_min_verdicts,
    )


def apply_config_policy(result: ScanResult, config: RepoTrustConfig) -> ScanResult:
    if not config.disabled_findings and not config.severity_overrides:
        return result

    findings = []
    for finding in result.findings:
        if finding.id in config.disabled_findings:
            continue
        severity = config.severity_overrides.get(finding.id)
        if severity is not None:
            finding = _replace_finding_severity(finding, Severity(severity))
        findings.append(finding)

    return ScanResult(
        target=result.target,
        detected_files=result.detected_files,
        findings=findings,
        score=calculate_score(findings, weights=config.weights),
        generated_at=result.generated_at,
    )


def _replace_finding_severity(finding: Finding, severity: Severity) -> Finding:
    return Finding(
        id=finding.id,
        category=finding.category,
        severity=severity,
        message=finding.message,
        evidence=finding.evidence,
        recommendation=finding.recommendation,
    )


def _parse_policy(raw_policy: Any) -> tuple[int | None, dict[str, str]]:
    if raw_policy is None:
        return None, {}
    if not isinstance(raw_policy, dict):
        raise ConfigError("[policy] must be a TOML table.")

    unknown_keys = set(raw_policy) - {"fail_under", "profiles"}
    if unknown_keys:
        keys = ", ".join(sorted(unknown_keys))
        raise ConfigError(f"Unknown [policy] key(s): {keys}")

    profile_min_verdicts = _parse_profile_policy(raw_policy.get("profiles"))

    if "fail_under" not in raw_policy:
        return None, profile_min_verdicts

    fail_under = raw_policy["fail_under"]
    if isinstance(fail_under, bool) or not isinstance(fail_under, int):
        raise ConfigError("policy.fail_under must be an integer from 0 to 100.")
    if fail_under < 0 or fail_under > 100:
        raise ConfigError("policy.fail_under must be an integer from 0 to 100.")
    return fail_under, profile_min_verdicts


def _parse_profile_policy(raw_profiles: Any) -> dict[str, str]:
    if raw_profiles is None:
        return {}
    if not isinstance(raw_profiles, dict):
        raise ConfigError("[policy.profiles] must be a TOML table.")

    expected_profiles = {"install", "dependency", "agent_delegate"}
    unknown_profiles = set(raw_profiles) - expected_profiles
    if unknown_profiles:
        profiles = ", ".join(sorted(unknown_profiles))
        raise ConfigError(f"Unknown [policy.profiles] key(s): {profiles}")

    parsed = {}
    for profile, verdict in raw_profiles.items():
        if not isinstance(verdict, str) or verdict not in VERDICT_RANK:
            raise ConfigError(
                f"policy.profiles.{profile} must be one of: "
                + ", ".join(VERDICT_RANK)
                + "."
            )
        parsed[profile] = verdict
    return parsed


def _parse_rules(raw_rules: Any) -> frozenset[str]:
    if raw_rules is None:
        return frozenset()
    if not isinstance(raw_rules, dict):
        raise ConfigError("[rules] must be a TOML table.")

    unknown_keys = set(raw_rules) - {"disabled"}
    if unknown_keys:
        keys = ", ".join(sorted(unknown_keys))
        raise ConfigError(f"Unknown [rules] key(s): {keys}")

    disabled = raw_rules.get("disabled", [])
    if not isinstance(disabled, list) or not all(
        isinstance(finding_id, str) for finding_id in disabled
    ):
        raise ConfigError("rules.disabled must be a list of finding ID strings.")
    return frozenset(disabled)


def _parse_severity_overrides(raw_overrides: Any) -> dict[str, str]:
    if raw_overrides is None:
        return {}
    if not isinstance(raw_overrides, dict):
        raise ConfigError("[severity_overrides] must be a TOML table.")

    parsed = {}
    allowed = {severity.value for severity in Severity}
    for finding_id, severity in raw_overrides.items():
        if not isinstance(finding_id, str):
            raise ConfigError("[severity_overrides] keys must be finding ID strings.")
        if not isinstance(severity, str) or severity not in allowed:
            raise ConfigError(
                f"severity_overrides.{finding_id} must be one of: "
                + ", ".join(sorted(allowed))
                + "."
            )
        parsed[finding_id] = severity
    return parsed


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


VERDICT_RANK = {
    "do_not_install_before_review": 0,
    "insufficient_evidence": 1,
    "usable_after_review": 2,
    "usable_by_current_checks": 3,
}

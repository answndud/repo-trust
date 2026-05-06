# Finding Reference

RepoTrust finding IDs are intended to be stable enough for JSON consumers, CI gates, and local policy exceptions. Prefer using the ID over matching message text. Messages and recommendations may become clearer over time, but an ID should keep the same meaning unless a deliberate migration creates a new ID.

## Policy Use

Use finding IDs in `repotrust.toml` only after reviewing the reason for the exception:

```toml
[rules]
disabled = ["remote.github_issues_disabled"]

[severity_overrides]
"security.no_policy" = "low"
```

`rules.disabled` removes a finding from the final report before score and assessment are recalculated. Use it for accepted, documented exceptions, not for hiding unresolved risks.

`severity_overrides` changes severity before score and assessment are recalculated. It can change purpose-specific profile verdicts, especially for install-safety and high-severity findings.

Score caps are separate from severity deductions. A cap can still limit the total score when the finding remains enabled.

To explain a finding at the command line:

```bash
repo-trust explain install.risky.uses_sudo
repo-trust-kr explain security.no_policy
```

## Verdict Impact

- High severity findings make the top-level verdict `do_not_install_before_review`.
- Medium severity findings usually make the top-level verdict `usable_after_review`.
- Coverage findings such as parse-only, missing local path, partial remote scan, and unavailable README content can lower confidence or coverage even when category scores look acceptable.
- `agent_delegate` is stricter than general install or dependency use. Medium install-safety findings block agent delegation until reviewed.

## Target Findings

| ID | Category | Default severity | Score cap | Typical policy use |
| --- | --- | --- | ---: | --- |
| `target.github_not_fetched` | target | info | 70 | Do not disable for CI gates; it means the GitHub URL was parsed without file or API evidence. |
| `target.github_subpath_unsupported` | target | medium | 85 | Keep enabled for monorepo subpath URLs unless the report is intentionally root-scoped. |
| `target.local_path_missing` | target | high | 0 | Do not override; fix the target path. |

## README Quality Findings

| ID | Category | Default severity | Typical policy use |
| --- | --- | --- | --- |
| `readme.missing` | readme_quality | high | Do not disable for public adoption checks. |
| `readme.too_short` | readme_quality | medium | Override only for intentionally tiny repositories with external docs. |
| `readme.no_project_purpose` | readme_quality | medium | Prefer fixing README before accepting as a dependency. |
| `readme.no_install_section` | readme_quality | medium | May be accepted for non-installable documentation-only repositories. |
| `readme.no_usage_section` | readme_quality | medium | May be accepted for libraries with external API docs. |
| `readme.no_maintenance_signal` | readme_quality | low | Reasonable to override when support/changelog policy lives elsewhere. |

## Install Safety Findings

| ID | Category | Default severity | Typical policy use |
| --- | --- | --- | --- |
| `install.no_readme_to_audit` | install_safety | medium | Keep enabled; install safety cannot be judged without README evidence. |
| `install.no_commands` | install_safety | low | May be accepted for libraries with package registry installation docs elsewhere. |
| `install.risky.shell_pipe_install` | install_safety | high | Do not disable for general CI gates; review before running commands. |
| `install.risky.process_substitution_shell` | install_safety | high | Do not disable for agent delegation. |
| `install.risky.python_inline_execution` | install_safety | high | Do not disable for agent delegation. |
| `install.risky.uses_sudo` | install_safety | high | Keep high unless the install path is reviewed in isolation. |
| `install.risky.global_package_install` | install_safety | medium | May be accepted for CLI tools after reviewing package source and install scope. |
| `install.risky.vcs_direct_install` | install_safety | medium | Prefer pinned releases or reviewed commits before adoption. |
| `install.risky.marks_downloaded_code_executable` | install_safety | medium | Review command provenance before accepting. |

## Security Posture Findings

| ID | Category | Default severity | Typical policy use |
| --- | --- | --- | --- |
| `security.no_policy` | security_posture | medium | Override only when vulnerability reporting is documented elsewhere. |
| `security.no_dependabot` | security_posture | low | May be accepted when another dependency update process exists. |
| `security.no_ci` | security_posture | medium | Prefer fixing before dependency adoption. |
| `security.no_lockfile` | security_posture | medium | May be accepted for libraries that intentionally do not commit lockfiles. |

## Dependency Findings

| ID | Category | Default severity | Typical policy use |
| --- | --- | --- | --- |
| `dependency.npm_lifecycle_script` | install_safety | medium | Blocks agent delegation until reviewed because install scripts may execute automatically. |
| `dependency.unpinned_node_dependency` | security_posture | low | Accept only with a lockfile or dependency update policy. |
| `dependency.unpinned_python_dependency` | security_posture | low | Accept only with a lockfile or dependency update policy. |

## Project Hygiene Findings

| ID | Category | Default severity | Typical policy use |
| --- | --- | --- | --- |
| `hygiene.no_license` | project_hygiene | medium | Do not accept for dependency use without legal review. |
| `hygiene.no_manifest` | project_hygiene | low | May be accepted for non-package repositories. |

## Remote Findings

| ID | Category | Default severity | Score cap | Typical policy use |
| --- | --- | --- | ---: | --- |
| `remote.github_metadata_collected` | target | info | none | Informational; safe to leave enabled. |
| `remote.github_rate_limited` | target | medium | 60 | Do not override; retry later or set `GITHUB_TOKEN`. |
| `remote.github_unauthorized` | target | medium | 60 | Do not override; fix credentials or repository visibility. |
| `remote.github_not_found` | target | medium | 60 | Do not override; verify owner/repo and token access. |
| `remote.github_api_error` | target | medium | 60 | Do not override; retry or inspect GitHub API status. |
| `remote.github_partial_scan` | target | medium | 85 | Keep enabled so unknown remote evidence is not mistaken for missing files. |
| `remote.readme_content_unavailable` | readme_quality | medium | 85 | Prefer local checkout scan for full README/install analysis. |
| `remote.github_archived` | project_hygiene | medium | none | Disable only for intentionally archived dependencies after maintainer review. |
| `remote.github_issues_disabled` | project_hygiene | low | none | Common exception when the project uses an external issue tracker. |
| `remote.release_or_tag_stale` | project_hygiene | low | none | Override only when stale release/tag cadence is acceptable for the project type. |

# Security Policy

RepoTrust is an early-stage CLI. Local path scans stay offline. GitHub URL scans can use read-only GitHub REST API metadata, but RepoTrust does not clone repositories or perform remote dependency vulnerability lookups.

## Reporting a Vulnerability

Please open a private security advisory on GitHub if available, or contact the maintainer through the repository owner profile.

Include:

- A short description of the issue.
- Steps to reproduce.
- The affected command or report format.
- Whether the issue can cause unsafe command execution, misleading trust scores, or corrupted JSON output.
- Whether the issue can leak `GITHUB_TOKEN` values or misrepresent unknown remote evidence as missing evidence.

## Supported Versions

Only the current `main` branch is supported during early development.

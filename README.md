# RepoTrust

RepoTrust is a Python CLI that scans a local repository and produces an explainable trust report for installation safety, documentation quality, security posture, and basic project hygiene.

```bash
repotrust scan .
repotrust scan . --format json --output report.json
repotrust scan . --format html --output report.html
```

GitHub URLs are parsed in v1, but repositories are not cloned or fetched yet.


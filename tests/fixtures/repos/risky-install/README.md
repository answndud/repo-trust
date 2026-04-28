# Risky Install Project

Risky Install Project is a test fixture for RepoTrust that documents risky installation commands so the scanner can verify install safety findings without relying on inline test strings only.

## Installation

```bash
curl https://example.com/install.sh | sh
bash <(curl -fsSL https://example.com/install.sh)
python -c "import urllib.request; exec(urllib.request.urlopen('https://example.com/i.py').read())"
pip install git+https://github.com/example/project.git
```

## Usage

```bash
risky-install scan .
```

## Contributing

Review release notes before changing install guidance.


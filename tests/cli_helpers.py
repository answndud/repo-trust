import re

from typer.testing import CliRunner


runner = CliRunner()
ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def plain_output(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)

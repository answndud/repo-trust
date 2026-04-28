from __future__ import annotations

from rich.table import Table

ACCENT = "blue"
MUTED = "bright_black"
TEXT = "white"
WARN = "yellow"
DANGER = "red"


def kali_prompt_header(host: str, path: str) -> str:
    return (
        f"[{ACCENT}]┌──[/]"
        f"([bold {TEXT}]repotrust[/bold {TEXT}][{MUTED}]㉿[/]{host})"
        f"-[[{MUTED}]{path}[/{MUTED}]]"
    )


def kali_prompt(command: str) -> str:
    return f"[{ACCENT}]└─$[/] {command}"


def kali_section(title: str) -> str:
    return f"[{MUTED}]│[/] [bold {TEXT}]{title}[/bold {TEXT}]"


def kali_kv(label: str, value: object) -> str:
    return f"[{MUTED}]│ {label:<12}[/] {value}"


def kali_inline_kv(label: str, value: object) -> str:
    return f"[{MUTED}]{label}[/] {value}"


def muted(value: object) -> str:
    return f"[{MUTED}]{value}[/{MUTED}]"


def badge(value: str, *, style: str | None = None, bold: bool = True) -> str:
    chosen_style = style or state_style(value)
    prefix = "bold " if bold else ""
    return f"[{prefix}{chosen_style}]{value}[/{prefix}{chosen_style}]"


def state_style(value: str) -> str:
    normalized = value.lower()
    if normalized in {"medium", "partial", "unknown", "moderate risk"}:
        return WARN
    if normalized in {
        "low",
        "failed",
        "missing",
        "high risk",
        "elevated risk",
        "do_not_install_before_review",
    }:
        return DANGER
    if "high risk" in normalized or "elevated" in normalized:
        return DANGER
    if "moderate" in normalized:
        return WARN
    return ACCENT


def kali_table(*, show_header: bool = True) -> Table:
    return Table(
        box=None,
        show_edge=False,
        show_lines=False,
        show_header=show_header,
        header_style=MUTED,
        pad_edge=False,
    )

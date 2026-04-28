from __future__ import annotations

from rich.table import Table

ACCENT = "green"
MUTED = "dim"
WARN = "yellow"
DANGER = "red"


def header(title: str, context: str | None = None) -> str:
    suffix = f" [dim]// {context}[/dim]" if context else ""
    return f"[bold {ACCENT}]{title}[/bold {ACCENT}]{suffix}"


def section(title: str) -> str:
    return f"\n[dim]--[/dim] [bold {ACCENT}]{title}[/bold {ACCENT}]"


def kv(label: str, value: str) -> str:
    return f"[dim]{label:<12}[/dim] {value}"


def inline_kv(label: str, value: str) -> str:
    return f"[dim]{label}[/dim] {value}"


def status_style(value: str) -> str:
    normalized = value.lower()
    if normalized in {"high", "full", "found", "low risk"}:
        return ACCENT
    if normalized in {"medium", "partial", "unknown", "moderate risk"}:
        return WARN
    if normalized in {"low", "failed", "missing", "high risk", "elevated risk"}:
        return DANGER
    if "high" in normalized or "elevated" in normalized:
        return DANGER
    if "moderate" in normalized:
        return WARN
    return ACCENT


def badge(value: str, *, style: str | None = None, bold: bool = True) -> str:
    chosen_style = style or status_style(value)
    prefix = "bold " if bold else ""
    return f"[{prefix}{chosen_style}]{value}[/{prefix}{chosen_style}]"


def muted(value: object) -> str:
    return f"[{MUTED}]{value}[/{MUTED}]"


def data_table(*, show_header: bool = True) -> Table:
    return Table(
        box=None,
        show_edge=False,
        show_lines=False,
        show_header=show_header,
        header_style=MUTED,
        pad_edge=False,
    )

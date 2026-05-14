from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from rich.cells import cell_len
from rich.console import Console

from .console_i18n import ConsoleLocale, ConsoleText, console_text
from .terminal_theme import muted


@dataclass(frozen=True)
class ConsoleWorkflow:
    target: str = ""
    report_format: str = "html"
    workflow_kind: str = "scan"
    terminal_only: bool = False
    parse_only: bool = False
    remote: bool = False
    verbose: bool = False
    locale: ConsoleLocale = "en"


RunWorkflow = Callable[[ConsoleWorkflow], None]
BACK: Final = "__repotrust_back__"


def run_console_mode(
    *,
    console: Console,
    help_text: Callable[[], str],
    version: str,
    run_workflow: RunWorkflow,
    locale: ConsoleLocale = "en",
) -> None:
    """Run the interactive product shell for humans."""
    _run_console_mode_body(
        console=console,
        help_text=help_text,
        version=version,
        run_workflow=run_workflow,
        locale=locale,
    )


def _run_console_mode_body(
    *,
    console: Console,
    help_text: Callable[[], str],
    version: str,
    run_workflow: RunWorkflow,
    locale: ConsoleLocale,
) -> None:
    text = console_text(locale)
    while True:
        _print_console_home(console=console, version=version, text=text)
        choice = _ask_menu_choice(console=console, text=text)
        if choice == "q":
            console.print(f"[dim]{text['session_closed']}[/dim]")
            return
        if choice == "?":
            console.print(help_text())
            return

        workflow = _prompt_workflow(
            choice,
            console=console,
            text=text,
            locale=locale,
        )
        if workflow is None:
            console.print(muted(text["back_message"]))
            continue
        console.print()
        console.print(f"[bright_black]{text['processing_message']}[/]")
        run_workflow(workflow)
        return


def _print_console_home(
    *,
    console: Console,
    version: str,
    text: ConsoleText,
) -> None:
    console.print(f"[bold white]{text['console_title']} v{version}[/]")
    console.print(muted(text["tagline"]))
    console.print(muted(text["first_run_hint"]))
    console.print(_separator())
    console.print(f"[bold white]{text['workflows_title']}[/]")
    for line in _workflow_lines(text):
        console.print(line)
    console.print(_separator())
    console.print(muted(text["controls"]))


def _workflow_lines(text: ConsoleText) -> list[str]:
    lines: list[str] = []
    action_width = max(cell_len(str(action)) for _, action, _, _ in text["workflows"])
    for key, action, use_when, output in text["workflows"]:
        suffix = f" [bright_black]=>[/] {output}" if output else ""
        action_label = _pad_cells(str(action), action_width)
        lines.append(
            f"[cyan][{key}][/cyan]  "
            f"[white]{action_label}[/]{suffix}  "
            f"{muted(use_when)}"
        )
    return lines


def _separator(width: int = 36) -> str:
    return f"[bright_black]{'─' * width}[/]"


def _prompt_workflow(
    choice: str,
    *,
    console: Console,
    text: ConsoleText,
    locale: ConsoleLocale,
) -> ConsoleWorkflow | None:
    if choice == "l":
        _print_selected(console=console, label=str(text["selected_local"]))
        target = _ask_value(
            console=console,
            prompt=str(text["local_path_prompt"]),
            default=".",
            default_hint=str(text["default_hint"]),
            controls=str(text["input_controls"]),
        )
        if target == BACK:
            return None
        return ConsoleWorkflow(
            target=target,
            report_format="html",
            locale=locale,
        )
    if choice == "g":
        _print_selected(console=console, label=str(text["selected_github"]))
        target = _ask_value(
            console=console,
            prompt=str(text["github_url_prompt"]),
            example=str(text["github_url_example"]),
            controls=str(text["input_controls"]),
        )
        if target == BACK:
            return None
        return ConsoleWorkflow(
            target=target,
            report_format="html",
            locale=locale,
        )
    if choice == "j":
        _print_selected(console=console, label=str(text["selected_json"]))
        target = _ask_value(
            console=console,
            prompt=str(text["any_target_prompt"]),
            default=".",
            default_hint=str(text["default_hint"]),
            controls=str(text["input_controls"]),
        )
        if target == BACK:
            return None
        return ConsoleWorkflow(
            target=target,
            report_format="json",
            locale=locale,
        )
    if choice == "s":
        _print_selected(console=console, label=str(text["selected_safe_install"]))
        target = _ask_value(
            console=console,
            prompt=str(text["any_target_prompt"]),
            default=".",
            default_hint=str(text["default_hint"]),
            controls=str(text["input_controls"]),
        )
        if target == BACK:
            return None
        return ConsoleWorkflow(
            target=target,
            workflow_kind="safe_install",
            locale=locale,
        )
    if choice == "n":
        _print_selected(console=console, label=str(text["selected_next_steps"]))
        target = _ask_value(
            console=console,
            prompt=str(text["any_target_prompt"]),
            default=".",
            default_hint=str(text["default_hint"]),
            controls=str(text["input_controls"]),
        )
        if target == BACK:
            return None
        return ConsoleWorkflow(
            target=target,
            workflow_kind="next_steps",
            locale=locale,
        )
    _print_selected(console=console, label=str(text["selected_check"]))
    target = _ask_value(
        console=console,
        prompt=str(text["any_target_prompt"]),
        default=".",
        default_hint=str(text["default_hint"]),
        controls=str(text["input_controls"]),
    )
    if target == BACK:
        return None
    return ConsoleWorkflow(
        target=target,
        report_format="markdown",
        terminal_only=True,
        verbose=True,
        locale=locale,
    )


def _ask_menu_choice(*, console: Console, text: ConsoleText) -> str:
    choices = {"g", "l", "c", "j", "s", "n", "?", "q"}
    while True:
        value = _input_command(console, prompt=f"[cyan]→[/] {text['select_prompt']} ").strip() or "1"
        normalized = _normalize_menu_choice(value)
        if normalized in choices:
            return normalized
        console.print(f"[red]│ invalid selection:[/] {value}")


def _ask_value(
    *,
    console: Console,
    prompt: str,
    default: str | None = None,
    default_hint: str = "default",
    example: str | None = None,
    controls: str | None = None,
) -> str:
    suffix = f" [bright_black]({default_hint} {default})[/]" if default is not None else ""
    console.print(f"[bold white]{prompt}[/]{suffix}")
    if example:
        console.print(muted(example))
    if controls:
        console.print(muted(controls))
    value = _input_command(console, prompt="[cyan]>[/] ").strip()
    if value.lower() == "b":
        return BACK
    if not value and default is not None:
        return default
    return value


def _print_selected(*, console: Console, label: str) -> None:
    console.print()
    console.print(f"[green]{label}[/]")


def _normalize_menu_choice(value: str) -> str:
    normalized = value.lower()
    if normalized.isdigit():
        return {
            "1": "l",
            "2": "g",
            "3": "j",
            "4": "c",
            "6": "?",
            "8": "s",
        }.get(str(int(normalized)), normalized)
    return normalized


def _pad_cells(value: str, width: int) -> str:
    return value + (" " * max(width - cell_len(value), 0))


def _input_command(console: Console, prompt: str = "[cyan]>[/] ") -> str:
    value = console.input(prompt)
    if not console.is_terminal:
        console.print()
    return value

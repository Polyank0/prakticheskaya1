"""Служебные команды эмулятора."""

from typing import TYPE_CHECKING

from src.commands.registry import command
from src.errors import ShellError

if TYPE_CHECKING:
    from src.session import Session


@command("exit")
def run_exit(session: "Session", args: list[str]) -> str:
    """Завершает сеанс; аргументы не принимаются."""
    if args:
        raise ShellError("exit: too many arguments")
    session.running = False
    return ""

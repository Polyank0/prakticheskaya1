"""Команды навигации ls и cd (пока заглушки)."""

from typing import TYPE_CHECKING

from src.commands.registry import command

if TYPE_CHECKING:
    from src.session import Session


def describe_call(name: str, args: list[str]) -> str:
    """Формирует ответ заглушки: имя команды и её аргументы."""
    if not args:
        return f"{name}: stub, no arguments"
    return f"{name}: stub, arguments: {' | '.join(args)}"


@command("ls")
def run_ls(_session: "Session", args: list[str]) -> str:
    """Заглушка ls: выводит своё имя и аргументы."""
    return describe_call("ls", args)


@command("cd")
def run_cd(_session: "Session", args: list[str]) -> str:
    """Заглушка cd: выводит своё имя и аргументы."""
    return describe_call("cd", args)

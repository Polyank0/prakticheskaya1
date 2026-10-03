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


@command("conf-dump")
def run_conf_dump(session: "Session", args: list[str]) -> str:
    """Выводит параметры эмулятора в формате ключ=значение."""
    if args:
        raise ShellError("conf-dump: too many arguments")
    return session.settings.dump()


@command("vfs-info")
def run_vfs_info(session: "Session", args: list[str]) -> str:
    """Выводит источник VFS, число элементов и все пути."""
    if args:
        raise ShellError("vfs-info: too many arguments")
    paths = session.fs.paths()
    dirs = [path for path in paths if session.fs.is_dir(path)]
    lines = [
        f"source: {session.settings.vfs_path or '(memory only)'}",
        f"directories: {len(dirs)}, files: {len(paths) - len(dirs)}",
    ]
    for path in paths:
        if session.fs.is_dir(path):
            lines.append(f"d {'-':>7} {path}")
        else:
            lines.append(f"f {session.fs.size(path):>7} {path}")
    return "\n".join(lines)

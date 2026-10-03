"""Команды навигации ls и cd."""

from typing import TYPE_CHECKING

from src.commands.registry import command
from src.errors import ShellError
from src.memory_fs import ROOT, resolve

if TYPE_CHECKING:
    from src.session import Session

LONG_FLAG = "-l"


def format_entry(session: "Session", path: str, name: str, long: bool) -> str:
    """Возвращает строку списка для одного элемента."""
    is_dir = session.fs.is_dir(path)
    if not long:
        return name + ("/" if is_dir else "")
    size = "-" if is_dir else str(session.fs.size(path))
    return f"{'d' if is_dir else 'f'} {size:>7} {name}"


def list_target(session: "Session", target: str, long: bool) -> str:
    """Возвращает список содержимого каталога или строку для файла."""
    path = resolve(session.cwd, target)
    if not session.fs.exists(path):
        raise ShellError(f"ls: {target}: No such file or directory")
    if session.fs.is_file(path):
        return format_entry(session, path, target, long)
    return "\n".join(
        format_entry(session, resolve(path, name), name, long)
        for name in session.fs.children(path)
    )


@command("ls")
def run_ls(session: "Session", args: list[str]) -> str:
    """Выводит содержимое каталогов; -l добавляет тип и размер."""
    long = LONG_FLAG in args
    targets = [arg for arg in args if arg != LONG_FLAG]
    for target in targets:
        if target.startswith("-"):
            raise ShellError(f"ls: invalid option '{target}'")
    if not targets:
        return list_target(session, ".", long)
    if len(targets) == 1:
        return list_target(session, targets[0], long)
    blocks = [
        f"{target}:\n{list_target(session, target, long)}"
        for target in targets
    ]
    return "\n\n".join(blocks)


@command("cd")
def run_cd(session: "Session", args: list[str]) -> str:
    """Меняет текущий каталог; без аргумента переходит в корень."""
    if len(args) > 1:
        raise ShellError("cd: too many arguments")
    target = args[0] if args else ROOT
    path = resolve(session.cwd, target)
    if not session.fs.exists(path):
        raise ShellError(f"cd: {target}: No such file or directory")
    if session.fs.is_file(path):
        raise ShellError(f"cd: {target}: Not a directory")
    session.cwd = path
    return ""

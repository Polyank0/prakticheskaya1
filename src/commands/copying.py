"""Команда cp: копирование внутри VFS без записи на диск."""

import posixpath
from typing import TYPE_CHECKING

from src.commands.registry import command
from src.errors import ShellError
from src.memory_fs import ROOT, resolve

if TYPE_CHECKING:
    from src.session import Session

RECURSIVE_FLAGS = ("-r", "-R")


def is_inside(inner: str, outer: str) -> bool:
    """Сообщает, лежит ли путь inner внутри outer или совпадает с ним."""
    if outer == ROOT or inner == outer:
        return True
    return inner.startswith(outer + "/")


def pick_target(session: "Session", source: str, destination: str) -> str:
    """Определяет путь, по которому появится копия."""
    path = resolve(session.cwd, destination)
    if session.fs.is_dir(path):
        return resolve(path, posixpath.basename(source))
    return path


def check_target(session: "Session", source: str, target: str) -> None:
    """Проверяет, что копию можно создать по выбранному пути."""
    fs = session.fs
    if target == source:
        raise ShellError(f"cp: '{source}' and '{target}' are the same file")
    if fs.is_dir(source) and is_inside(target, source):
        raise ShellError(f"cp: cannot copy directory '{source}' into itself")
    if not fs.is_dir(posixpath.dirname(target)):
        raise ShellError(f"cp: cannot create '{target}': No such directory")
    if fs.is_dir(source) and fs.is_file(target):
        raise ShellError(f"cp: cannot replace file '{target}' with directory")


def copy_one(
    session: "Session", name: str, destination: str, deep: bool
) -> None:
    """Копирует один источник в место назначения."""
    source = resolve(session.cwd, name)
    if not session.fs.exists(source):
        raise ShellError(f"cp: cannot stat '{name}': No such file or directory")
    if session.fs.is_dir(source) and not deep:
        raise ShellError(f"cp: -r not specified; omitting directory '{name}'")
    target = pick_target(session, source, destination)
    check_target(session, source, target)
    session.fs.copy(source, target)


def split_operands(args: list[str]) -> tuple[bool, list[str]]:
    """Отделяет ключ -r от путей и отклоняет неизвестные ключи."""
    deep = False
    operands = []
    for arg in args:
        if arg in RECURSIVE_FLAGS:
            deep = True
        elif arg.startswith("-"):
            raise ShellError(f"cp: invalid option '{arg}'")
        else:
            operands.append(arg)
    return deep, operands


def check_destination(
    session: "Session", sources: list[str], destination: str
) -> None:
    """Проверяет, что несколько источников копируются в каталог."""
    to_dir = session.fs.is_dir(resolve(session.cwd, destination))
    if len(sources) > 1 and not to_dir:
        raise ShellError(f"cp: target '{destination}' is not a directory")


@command("cp")
def run_cp(session: "Session", args: list[str]) -> str:
    """Копирует файлы; с ключом -r копирует каталоги с содержимым."""
    deep, operands = split_operands(args)
    if not operands:
        raise ShellError("cp: missing file operand")
    sources, destination = operands[:-1], operands[-1]
    if not sources:
        raise ShellError(
            f"cp: missing destination file operand after '{destination}'"
        )
    check_destination(session, sources, destination)
    for name in sources:
        copy_one(session, name, destination, deep)
    return ""

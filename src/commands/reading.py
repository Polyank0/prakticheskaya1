"""Команды чтения: cat, tail и history."""

from typing import TYPE_CHECKING

from src.commands.registry import command
from src.errors import ShellError
from src.memory_fs import resolve

if TYPE_CHECKING:
    from src.session import Session

DEFAULT_TAIL_LINES = 10
COUNT_FLAG = "-n"
CLEAR_FLAG = "-c"


def read_text(session: "Session", name: str, target: str) -> str:
    """Читает файл VFS как текст для команды с данным именем."""
    path = resolve(session.cwd, target)
    if not session.fs.exists(path):
        raise ShellError(f"{name}: {target}: No such file or directory")
    if session.fs.is_dir(path):
        raise ShellError(f"{name}: {target}: Is a directory")
    return session.fs.read(path).decode("utf-8", errors="replace")


def parse_count(name: str, text: str) -> int:
    """Превращает аргумент в неотрицательное целое число."""
    if not text.isdigit():
        raise ShellError(f"{name}: {text}: numeric argument required")
    return int(text)


def take_count(args: list[str]) -> tuple[int, list[str]]:
    """Отделяет параметр -n ЧИСЛО от списка файлов команды tail."""
    if not args or args[0] != COUNT_FLAG:
        return DEFAULT_TAIL_LINES, args
    if len(args) == 1:
        raise ShellError("tail: option requires an argument -- 'n'")
    return parse_count("tail", args[1]), args[2:]


@command("cat")
def run_cat(session: "Session", args: list[str]) -> str:
    """Выводит содержимое файлов подряд."""
    if not args:
        raise ShellError("cat: missing file operand")
    texts = [read_text(session, "cat", target) for target in args]
    return "".join(texts).rstrip("\n")


@command("tail")
def run_tail(session: "Session", args: list[str]) -> str:
    """Выводит последние строки файлов; число строк задаёт -n."""
    count, targets = take_count(args)
    if not targets:
        raise ShellError("tail: missing file operand")
    blocks = []
    for target in targets:
        lines = read_text(session, "tail", target).splitlines()
        body = "\n".join(lines[-count:] if count else [])
        if len(targets) > 1:
            body = f"==> {target} <==\n{body}"
        blocks.append(body)
    return "\n".join(blocks)


@command("history")
def run_history(session: "Session", args: list[str]) -> str:
    """Выводит нумерованный список команд; -c очищает историю."""
    if len(args) > 1:
        raise ShellError("history: too many arguments")
    if args == [CLEAR_FLAG]:
        session.history.clear()
        return ""
    numbered = list(enumerate(session.history, start=1))
    if args:
        count = parse_count("history", args[0])
        numbered = numbered[-count:] if count else []
    return "\n".join(f"{number:>5}  {text}" for number, text in numbered)

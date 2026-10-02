"""Сеанс эмулятора: состояние и выполнение введённых строк."""

from typing import NamedTuple

from src.commands import find_command
from src.errors import ShellError
from src.lexer import split_line

DEFAULT_VFS_NAME = "novfs"


class Reply(NamedTuple):
    """Ответ эмулятора на одну строку ввода."""

    text: str
    failed: bool


class Session:
    """Хранит состояние оболочки и выполняет команды."""

    def __init__(self, vfs_name: str = DEFAULT_VFS_NAME) -> None:
        """Создаёт сеанс с именем VFS и корневым текущим каталогом."""
        self.vfs_name = vfs_name
        self.cwd = "/"
        self.running = True

    def title(self) -> str:
        """Возвращает заголовок окна с именем VFS."""
        return f"{self.vfs_name} - эмулятор оболочки"

    def prompt(self) -> str:
        """Возвращает приглашение к вводу."""
        return f"{self.vfs_name}:{self.cwd}$ "

    def run_line(self, line: str) -> Reply:
        """Выполняет строку и возвращает текст ответа с признаком ошибки."""
        try:
            words = split_line(line)
            if not words:
                return Reply("", False)
            handler = find_command(words[0])
            return Reply(handler(self, words[1:]), False)
        except ShellError as error:
            return Reply(str(error), True)

"""Сеанс эмулятора: состояние и выполнение введённых строк."""

from typing import NamedTuple, Optional

from src.commands import find_command
from src.csv_source import load_csv
from src.errors import ShellError
from src.lexer import split_line
from src.memory_fs import ROOT, MemoryFs, VfsError
from src.settings import Settings


class Reply(NamedTuple):
    """Ответ эмулятора на одну строку ввода."""

    text: str
    failed: bool


class Session:
    """Хранит состояние оболочки и выполняет команды."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Создаёт сеанс по параметрам запуска."""
        self.settings = settings or Settings()
        self.vfs_name = self.settings.vfs_name()
        self.cwd = ROOT
        self.running = True
        self.history: list[str] = []
        self.fs = MemoryFs()
        self.problems: list[str] = []
        self._load_vfs()

    def _load_vfs(self) -> None:
        """Загружает VFS в память; ошибку загрузки запоминает."""
        if not self.settings.vfs_path:
            return
        try:
            self.fs = load_csv(self.settings.vfs_path)
        except VfsError as error:
            self.problems.append(f"VFS not loaded: {error}")

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
            self.history.append(line.strip())
            handler = find_command(words[0])
            return Reply(handler(self, words[1:]), False)
        except ShellError as error:
            return Reply(str(error), True)

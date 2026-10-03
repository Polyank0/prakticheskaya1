"""Виртуальная файловая система, которая хранится только в памяти."""

import posixpath
from typing import Optional

from src.errors import ShellError

ROOT = "/"


class VfsError(ShellError):
    """Ошибка загрузки или изменения VFS."""


def resolve(cwd: str, target: str) -> str:
    """Превращает путь в абсолютный без точек и лишних разделителей."""
    joined = posixpath.normpath(posixpath.join(cwd, target))
    return ROOT + joined.lstrip("/")


class MemoryFs:
    """Плоский словарь: путь -> байты файла или None для каталога."""

    def __init__(self) -> None:
        """Создаёт файловую систему с одним корневым каталогом."""
        self._entries: dict[str, Optional[bytes]] = {ROOT: None}

    def exists(self, path: str) -> bool:
        """Сообщает, есть ли элемент с таким путём."""
        return path in self._entries

    def is_dir(self, path: str) -> bool:
        """Сообщает, является ли путь каталогом."""
        return self.exists(path) and self._entries[path] is None

    def is_file(self, path: str) -> bool:
        """Сообщает, является ли путь файлом."""
        return self.exists(path) and self._entries[path] is not None

    def paths(self) -> list[str]:
        """Возвращает все пути в алфавитном порядке."""
        return sorted(self._entries)

    def add_dir(self, path: str) -> None:
        """Создаёт каталог и недостающие родительские каталоги."""
        if self.is_file(path):
            raise VfsError(f"not a directory: {path}")
        if path != ROOT:
            self.add_dir(posixpath.dirname(path))
        self._entries[path] = None

    def add_file(self, path: str, data: bytes) -> None:
        """Создаёт или заменяет файл с данным содержимым."""
        if self.is_dir(path):
            raise VfsError(f"is a directory: {path}")
        self.add_dir(posixpath.dirname(path))
        self._entries[path] = data

    def read(self, path: str) -> bytes:
        """Возвращает содержимое файла."""
        data = self._entries.get(path)
        if data is None:
            raise VfsError(f"not a file: {path}")
        return data

    def size(self, path: str) -> int:
        """Возвращает размер файла в байтах; для каталога ноль."""
        return len(self._entries.get(path) or b"")

    def children(self, path: str) -> list[str]:
        """Возвращает имена элементов, лежащих прямо в каталоге."""
        prefix = path.rstrip("/") + "/"
        names = [
            entry[len(prefix):]
            for entry in self._entries
            if entry.startswith(prefix) and entry != path
        ]
        return sorted(name for name in names if "/" not in name)

    def copy(self, source: str, target: str) -> None:
        """Копирует файл или каталог со всем содержимым в памяти."""
        prefix = source.rstrip("/") + "/"
        for path in self.paths():
            if path != source and not path.startswith(prefix):
                continue
            new_path = target + path[len(source):]
            data = self._entries[path]
            if data is None:
                self.add_dir(new_path)
            else:
                self.add_file(new_path, data)

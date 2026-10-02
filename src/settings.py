"""Параметры эмулятора, заданные в командной строке."""

import argparse
import os
from dataclasses import dataclass
from typing import Optional, Sequence

DEFAULT_VFS_NAME = "novfs"


@dataclass(frozen=True)
class Settings:
    """Набор параметров запуска эмулятора."""

    vfs_path: str = ""
    script_path: str = ""

    def vfs_name(self) -> str:
        """Возвращает имя VFS: имя файла без каталога и расширения."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        file_name = os.path.basename(self.vfs_path.replace("\\", "/"))
        return os.path.splitext(file_name)[0] or DEFAULT_VFS_NAME

    def as_pairs(self) -> list[tuple[str, str]]:
        """Возвращает параметры в виде пар ключ-значение."""
        return [
            ("vfs_path", self.vfs_path),
            ("script_path", self.script_path),
            ("vfs_name", self.vfs_name()),
        ]

    def dump(self) -> str:
        """Возвращает параметры строками вида ключ=значение."""
        return "\n".join(f"{key}={value}" for key, value in self.as_pairs())


def read_settings(argv: Optional[Sequence[str]] = None) -> Settings:
    """Разбирает аргументы командной строки и возвращает параметры."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор оболочки UNIX-подобной ОС",
    )
    parser.add_argument("--vfs", default="", help="путь к файлу VFS")
    parser.add_argument(
        "--script", default="", help="путь к стартовому скрипту"
    )
    options = parser.parse_args(argv)
    return Settings(vfs_path=options.vfs, script_path=options.script)

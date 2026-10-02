"""Разбор командной строки: кавычки, комментарии, переменные окружения."""

import os
import shlex

from src.errors import ParseError


def expand_variables(word: str) -> str:
    """Подставляет в слово значения переменных окружения реальной ОС."""
    return os.path.expandvars(word)


def split_line(line: str) -> list[str]:
    """Делит строку на слова и раскрывает в них переменные окружения."""
    try:
        words = shlex.split(line, comments=True)
    except ValueError as error:
        raise ParseError(f"parse error: {error}") from error
    return [expand_variables(word) for word in words]

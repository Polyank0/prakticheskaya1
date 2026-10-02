"""Чтение стартового скрипта эмулятора."""

from src.errors import ShellError


def read_script(path: str) -> list[str]:
    """Возвращает непустые строки скрипта, включая комментарии."""
    try:
        with open(path, "r", encoding="utf-8") as script_file:
            lines = script_file.read().splitlines()
    except FileNotFoundError as error:
        raise ShellError(f"script not found: {path}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise ShellError(f"cannot read script {path}: {error}") from error
    return [line for line in lines if line.strip()]

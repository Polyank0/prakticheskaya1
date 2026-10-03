"""Команды эмулятора; импорт модулей заполняет реестр."""

from src.commands import navigation, reading, service
from src.commands.registry import command_names, find_command

__all__ = [
    "command_names",
    "find_command",
    "navigation",
    "reading",
    "service",
]

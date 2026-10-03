"""Команды эмулятора; импорт модулей заполняет реестр."""

from src.commands import copying, navigation, reading, service
from src.commands.registry import command_names, find_command

__all__ = [
    "command_names",
    "copying",
    "find_command",
    "navigation",
    "reading",
    "service",
]

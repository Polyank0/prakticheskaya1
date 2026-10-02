"""Реестр команд эмулятора."""

from typing import TYPE_CHECKING, Callable

from src.errors import ShellError

if TYPE_CHECKING:
    from src.session import Session

Handler = Callable[["Session", list], str]

_HANDLERS: dict[str, Handler] = {}


def command(name: str) -> Callable[[Handler], Handler]:
    """Регистрирует функцию как обработчик команды с данным именем."""

    def register(handler: Handler) -> Handler:
        """Запоминает обработчик и возвращает его без изменений."""
        _HANDLERS[name] = handler
        return handler

    return register


def find_command(name: str) -> Handler:
    """Возвращает обработчик команды или сообщает, что её нет."""
    handler = _HANDLERS.get(name)
    if handler is None:
        raise ShellError(f"{name}: command not found")
    return handler


def command_names() -> list[str]:
    """Возвращает имена всех зарегистрированных команд."""
    return sorted(_HANDLERS)

"""Точка входа эмулятора оболочки."""

from src.session import Session
from src.terminal_window import TerminalWindow


def main() -> None:
    """Создаёт сеанс и открывает окно терминала."""
    TerminalWindow(Session()).run()


if __name__ == "__main__":
    main()

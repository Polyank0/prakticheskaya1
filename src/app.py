"""Точка входа эмулятора оболочки."""

from src.errors import ShellError
from src.script_reader import read_script
from src.session import Session
from src.settings import read_settings
from src.terminal_window import TerminalWindow


def debug_lines(session: Session) -> list[str]:
    """Возвращает отладочные строки с параметрами запуска."""
    pairs = session.settings.as_pairs()
    return [f"[debug] {key}={value}" for key, value in pairs]


def main() -> None:
    """Читает параметры, открывает окно и запускает стартовый скрипт."""
    session = Session(read_settings())
    window = TerminalWindow(session)
    window.show_notes(debug_lines(session))
    if session.problems:
        problems = [f"[error] {text}" for text in session.problems]
        window.show_notes(problems, "error")
    script_path = session.settings.script_path
    if script_path:
        try:
            window.play_script(read_script(script_path))
        except ShellError as error:
            window.show_notes([f"[error] {error}"], "error")
    window.run()


if __name__ == "__main__":
    main()

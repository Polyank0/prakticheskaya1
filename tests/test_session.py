"""Тесты сеанса: приглашение, выход, ошибки."""

import unittest

from src.session import Session
from src.settings import Settings


class SessionTest(unittest.TestCase):
    """Проверяет выполнение строк в сеансе."""

    def test_title_and_prompt_contain_vfs_name(self) -> None:
        """Имя VFS входит в заголовок окна и приглашение."""
        session = Session(Settings(vfs_path="images/disk_a.csv"))
        self.assertIn("disk_a", session.title())
        self.assertEqual(session.prompt(), "disk_a:/$ ")

    def test_empty_line(self) -> None:
        """Пустая строка ничего не делает."""
        reply = Session().run_line("   ")
        self.assertEqual((reply.text, reply.failed), ("", False))

    def test_unknown_command(self) -> None:
        """Неизвестная команда даёт ошибку."""
        reply = Session().run_line("mkdir x")
        self.assertTrue(reply.failed)
        self.assertEqual(reply.text, "mkdir: command not found")

    def test_parse_error_is_reported(self) -> None:
        """Ошибка разбора возвращается как ответ с признаком ошибки."""
        reply = Session().run_line("ls 'abc")
        self.assertTrue(reply.failed)
        self.assertIn("parse error", reply.text)

    def test_exit_stops_session(self) -> None:
        """Команда exit завершает сеанс."""
        session = Session()
        session.run_line("exit")
        self.assertFalse(session.running)

    def test_exit_rejects_arguments(self) -> None:
        """Команда exit с аргументами даёт ошибку и не завершает сеанс."""
        session = Session()
        reply = session.run_line("exit now")
        self.assertTrue(reply.failed)
        self.assertTrue(session.running)


if __name__ == "__main__":
    unittest.main()

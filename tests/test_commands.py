"""Тесты команд ls, cd, cat, tail и history."""

import unittest

from src.session import Session
from src.settings import Settings

LOG = "/home/student/projects/shell/log.txt"
DEFAULT_TAIL = 10


def deep_session() -> Session:
    """Создаёт сеанс с глубокой VFS."""
    return Session(Settings(vfs_path="vfs/deep.csv"))


def several_session() -> Session:
    """Создаёт сеанс с VFS из нескольких файлов."""
    return Session(Settings(vfs_path="vfs/several.csv"))


class LsTest(unittest.TestCase):
    """Проверяет команду ls."""

    def test_current_directory(self) -> None:
        """Без аргументов выводится текущий каталог, каталоги с чертой."""
        reply = several_session().run_line("ls")
        self.assertEqual(reply.text, "docs/\nempty/\nreadme.txt")

    def test_long_format(self) -> None:
        """Ключ -l добавляет тип и размер."""
        reply = several_session().run_line("ls -l")
        self.assertIn("d       - docs", reply.text)
        self.assertIn("f      19 readme.txt", reply.text)

    def test_file_and_several_targets(self) -> None:
        """Файл выводится одной строкой, несколько целей с заголовками."""
        session = several_session()
        self.assertEqual(session.run_line("ls readme.txt").text, "readme.txt")
        reply = session.run_line("ls docs empty")
        self.assertEqual(reply.text, "docs:\nnotes.txt\ntodo.txt\n\nempty:\n")

    def test_errors(self) -> None:
        """Несуществующий путь и неизвестный ключ дают ошибки."""
        session = several_session()
        self.assertIn("No such file", session.run_line("ls /none").text)
        self.assertIn("invalid option", session.run_line("ls -x").text)
        self.assertTrue(session.run_line("ls -x").failed)


class CdTest(unittest.TestCase):
    """Проверяет команду cd."""

    def test_moves_and_changes_prompt(self) -> None:
        """Переход меняет текущий каталог и приглашение."""
        session = deep_session()
        session.run_line("cd home/student")
        self.assertEqual(session.cwd, "/home/student")
        self.assertEqual(session.prompt(), "deep:/home/student$ ")
        session.run_line("cd ../../etc")
        self.assertEqual(session.cwd, "/etc")

    def test_without_argument_goes_to_root(self) -> None:
        """Без аргумента cd возвращает в корень."""
        session = deep_session()
        session.run_line("cd /var/log")
        session.run_line("cd")
        self.assertEqual(session.cwd, "/")

    def test_errors_keep_directory(self) -> None:
        """Ошибки cd не меняют текущий каталог."""
        session = deep_session()
        self.assertIn("No such file", session.run_line("cd /none").text)
        self.assertIn("Not a directory", session.run_line("cd /etc/motd").text)
        self.assertIn("too many", session.run_line("cd /etc /var").text)
        self.assertEqual(session.cwd, "/")


class CatTest(unittest.TestCase):
    """Проверяет команду cat."""

    def test_one_and_several_files(self) -> None:
        """Файлы выводятся подряд."""
        session = several_session()
        self.assertEqual(session.run_line("cat docs/todo.txt").text,
                         "buy milk\nsleep")
        reply = session.run_line("cat readme.txt docs/todo.txt")
        self.assertEqual(reply.text, "Several files VFS.\nbuy milk\nsleep")

    def test_errors(self) -> None:
        """Нет аргумента, каталог и отсутствующий файл дают ошибки."""
        session = several_session()
        self.assertIn("missing file operand", session.run_line("cat").text)
        self.assertIn("Is a directory", session.run_line("cat docs").text)
        self.assertIn("No such file", session.run_line("cat nope").text)


class TailTest(unittest.TestCase):
    """Проверяет команду tail."""

    def test_default_count(self) -> None:
        """По умолчанию выводятся последние десять строк."""
        lines = deep_session().run_line(f"tail {LOG}").text.splitlines()
        self.assertEqual(len(lines), DEFAULT_TAIL)
        self.assertEqual((lines[0], lines[-1]), ("e03", "e12"))

    def test_explicit_count(self) -> None:
        """Ключ -n задаёт число строк, ноль даёт пустой вывод."""
        session = deep_session()
        self.assertEqual(session.run_line(f"tail -n 2 {LOG}").text, "e11\ne12")
        self.assertEqual(session.run_line(f"tail -n 0 {LOG}").text, "")

    def test_several_files_have_headers(self) -> None:
        """Для нескольких файлов печатаются заголовки."""
        reply = several_session().run_line(
            "tail -n 1 docs/todo.txt docs/notes.txt"
        )
        expected = (
            "==> docs/todo.txt <==\nsleep\n"
            "==> docs/notes.txt <==\nthird line"
        )
        self.assertEqual(reply.text, expected)

    def test_errors(self) -> None:
        """Неверные аргументы tail дают ошибки."""
        session = several_session()
        self.assertIn("missing file operand", session.run_line("tail").text)
        self.assertIn("requires an argument", session.run_line("tail -n").text)
        self.assertIn("numeric", session.run_line("tail -n x readme.txt").text)
        self.assertIn("Is a directory", session.run_line("tail docs").text)


class HistoryTest(unittest.TestCase):
    """Проверяет команду history."""

    def test_numbered_list(self) -> None:
        """История хранит команды по порядку, включая ошибочные."""
        session = several_session()
        session.run_line("ls")
        session.run_line("unknown")
        session.run_line("# комментарий")
        reply = session.run_line("history")
        expected = "    1  ls\n    2  unknown\n    3  history"
        self.assertEqual(reply.text, expected)

    def test_last_items_and_clear(self) -> None:
        """Число ограничивает вывод, -c очищает историю."""
        session = several_session()
        session.run_line("ls")
        session.run_line("cd docs")
        reply = session.run_line("history 1")
        self.assertEqual(reply.text, "    3  history 1")
        session.run_line("history -c")
        self.assertEqual(session.history, [])

    def test_errors(self) -> None:
        """Неверные аргументы history дают ошибки."""
        session = several_session()
        self.assertIn("numeric", session.run_line("history abc").text)
        self.assertIn("too many", session.run_line("history 1 2").text)


if __name__ == "__main__":
    unittest.main()

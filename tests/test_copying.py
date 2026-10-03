"""Тесты команды cp."""

import unittest

from src.session import Session
from src.settings import Settings

SOURCE_CSV = "vfs/several.csv"


def new_session() -> Session:
    """Создаёт сеанс с VFS из нескольких файлов."""
    return Session(Settings(vfs_path=SOURCE_CSV))


class CopyFileTest(unittest.TestCase):
    """Проверяет копирование файлов."""

    def test_copy_with_new_name(self) -> None:
        """Копия получает то же содержимое, оригинал остаётся."""
        session = new_session()
        reply = session.run_line("cp readme.txt copy.txt")
        self.assertEqual((reply.text, reply.failed), ("", False))
        self.assertEqual(session.fs.read("/copy.txt"),
                         session.fs.read("/readme.txt"))

    def test_copy_into_directory(self) -> None:
        """При копировании в каталог имя файла сохраняется."""
        session = new_session()
        session.run_line("cp readme.txt docs")
        self.assertTrue(session.fs.is_file("/docs/readme.txt"))

    def test_several_sources(self) -> None:
        """Несколько файлов копируются в каталог."""
        session = new_session()
        session.run_line("cp docs/todo.txt docs/notes.txt empty")
        self.assertEqual(session.fs.children("/empty"),
                         ["notes.txt", "todo.txt"])

    def test_overwrite_existing_file(self) -> None:
        """Существующий файл заменяется содержимым источника."""
        session = new_session()
        session.run_line("cp docs/todo.txt readme.txt")
        self.assertEqual(session.fs.read("/readme.txt"), b"buy milk\nsleep\n")

    def test_relative_paths_use_current_directory(self) -> None:
        """Относительные пути считаются от текущего каталога."""
        session = new_session()
        session.run_line("cd docs")
        session.run_line("cp todo.txt ../empty/list.txt")
        self.assertTrue(session.fs.is_file("/empty/list.txt"))


class CopyDirectoryTest(unittest.TestCase):
    """Проверяет копирование каталогов."""

    def test_recursive_copy_to_new_name(self) -> None:
        """Ключ -r копирует каталог со всем содержимым."""
        session = new_session()
        session.run_line("cp -r docs backup")
        self.assertEqual(session.fs.children("/backup"),
                         ["notes.txt", "todo.txt"])
        self.assertEqual(session.fs.children("/docs"),
                         ["notes.txt", "todo.txt"])

    def test_recursive_copy_into_existing_directory(self) -> None:
        """Каталог копируется внутрь существующего каталога."""
        session = new_session()
        session.run_line("cp -r docs empty")
        self.assertTrue(session.fs.is_file("/empty/docs/todo.txt"))

    def test_directory_without_flag(self) -> None:
        """Без ключа -r каталог не копируется."""
        session = new_session()
        reply = session.run_line("cp docs backup")
        self.assertTrue(reply.failed)
        self.assertIn("-r not specified", reply.text)
        self.assertFalse(session.fs.exists("/backup"))

    def test_directory_into_itself(self) -> None:
        """Каталог нельзя скопировать внутрь самого себя."""
        session = new_session()
        self.assertIn("into itself",
                      session.run_line("cp -r docs docs/inner").text)
        self.assertIn("into itself", session.run_line("cp -r / /all").text)

    def test_directory_over_file(self) -> None:
        """Каталог нельзя записать поверх файла."""
        reply = new_session().run_line("cp -r docs readme.txt")
        self.assertIn("with directory", reply.text)


class CopyErrorsTest(unittest.TestCase):
    """Проверяет ошибки аргументов cp."""

    def test_missing_operands(self) -> None:
        """Без источника или без назначения выводится ошибка."""
        session = new_session()
        self.assertIn("missing file operand", session.run_line("cp").text)
        self.assertIn("missing destination",
                      session.run_line("cp readme.txt").text)

    def test_missing_source_and_parent(self) -> None:
        """Нет источника или каталога назначения: ошибка."""
        session = new_session()
        self.assertIn("cannot stat", session.run_line("cp nope a.txt").text)
        self.assertIn("cannot create",
                      session.run_line("cp readme.txt /no/a.txt").text)

    def test_same_file_and_bad_target(self) -> None:
        """Копия в себя и несколько источников в файл дают ошибки."""
        session = new_session()
        self.assertIn("same file",
                      session.run_line("cp readme.txt readme.txt").text)
        reply = session.run_line("cp readme.txt docs/todo.txt docs/notes.txt")
        self.assertIn("is not a directory", reply.text)
        self.assertIn("invalid option",
                      session.run_line("cp -x readme.txt a").text)

    def test_source_csv_is_untouched(self) -> None:
        """Копирование меняет только память, CSV-файл прежний."""
        with open(SOURCE_CSV, "rb") as csv_file:
            before = csv_file.read()
        session = new_session()
        session.run_line("cp -r docs backup")
        with open(SOURCE_CSV, "rb") as csv_file:
            self.assertEqual(csv_file.read(), before)


if __name__ == "__main__":
    unittest.main()

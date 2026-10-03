"""Тесты VFS: загрузка из CSV и работа в памяти."""

import os
import tempfile
import unittest

from src.csv_source import load_csv
from src.memory_fs import MemoryFs, VfsError, resolve
from src.session import Session
from src.settings import Settings

DEEP_FILE = "/home/student/projects/shell/main.py"


def load_text(text: str) -> MemoryFs:
    """Загружает VFS из CSV-текста через временный файл."""
    handle, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(handle, "w", encoding="utf-8") as csv_file:
        csv_file.write(text)
    try:
        return load_csv(path)
    finally:
        os.remove(path)


class ResolveTest(unittest.TestCase):
    """Проверяет приведение путей к абсолютному виду."""

    def test_relative_and_parent(self) -> None:
        """Относительные пути и две точки считаются от текущего каталога."""
        self.assertEqual(resolve("/a/b", "c"), "/a/b/c")
        self.assertEqual(resolve("/a/b", "../x/./y"), "/a/x/y")

    def test_root_is_the_top(self) -> None:
        """Выше корня подняться нельзя."""
        self.assertEqual(resolve("/", "../.."), "/")
        self.assertEqual(resolve("/a", "//b//c/"), "/b/c")


class CsvLoadTest(unittest.TestCase):
    """Проверяет загрузку готовых и ошибочных CSV-файлов."""

    def test_minimal(self) -> None:
        """Минимальная VFS содержит один файл в корне."""
        fs = load_csv("vfs/minimal.csv")
        self.assertEqual(fs.children("/"), ["hello.txt"])
        self.assertEqual(fs.read("/hello.txt"), b"Hello, VFS!\n")

    def test_several_files(self) -> None:
        """VFS с несколькими файлами содержит каталоги и файлы."""
        fs = load_csv("vfs/several.csv")
        self.assertEqual(fs.children("/"), ["docs", "empty", "readme.txt"])
        self.assertEqual(fs.children("/docs"), ["notes.txt", "todo.txt"])
        self.assertEqual(fs.children("/empty"), [])

    def test_three_levels(self) -> None:
        """Глубокая VFS создаёт недостающие родительские каталоги."""
        fs = load_csv("vfs/deep.csv")
        self.assertTrue(fs.is_file(DEEP_FILE))
        self.assertTrue(fs.is_dir("/home/student/projects"))
        self.assertTrue(fs.is_dir("/home"))

    def test_binary_data(self) -> None:
        """Двоичные данные восстанавливаются из base64 без искажений."""
        fs = load_csv("vfs/deep.csv")
        expected = bytes([0, 255, 16, 128, 7])
        self.assertEqual(fs.read("/home/student/photo.bin"), expected)

    def test_missing_file(self) -> None:
        """Отсутствующий файл VFS даёт ошибку загрузки."""
        with self.assertRaises(VfsError) as caught:
            load_csv("vfs/no_such_file.csv")
        self.assertIn("not found", str(caught.exception))

    def test_broken_base64(self) -> None:
        """Неверный base64 даёт ошибку с номером строки."""
        with self.assertRaises(VfsError) as caught:
            load_csv("vfs/broken.csv")
        self.assertIn("line 3", str(caught.exception))

    def test_wrong_header(self) -> None:
        """Неверный заголовок CSV даёт ошибку."""
        with self.assertRaises(VfsError):
            load_text("name,kind\n/a,dir\n")

    def test_unknown_type_and_relative_path(self) -> None:
        """Неизвестный тип и относительный путь дают ошибки."""
        with self.assertRaises(VfsError):
            load_text("path,type,data\n/a,link,\n")
        with self.assertRaises(VfsError):
            load_text("path,type,data\na.txt,file,\n")

    def test_file_used_as_directory(self) -> None:
        """Нельзя положить элемент внутрь файла."""
        with self.assertRaises(VfsError):
            load_text("path,type,data\n/a,file,\n/a/b,file,\n")

    def test_duplicate_path(self) -> None:
        """Повтор пути даёт ошибку."""
        with self.assertRaises(VfsError):
            load_text("path,type,data\n/a,dir,\n/a,dir,\n")


class SessionVfsTest(unittest.TestCase):
    """Проверяет подключение VFS к сеансу."""

    def test_source_file_is_not_modified(self) -> None:
        """Работа с VFS не меняет исходный CSV-файл."""
        with open("vfs/several.csv", "rb") as csv_file:
            before = csv_file.read()
        session = Session(Settings(vfs_path="vfs/several.csv"))
        session.fs.add_file("/new.txt", b"data")
        with open("vfs/several.csv", "rb") as csv_file:
            self.assertEqual(csv_file.read(), before)

    def test_load_problem_is_kept(self) -> None:
        """Ошибка загрузки запоминается, сеанс работает с пустой VFS."""
        session = Session(Settings(vfs_path="vfs/broken.csv"))
        self.assertIn("VFS not loaded", session.problems[0])
        self.assertEqual(session.fs.paths(), ["/"])

    def test_vfs_info(self) -> None:
        """Команда vfs-info показывает источник, счётчики и пути."""
        session = Session(Settings(vfs_path="vfs/minimal.csv"))
        reply = session.run_line("vfs-info")
        self.assertIn("source: vfs/minimal.csv", reply.text)
        self.assertIn("directories: 1, files: 1", reply.text)
        self.assertIn("/hello.txt", reply.text)

    def test_vfs_info_rejects_arguments(self) -> None:
        """Команда vfs-info с аргументами даёт ошибку."""
        self.assertTrue(Session().run_line("vfs-info /").failed)


if __name__ == "__main__":
    unittest.main()

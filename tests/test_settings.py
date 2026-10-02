"""Тесты параметров командной строки, conf-dump и чтения скрипта."""

import os
import tempfile
import unittest
import unittest.mock

from src.errors import ShellError
from src.script_reader import read_script
from src.session import Session
from src.settings import Settings, read_settings


def write_temp_script(text: str) -> str:
    """Создаёт временный файл скрипта и возвращает путь к нему."""
    handle, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(handle, "w", encoding="utf-8") as script_file:
        script_file.write(text)
    return path


class SettingsTest(unittest.TestCase):
    """Проверяет разбор параметров и их вывод."""

    def test_defaults(self) -> None:
        """Без аргументов пути пустые, имя VFS по умолчанию."""
        settings = read_settings([])
        self.assertEqual(settings.vfs_path, "")
        self.assertEqual(settings.script_path, "")
        self.assertEqual(settings.vfs_name(), "novfs")

    def test_both_options(self) -> None:
        """Оба параметра читаются из командной строки."""
        settings = read_settings(["--vfs", "a.csv", "--script", "b.txt"])
        self.assertEqual(settings.vfs_path, "a.csv")
        self.assertEqual(settings.script_path, "b.txt")

    def test_vfs_name_from_windows_path(self) -> None:
        """Имя VFS берётся из имени файла при любом разделителе пути."""
        settings = Settings(vfs_path="C:\\work\\disks\\main.csv")
        self.assertEqual(settings.vfs_name(), "main")
        self.assertEqual(Settings(vfs_path="vfs/deep.csv").vfs_name(), "deep")

    def test_unknown_option_is_rejected(self) -> None:
        """Неизвестный параметр завершает разбор с ошибкой."""
        with self.assertRaises(SystemExit):
            with open(os.devnull, "w", encoding="utf-8") as sink:
                with unittest.mock.patch("sys.stderr", sink):
                    read_settings(["--color", "red"])

    def test_conf_dump_output(self) -> None:
        """Команда conf-dump печатает все параметры как ключ=значение."""
        settings = Settings(vfs_path="vfs/a.csv", script_path="s.txt")
        reply = Session(settings).run_line("conf-dump")
        expected = "vfs_path=vfs/a.csv\nscript_path=s.txt\nvfs_name=a"
        self.assertEqual(reply.text, expected)
        self.assertFalse(reply.failed)

    def test_conf_dump_rejects_arguments(self) -> None:
        """Команда conf-dump с аргументами даёт ошибку."""
        reply = Session().run_line("conf-dump all")
        self.assertTrue(reply.failed)


class ScriptReaderTest(unittest.TestCase):
    """Проверяет чтение стартового скрипта."""

    def test_blank_lines_are_skipped(self) -> None:
        """Пустые строки пропускаются, комментарии остаются."""
        path = write_temp_script("# start\n\nls\n   \ncd /\n")
        try:
            self.assertEqual(read_script(path), ["# start", "ls", "cd /"])
        finally:
            os.remove(path)

    def test_comment_line_does_nothing(self) -> None:
        """Строка-комментарий выполняется без вывода и без ошибки."""
        reply = Session().run_line("# просто комментарий")
        self.assertEqual((reply.text, reply.failed), ("", False))

    def test_missing_script(self) -> None:
        """Отсутствующий файл скрипта даёт понятную ошибку."""
        with self.assertRaises(ShellError) as caught:
            read_script("no_such_script_file.txt")
        self.assertIn("script not found", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

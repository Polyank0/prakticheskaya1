"""Тесты разбора командной строки."""

import os
import unittest

from src.errors import ParseError
from src.lexer import split_line

os.environ["EMULATOR_TEST_DIR"] = "/srv/data"


class LexerTest(unittest.TestCase):
    """Проверяет кавычки, комментарии и переменные окружения."""

    def test_plain_words(self) -> None:
        """Слова делятся по пробелам."""
        self.assertEqual(split_line("ls  -l   docs"), ["ls", "-l", "docs"])

    def test_quotes_keep_spaces(self) -> None:
        """Текст в кавычках остаётся одним аргументом."""
        self.assertEqual(split_line('cd "my folder"'), ["cd", "my folder"])

    def test_variable_expansion(self) -> None:
        """Переменная вида $NAME заменяется значением."""
        words = split_line("cd $EMULATOR_TEST_DIR/logs")
        self.assertEqual(words, ["cd", "/srv/data/logs"])

    def test_braced_variable_expansion(self) -> None:
        """Переменная вида ${NAME} заменяется значением."""
        words = split_line("ls ${EMULATOR_TEST_DIR}_old")
        self.assertEqual(words, ["ls", "/srv/data_old"])

    def test_unknown_variable_stays(self) -> None:
        """Неизвестная переменная остаётся в тексте как есть."""
        words = split_line("ls $EMULATOR_NO_SUCH_VARIABLE")
        self.assertEqual(words, ["ls", "$EMULATOR_NO_SUCH_VARIABLE"])

    def test_comment_is_dropped(self) -> None:
        """Комментарий после решётки отбрасывается."""
        self.assertEqual(split_line("ls docs # список"), ["ls", "docs"])
        self.assertEqual(split_line("# только комментарий"), [])

    def test_unclosed_quote(self) -> None:
        """Незакрытая кавычка даёт ошибку разбора."""
        with self.assertRaises(ParseError):
            split_line('ls "docs')


if __name__ == "__main__":
    unittest.main()

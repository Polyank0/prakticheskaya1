"""Загрузка VFS из CSV-файла со столбцами path, type, data."""

import base64
import binascii
import csv

from src.memory_fs import ROOT, MemoryFs, VfsError, resolve

COLUMNS = ("path", "type", "data")
FIRST_DATA_LINE = 2


def decode_data(text: str, line: int) -> bytes:
    """Раскодирует содержимое файла из base64."""
    try:
        return base64.b64decode(text.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as error:
        raise VfsError(f"line {line}: invalid base64 data") from error


def add_row(target: MemoryFs, row: dict, line: int) -> None:
    """Добавляет в файловую систему элемент из одной строки CSV."""
    raw_path = (row.get("path") or "").strip()
    kind = (row.get("type") or "").strip()
    if not raw_path.startswith(ROOT):
        raise VfsError(f"line {line}: path must start with '/'")
    path = resolve(ROOT, raw_path)
    if target.exists(path) and path != ROOT:
        raise VfsError(f"line {line}: duplicate path {path}")
    try:
        if kind == "dir":
            target.add_dir(path)
        elif kind == "file":
            target.add_file(path, decode_data(row.get("data") or "", line))
        else:
            raise VfsError(f"line {line}: unknown type '{kind}'")
    except VfsError as error:
        prefix = f"line {line}: "
        text = str(error)
        raise VfsError(text if text.startswith(prefix) else prefix + text)


def read_rows(path: str) -> list[dict]:
    """Читает строки CSV-файла и проверяет заголовок."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            header = tuple(reader.fieldnames or ())
            rows = list(reader)
    except FileNotFoundError as error:
        raise VfsError(f"VFS file not found: {path}") from error
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise VfsError(f"cannot read VFS file {path}: {error}") from error
    if header != COLUMNS:
        raise VfsError(f"VFS header must be: {','.join(COLUMNS)}")
    return rows


def load_csv(path: str) -> MemoryFs:
    """Строит файловую систему в памяти по CSV-файлу."""
    target = MemoryFs()
    for line, row in enumerate(read_rows(path), start=FIRST_DATA_LINE):
        add_row(target, row, line)
    return target

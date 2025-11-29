import os
from pathlib import Path
from typing import Optional

def ensure_directory_exists(file_path: str) -> Path:
    """Создает директорию если она не существует"""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def get_file_extension(file_path: str) -> str:
    """Возвращает расширение файла"""
    return Path(file_path).suffix.lower()

def validate_pdf_file(file_path: str) -> bool:
    """Проверяет что файл существует и это PDF"""
    path = Path(file_path)
    return path.exists() and path.is_file() and get_file_extension(file_path) == '.pdf'
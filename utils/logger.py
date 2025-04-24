# utils/logger.py

"""
Модуль налаштування логування для додатку YouTube Uploader.
Забезпечує єдиний формат логів та можливість збереження їх у файл.
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


def setup_logger(
        log_dir: str = "logs",
        log_level: int = logging.INFO,
        max_log_size: int = 5 * 1024 * 1024,  # 5 MB
        backup_count: int = 3
) -> logging.Logger:
    """
    Налаштовує логер для додатку.

    Args:
        log_dir: Директорія для зберігання лог-файлів.
        log_level: Рівень логування.
        max_log_size: Максимальний розмір лог-файлу перед ротацією.
        backup_count: Кількість резервних копій лог-файлів.

    Returns:
        Налаштований об'єкт логера.
    """
    # Створення директорії для логів, якщо вона не існує
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Створення імені файлу логу з датою
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = log_path / f"app_{current_date}.log"

    # Основні налаштування логера
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Формат логування
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Обробник для виведення в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Обробник для запису у файл з ротацією
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # Відключення передачі логів до батьківських логерів
    logger.propagate = False

    logger.info("Logger initialized")
    return logger


class LoggingMixin:
    """
    Міксін для додавання можливостей логування до класів.

    Приклад використання:
    ```
    class MyClass(LoggingMixin):
        def __init__(self):
            super().__init__()
            self.logger.info("MyClass initialized")
    ```
    """

    def __init__(self):
        """Ініціалізує логер для класу."""
        self.logger = logging.getLogger(self.__class__.__name__)
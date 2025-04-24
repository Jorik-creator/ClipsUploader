# main.py

"""
Головний файл для запуску додатку YouTube Uploader.
Ініціалізує журнал логування та запускає основне вікно програми.
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


# Налаштування логування
def setup_logging():
    """Налаштовує систему логування додатку."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Налаштування обробників логів
    file_handler = logging.FileHandler(log_dir / "app.log", encoding='utf-8')
    console_handler = logging.StreamHandler()

    # Формат логів
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Налаштування кореневого логера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger


def main():
    """Головна функція для запуску додатку."""
    # Налаштування логування
    logger = setup_logging()
    logger.info("Application starting...")

    # Створення Qt-додатку
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Використовуємо стиль Fusion для кросплатформної сумісності

    # Імпорт головного вікна
    try:
        from gui.main_window import MainWindow
        window = MainWindow()
        window.show()
        logger.info("Main window initialized and shown")
    except Exception as e:
        logger.error(f"Error initializing main window: {e}")
        return 1

    # Запуск циклу обробки подій Qt
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
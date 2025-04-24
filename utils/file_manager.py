# utils/file_manager.py

"""
Модуль для роботи з відеофайлами та зображеннями.
Забезпечує функціональність для отримання інформації про файли, попередній перегляд та обробку.
"""

import os
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


# У виробничому коді можна використовувати додаткові бібліотеки для роботи з відео:
# - moviepy для обробки відео
# - pillow для обробки зображень
# - ffmpeg-python для розширеної обробки відео

class FileManager:
    """
    Клас для роботи з файлами у додатку YouTube Uploader.
    Забезпечує функціональність для роботи з відеофайлами та зображеннями.
    """

    # Дозволені формати файлів
    ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

    def __init__(self, temp_dir: str = None):
        """
        Ініціалізує менеджер файлів.

        Args:
            temp_dir: Директорія для тимчасових файлів (опціонально).
        """
        self.logger = logging.getLogger(__name__)
        self.temp_dir = temp_dir if temp_dir else tempfile.gettempdir()

        # Створення директорії для тимчасових файлів, якщо вона не існує
        os.makedirs(self.temp_dir, exist_ok=True)

        self.logger.info(f"File manager initialized with temp directory: {self.temp_dir}")

    def is_valid_video_file(self, file_path: str) -> bool:
        """
        Перевіряє, чи є файл дійсним відеофайлом.

        Args:
            file_path: Шлях до файлу.

        Returns:
            True, якщо файл є дійсним відеофайлом, інакше False.
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"File does not exist: {file_path}")
            return False

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.ALLOWED_VIDEO_EXTENSIONS:
            self.logger.warning(f"Invalid video file extension: {file_ext}")
            return False

        # Додаткові перевірки можуть бути додані тут
        # Наприклад, перевірка розміру файлу, його доступності тощо

        return True

    def is_valid_image_file(self, file_path: str) -> bool:
        """
        Перевіряє, чи є файл дійсним зображенням.

        Args:
            file_path: Шлях до файлу.

        Returns:
            True, якщо файл є дійсним зображенням, інакше False.
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"File does not exist: {file_path}")
            return False

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.ALLOWED_IMAGE_EXTENSIONS:
            self.logger.warning(f"Invalid image file extension: {file_ext}")
            return False

        # Додаткові перевірки можуть бути додані тут

        return True

    def get_video_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Отримує інформацію про відеофайл.

        Args:
            file_path: Шлях до відеофайлу.

        Returns:
            Словник з інформацією про відео або None у разі помилки.
        """
        if not self.is_valid_video_file(file_path):
            return None

        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()

            # В реальному проекті тут можна використовувати ffmpeg або moviepy
            # для отримання детальної інформації про відео (тривалість, розміри, кодеки)

            # Базова інформація про файл
            info = {
                'file_name': file_name,
                'file_path': file_path,
                'file_size': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'extension': file_ext,
                # Тут можуть бути додаткові поля
            }

            self.logger.info(f"Got video info for {file_name}")
            return info
        except Exception as e:
            self.logger.error(f"Error getting video info: {str(e)}")
            return None

    def create_temp_copy(self, file_path: str) -> Optional[str]:
        """
        Створює тимчасову копію файлу.

        Args:
            file_path: Шлях до вихідного файлу.

        Returns:
            Шлях до тимчасової копії або None у разі помилки.
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"File does not exist: {file_path}")
            return None

        try:
            file_name = os.path.basename(file_path)
            temp_file_path = os.path.join(self.temp_dir, f"temp_{file_name}")

            shutil.copy2(file_path, temp_file_path)
            self.logger.info(f"Created temporary copy: {temp_file_path}")

            return temp_file_path
        except Exception as e:
            self.logger.error(f"Error creating temporary copy: {str(e)}")
            return None

    def resize_image(self, image_path: str, max_width: int = 1280, max_height: int = 720) -> Optional[str]:
        """
        Змінює розмір зображення.

        Args:
            image_path: Шлях до вихідного зображення.
            max_width: Максимальна ширина.
            max_height: Максимальна висота.

        Returns:
            Шлях до обробленого зображення або None у разі помилки.
        """
        if not self.is_valid_image_file(image_path):
            return None

        # Примітка: для реальної реалізації потрібно використовувати бібліотеку обробки зображень,
        # наприклад, Pillow (PIL)

        # Цей код є заглушкою, в реальному додатку тут буде код зміни розміру зображення
        try:
            file_name = os.path.basename(image_path)
            output_path = os.path.join(self.temp_dir, f"resized_{file_name}")

            # Копіюємо файл для демонстрації
            shutil.copy2(image_path, output_path)
            self.logger.info(f"Resized image saved to: {output_path}")

            return output_path
        except Exception as e:
            self.logger.error(f"Error resizing image: {str(e)}")
            return None

    def trim_video(self, video_path: str, start_time: float = 0, end_time: Optional[float] = None) -> Optional[str]:
        """
        Обрізає відео за часовими мітками.

        Args:
            video_path: Шлях до вихідного відео.
            start_time: Час початку (в секундах).
            end_time: Час кінця (в секундах), None для кінця відео.

        Returns:
            Шлях до обробленого відео або None у разі помилки.
        """
        if not self.is_valid_video_file(video_path):
            return None

        # Примітка: для реальної реалізації потрібно використовувати бібліотеку обробки відео,
        # наприклад, moviepy або ffmpeg-python

        # Цей код є заглушкою, в реальному додатку тут буде код обрізки відео
        try:
            file_name = os.path.basename(video_path)
            output_path = os.path.join(self.temp_dir, f"trimmed_{file_name}")

            # Копіюємо файл для демонстрації
            shutil.copy2(video_path, output_path)
            self.logger.info(f"Trimmed video saved to: {output_path}")

            return output_path
        except Exception as e:
            self.logger.error(f"Error trimming video: {str(e)}")
            return None

    def extract_frame(self, video_path: str, time_position: float = 0) -> Optional[str]:
        """
        Витягує кадр з відео для використання як мініатюру.

        Args:
            video_path: Шлях до відео.
            time_position: Позиція в часі для витягнення кадру (в секундах).

        Returns:
            Шлях до зображення з кадром або None у разі помилки.
        """
        if not self.is_valid_video_file(video_path):
            return None

        # Примітка: для реальної реалізації потрібно використовувати бібліотеку обробки відео,
        # наприклад, moviepy або ffmpeg-python

        # Цей код є заглушкою, в реальному додатку тут буде код витягнення кадру
        try:
            file_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.temp_dir, f"{file_name}_thumbnail.jpg")

            # В реальному коді тут буде виклик ffmpeg або іншої бібліотеки
            # Створюємо порожній файл для демонстрації
            with open(output_path, 'w') as f:
                f.write("")

            self.logger.info(f"Extracted frame saved to: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error extracting frame: {str(e)}")
            return None

    def cleanup_temp_files(self) -> None:
        """Очищає тимчасові файли."""
        try:
            # Видалення файлів, які починаються з 'temp_', 'resized_', 'trimmed_'
            prefixes = ['temp_', 'resized_', 'trimmed_']

            for filename in os.listdir(self.temp_dir):
                if any(filename.startswith(prefix) for prefix in prefixes):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self.logger.debug(f"Removed temporary file: {file_path}")

            self.logger.info("Temporary files cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary files: {str(e)}")
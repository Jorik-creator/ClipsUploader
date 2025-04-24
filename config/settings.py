# config/settings.py

"""
Модуль налаштувань додатку YouTube Uploader.
Містить константи та параметри налаштувань для всіх компонентів додатку.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Базові шляхи
APP_DIR = Path(__file__).parent.parent
CONFIG_DIR = APP_DIR / "config"
RESOURCES_DIR = APP_DIR / "resources"
LOGS_DIR = APP_DIR / "logs"
TEMP_DIR = APP_DIR / "temp"

# Створення необхідних директорій
for directory in [LOGS_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Шлях до файлу конфігурації
CONFIG_FILE = CONFIG_DIR / "app_config.json"

# Шлях до секретів клієнта OAuth (в реальному додатку має бути доданий в .gitignore)
CLIENT_SECRET_FILE = CONFIG_DIR / "client_secret.json"

# Директорія для зберігання токенів автентифікації
TOKENS_DIR = APP_DIR / ".tokens"
TOKENS_DIR.mkdir(exist_ok=True)

# Налаштування YouTube API
YOUTUBE_CATEGORY_IDS = {
    "Фільми та анімація": "1",
    "Авто та транспорт": "2",
    "Музика": "10",
    "Тварини": "15",
    "Спорт": "17",
    "Подорожі та події": "19",
    "Ігри": "20",
    "Люди та блоги": "22",
    "Гумор": "23",
    "Розваги": "24",
    "Новини та політика": "25",
    "Практичні поради та стиль": "26",
    "Освіта": "27",
    "Наука і технології": "28",
    "Громадський рух": "29"
}

# Налаштування за замовчуванням
DEFAULT_SETTINGS = {
    "general": {
        "theme": "Системна",
        "temp_path": str(TEMP_DIR),
        "language": "uk"
    },
    "youtube": {
        "default_privacy": "private",
        "default_category": "22",  # "Люди та блоги"
        "notify_subscribers": False
    },
    "sheets": {
        "spreadsheet_id": "",
        "sheet_name": "Завантаження відео",
        "create_if_not_exists": True
    }
}


class AppSettings:
    """
    Клас для роботи з налаштуваннями додатку.
    Забезпечує завантаження, збереження та доступ до налаштувань.
    """

    def __init__(self):
        """Ініціалізує об'єкт налаштувань."""
        self.logger = logging.getLogger(__name__)
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> bool:
        """
        Завантажує налаштування з файлу.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    stored_settings = json.load(f)

                    # Оновлення налаштувань зі збереженими
                    for section, values in stored_settings.items():
                        if section in self.settings:
                            self.settings[section].update(values)

                self.logger.info("Settings loaded successfully")
                return True
            else:
                self.logger.info("Settings file does not exist, using defaults")
                return False
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            return False

    def save(self) -> bool:
        """
        Зберігає налаштування у файл.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            self.logger.info("Settings saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Отримує значення налаштування.

        Args:
            section: Розділ налаштувань.
            key: Ключ налаштування.
            default: Значення за замовчуванням, якщо налаштування не знайдено.

        Returns:
            Значення налаштування або значення за замовчуванням.
        """
        return self.settings.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Встановлює значення налаштування.

        Args:
            section: Розділ налаштувань.
            key: Ключ налаштування.
            value: Нове значення.
        """
        if section not in self.settings:
            self.settings[section] = {}

        self.settings[section][key] = value
        self.logger.debug(f"Setting {section}.{key} changed to {value}")

    def update(self, settings_dict: Dict[str, Any]) -> None:
        """
        Оновлює кілька налаштувань одночасно.

        Args:
            settings_dict: Словник з новими налаштуваннями у форматі {'section.key': value}.
        """
        for key, value in settings_dict.items():
            if '.' in key:
                section, setting = key.split('.', 1)
                self.set(section, setting, value)
            else:
                self.logger.warning(f"Invalid setting key format: {key}")
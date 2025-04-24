# gui/settings_widget.py

"""
Віджет налаштувань для додатку YouTube Uploader.
Забезпечує інтерфейс для налаштування інтеграції з Google Sheets та інших параметрів додатку.
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QFormLayout,
    QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsWidget(QWidget):
    """
    Віджет налаштувань додатку.
    Дозволяє налаштувати інтеграцію з Google Sheets та інші параметри програми.
    """

    # Сигнали
    settings_saved = pyqtSignal(dict)  # Сигнал про збереження налаштувань

    def __init__(self):
        """Ініціалізує віджет налаштувань."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Налаштування інтерфейсу
        self.init_ui()
        self.logger.info("Settings widget initialized")

    def init_ui(self):
        """Налаштовує користувацький інтерфейс віджета."""
        main_layout = QVBoxLayout(self)

        # Секція налаштувань Google Sheets
        self.create_sheets_settings_section(main_layout)

        # Секція налаштувань шаблонів метаданих
        self.create_templates_section(main_layout)

        # Секція загальних налаштувань
        self.create_general_settings_section(main_layout)

        # Кнопки збереження/скасування
        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Зберегти налаштування")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Скинути налаштування")
        self.reset_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_button)

        main_layout.addLayout(buttons_layout)

        # Заповнення полів збереженими налаштуваннями
        self.load_settings()

        self.logger.info("Settings widget UI setup complete")

    def create_sheets_settings_section(self, parent_layout):
        """
        Створює секцію налаштувань інтеграції з Google Sheets.

        Args:
            parent_layout: Батьківський макет.
        """
        sheets_group = QGroupBox("Налаштування Google Sheets")
        sheets_layout = QFormLayout(sheets_group)

        # ID таблиці
        self.spreadsheet_id_edit = QLineEdit()
        self.spreadsheet_id_edit.setPlaceholderText("Наприклад: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
        sheets_layout.addRow("ID таблиці:", self.spreadsheet_id_edit)

        # Назва листа
        self.sheet_name_edit = QLineEdit()
        self.sheet_name_edit.setPlaceholderText("Лист1")
        sheets_layout.addRow("Назва листа:", self.sheet_name_edit)

        # Створення нової таблиці
        create_sheet_layout = QHBoxLayout()
        self.create_sheet_check = QCheckBox("Створити нову таблицю, якщо не існує")
        self.create_sheet_check.setChecked(True)
        create_sheet_layout.addWidget(self.create_sheet_check)

        sheets_layout.addRow("", create_sheet_layout)

        parent_layout.addWidget(sheets_group)

    def create_templates_section(self, parent_layout):
        """
        Створює секцію налаштувань шаблонів метаданих.

        Args:
            parent_layout: Батьківський макет.
        """
        templates_group = QGroupBox("Шаблони метаданих")
        templates_layout = QFormLayout(templates_group)

        # Вибір шаблону
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Основний шаблон", "Додати новий шаблон..."])
        templates_layout.addRow("Шаблон:", self.template_combo)

        # Операції з шаблонами
        templates_buttons_layout = QHBoxLayout()

        self.save_template_button = QPushButton("Зберегти як шаблон")
        templates_buttons_layout.addWidget(self.save_template_button)

        self.delete_template_button = QPushButton("Видалити шаблон")
        templates_buttons_layout.addWidget(self.delete_template_button)

        templates_layout.addRow("", templates_buttons_layout)

        parent_layout.addWidget(templates_group)

    def create_general_settings_section(self, parent_layout):
        """
        Створює секцію загальних налаштувань додатку.

        Args:
            parent_layout: Батьківський макет.
        """
        general_group = QGroupBox("Загальні налаштування")
        general_layout = QFormLayout(general_group)

        # Вибір теми
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Світла", "Темна", "Системна"])
        general_layout.addRow("Тема інтерфейсу:", self.theme_combo)

        # Шлях для збереження тимчасових файлів
        temp_path_layout = QHBoxLayout()
        self.temp_path_edit = QLineEdit()
        temp_path_layout.addWidget(self.temp_path_edit)

        self.browse_temp_button = QPushButton("Вибрати...")
        self.browse_temp_button.clicked.connect(self.browse_temp_folder)
        temp_path_layout.addWidget(self.browse_temp_button)

        general_layout.addRow("Папка для тимчасових файлів:", temp_path_layout)

        parent_layout.addWidget(general_group)

    def browse_temp_folder(self):
        """Відкриває діалог вибору папки для тимчасових файлів."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Виберіть папку для тимчасових файлів",
            str(Path.home())
        )

        if folder_path:
            self.temp_path_edit.setText(folder_path)

    def load_settings(self):
        """Завантажує збережені налаштування."""
        # В реальному додатку тут буде завантаження з конфігураційного файлу
        # Це демонстраційний код
        self.logger.info("Loading settings")

        # Демонстраційні значення
        self.spreadsheet_id_edit.setText("")
        self.sheet_name_edit.setText("Завантаження відео")
        self.theme_combo.setCurrentText("Системна")
        self.temp_path_edit.setText(str(Path.home() / "temp"))

    def save_settings(self):
        """Зберігає поточні налаштування."""
        self.logger.info("Saving settings")

        # Збір налаштувань
        settings = {
            'spreadsheet_id': self.spreadsheet_id_edit.text(),
            'sheet_name': self.sheet_name_edit.text(),
            'create_if_not_exists': self.create_sheet_check.isChecked(),
            'theme': self.theme_combo.currentText(),
            'temp_path': self.temp_path_edit.text()
        }

        # В реальному додатку тут буде збереження в конфігураційний файл
        self.logger.info(f"Would save settings: {settings}")

        # Сповіщення користувача
        QMessageBox.information(
            self,
            "Налаштування",
            "Налаштування успішно збережено."
        )

        # Емісія сигналу про збереження налаштувань
        self.settings_saved.emit(settings)

    def reset_settings(self):
        """Скидає налаштування до значень за замовчуванням."""
        self.logger.info("Resetting settings")

        # Запит на підтвердження
        reply = QMessageBox.question(
            self,
            "Скидання налаштувань",
            "Ви впевнені, що хочете скинути всі налаштування до значень за замовчуванням?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Скидання налаштувань
            self.spreadsheet_id_edit.clear()
            self.sheet_name_edit.setText("Лист1")
            self.create_sheet_check.setChecked(True)
            self.theme_combo.setCurrentText("Системна")
            self.temp_path_edit.setText(str(Path.home() / "temp"))

            self.logger.info("Settings reset to defaults")
# gui/upload_widget.py

"""
Віджет для завантаження відео на YouTube.
Забезпечує інтерфейс для вибору файлів, введення метаданих та керування завантаженням.
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QComboBox,
    QFileDialog, QProgressBar, QGroupBox, QFormLayout,
    QCheckBox, QSpinBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal


class UploadWidget(QWidget):
    """
    Віджет для завантаження відео на YouTube.
    """

    # Сигнали
    upload_started = pyqtSignal(str)  # Сигнал про початок завантаження (шлях до файлу)
    upload_progress = pyqtSignal(int)  # Сигнал прогресу завантаження (відсоток)
    upload_completed = pyqtSignal(dict)  # Сигнал про завершення (метадані відео)
    upload_error = pyqtSignal(str)  # Сигнал про помилку (повідомлення)

    def __init__(self):
        """Ініціалізує віджет завантаження відео."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Ініціалізація змінних стану
        self.video_path = None

        # Налаштування інтерфейсу
        self.init_ui()
        self.logger.info("Upload widget initialized")

    def init_ui(self):
        """Налаштовує користувацький інтерфейс віджета."""
        main_layout = QVBoxLayout(self)

        # Секція вибору файлу
        self.create_file_selection_section(main_layout)

        # Секція метаданих відео
        self.create_metadata_section(main_layout)

        # Секція налаштувань завантаження
        self.create_upload_settings_section(main_layout)

        # Секція керування завантаженням
        self.create_upload_control_section(main_layout)

        self.logger.info("Upload widget UI setup complete")

    def create_file_selection_section(self, parent_layout):
        """
        Створює секцію вибору відеофайлу.

        Args:
            parent_layout: Батьківський макет.
        """
        file_group = QGroupBox("Вибір відеофайлу")
        file_layout = QVBoxLayout(file_group)

        # Кнопка вибору файлу та відображення шляху
        file_select_layout = QHBoxLayout()
        self.file_path_label = QLabel("Файл не вибрано")
        file_select_layout.addWidget(self.file_path_label, 1)

        self.browse_button = QPushButton("Обрати файл...")
        self.browse_button.clicked.connect(self.browse_file)
        file_select_layout.addWidget(self.browse_button)

        file_layout.addLayout(file_select_layout)

        # Інформація про вибраний файл
        self.file_info_label = QLabel("Інформація про файл: -")
        file_layout.addWidget(self.file_info_label)

        parent_layout.addWidget(file_group)

    def create_metadata_section(self, parent_layout):
        """
        Створює секцію введення метаданих відео.

        Args:
            parent_layout: Батьківський макет.
        """
        metadata_group = QGroupBox("Метадані відео")
        metadata_layout = QFormLayout(metadata_group)

        # Назва відео
        self.title_edit = QLineEdit()
        metadata_layout.addRow("Назва:", self.title_edit)

        # Опис відео
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        metadata_layout.addRow("Опис:", self.description_edit)

        # Теги
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Теги через кому")
        metadata_layout.addRow("Теги:", self.tags_edit)

        # Категорія
        self.category_combo = QComboBox()
        # Заповнення категорій YouTube
        categories = [
            "Фільми та анімація", "Авто та транспорт", "Музика", "Тварини",
            "Спорт", "Подорожі та події", "Ігри", "Люди та блоги",
            "Гумор", "Розваги", "Новини та політика", "Практичні поради та стиль",
            "Освіта", "Наука і технології", "Громадський рух"
        ]
        self.category_combo.addItems(categories)
        metadata_layout.addRow("Категорія:", self.category_combo)

        # Приватність
        self.privacy_combo = QComboBox()
        privacy_options = ["Публічне", "Непублічне", "Приватне"]
        self.privacy_combo.addItems(privacy_options)
        metadata_layout.addRow("Доступ:", self.privacy_combo)

        # Мініатюра
        thumbnail_layout = QHBoxLayout()
        self.thumbnail_path_label = QLabel("Мініатюра не вибрана")
        thumbnail_layout.addWidget(self.thumbnail_path_label, 1)

        self.thumbnail_button = QPushButton("Обрати мініатюру...")
        self.thumbnail_button.clicked.connect(self.browse_thumbnail)
        thumbnail_layout.addWidget(self.thumbnail_button)

        metadata_layout.addRow("Мініатюра:", thumbnail_layout)

        parent_layout.addWidget(metadata_group)

    def create_upload_settings_section(self, parent_layout):
        """
        Створює секцію налаштувань завантаження.

        Args:
            parent_layout: Батьківський макет.
        """
        settings_group = QGroupBox("Налаштування завантаження")
        settings_layout = QFormLayout(settings_group)

        # Планування публікації
        schedule_layout = QHBoxLayout()
        self.schedule_check = QCheckBox("Запланувати публікацію")
        schedule_layout.addWidget(self.schedule_check)

        self.schedule_datetime = QDateTimeEdit()
        self.schedule_datetime.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.schedule_datetime.setEnabled(False)
        schedule_layout.addWidget(self.schedule_datetime)

        # Зв'язування чекбокса з полем дати
        self.schedule_check.toggled.connect(self.schedule_datetime.setEnabled)

        settings_layout.addRow("Планування:", schedule_layout)

        # Додати в Google Sheets
        self.sheets_check = QCheckBox("Записати інформацію в Google Sheets")
        self.sheets_check.setChecked(True)
        settings_layout.addRow("Облік:", self.sheets_check)

        parent_layout.addWidget(settings_group)

    def create_upload_control_section(self, parent_layout):
        """
        Створює секцію керування завантаженням.

        Args:
            parent_layout: Батьківський макет.
        """
        control_layout = QVBoxLayout()

        # Прогрес-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        control_layout.addWidget(self.progress_bar)

        # Кнопки керування
        buttons_layout = QHBoxLayout()

        self.upload_button = QPushButton("Завантажити на YouTube")
        self.upload_button.clicked.connect(self.start_upload)
        self.upload_button.setEnabled(False)
        buttons_layout.addWidget(self.upload_button)

        self.cancel_button = QPushButton("Скасувати")
        self.cancel_button.clicked.connect(self.cancel_upload)
        self.cancel_button.setEnabled(False)
        buttons_layout.addWidget(self.cancel_button)

        control_layout.addLayout(buttons_layout)

        parent_layout.addLayout(control_layout)

    def browse_file(self):
        """Відкриває діалог вибору відеофайлу."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть відеофайл",
            "",
            "Відеофайли (*.mp4 *.avi *.mov *.wmv *.flv *.mkv)"
        )

        if file_path:
            self.video_path = file_path
            self.file_path_label.setText(Path(file_path).name)

            # Отримання інформації про файл
            file_info = Path(file_path)
            size_mb = file_info.stat().st_size / (1024 * 1024)

            self.file_info_label.setText(f"Інформація про файл: {file_info.name}, "
                                         f"Розмір: {size_mb:.2f} МБ")

            # Активація кнопки завантаження
            self.upload_button.setEnabled(True)

            self.logger.info(f"Selected video file: {file_path}")

    def browse_thumbnail(self):
        """Відкриває діалог вибору зображення для мініатюри."""
        thumbnail_path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть зображення для мініатюри",
            "",
            "Зображення (*.jpg *.jpeg *.png)"
        )

        if thumbnail_path:
            self.thumbnail_path_label.setText(Path(thumbnail_path).name)
            self.logger.info(f"Selected thumbnail: {thumbnail_path}")

    def start_upload(self):
        """Розпочинає процес завантаження відео на YouTube."""
        if not self.video_path:
            self.logger.warning("Attempted to upload without selecting a file")
            return

        self.logger.info("Starting upload process")

        # Збирання метаданих
        metadata = {
            'title': self.title_edit.text(),
            'description': self.description_edit.toPlainText(),
            'tags': [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()],
            'category': self.category_combo.currentText(),
            'privacy': self.privacy_combo.currentText(),
            'file_path': self.video_path,
            'add_to_sheets': self.sheets_check.isChecked()
        }

        # Перевірка обов'язкових полів
        if not metadata['title']:
            self.logger.warning("Upload attempted without title")
            return

        # Перевірка планування
        if self.schedule_check.isChecked():
            metadata['scheduled_time'] = self.schedule_datetime.dateTime().toString(Qt.DateFormat.ISODate)

        # Оновлення інтерфейсу
        self.progress_bar.setValue(0)
        self.upload_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Імітація процесу завантаження (в реальному додатку тут буде виклик API)
        # В цьому місці ви інтегруватимете взаємодію з YouTube API
        self.logger.info(f"Upload would start with metadata: {metadata}")

        # Емісія сигналу для початку завантаження
        self.upload_started.emit(self.video_path)

        # В реальному додатку тут буде асинхронний виклик API YouTube

    def cancel_upload(self):
        """Скасовує поточне завантаження."""
        self.logger.info("Upload canceled by user")

        # Оновлення інтерфейсу
        self.progress_bar.setValue(0)
        self.upload_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        # В реальному додатку тут буде логіка скасування завантаження

    def update_progress(self, percent):
        """
        Оновлює прогрес-бар під час завантаження.

        Args:
            percent: Відсоток завершення завантаження.
        """
        self.progress_bar.setValue(percent)

        # Якщо завантаження завершено
        if percent >= 100:
            self.upload_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
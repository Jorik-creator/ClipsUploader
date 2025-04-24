# gui/upload_widget.py

"""
Віджет для завантаження відео на YouTube.
Забезпечує інтерфейс для вибору файлів, введення метаданих та керування завантаженням.
"""

import logging
import asyncio
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QComboBox,
    QFileDialog, QProgressBar, QGroupBox, QFormLayout,
    QCheckBox, QSpinBox, QDateTimeEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal, QThreadPool, QRunnable, pyqtSlot, QThread

from core.youtube_api import YouTubeAPI
from core.sheets_api import GoogleSheetsAPI
import webbrowser
from config.settings import AppSettings
from config.settings import YOUTUBE_CATEGORY_IDS


class UploadWorker(QThread):
    """Клас для асинхронного завантаження відео в окремому потоці."""

    progress_signal = pyqtSignal(int)
    completed_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, youtube_api, video_path, metadata):
        """
        Ініціалізує робітника для завантаження відео.

        Args:
            youtube_api: Екземпляр класу YouTubeAPI.
            video_path: Шлях до відеофайлу.
            metadata: Словник з метаданими відео.
        """
        super().__init__()
        self.youtube_api = youtube_api
        self.video_path = video_path
        self.metadata = metadata
        self.logger = logging.getLogger(__name__)

    async def upload_async(self):
        """Асинхронний метод для завантаження відео."""
        try:
            # Визначення категорії
            category_id = YOUTUBE_CATEGORY_IDS.get(
                self.metadata.get('category'),
                "22"  # "Люди та блоги" за замовчуванням
            )

            # Визначення приватності
            privacy_mapping = {
                "Публічне": "public",
                "Непублічне": "unlisted",
                "Приватне": "private"
            }
            privacy_status = privacy_mapping.get(self.metadata.get('privacy'), "private")

            # Завантаження відео
            response = await self.youtube_api.upload_video(
                file_path=self.video_path,
                title=self.metadata.get('title', ''),
                description=self.metadata.get('description', ''),
                tags=self.metadata.get('tags', []),
                category_id=category_id,
                privacy_status=privacy_status,
                notify_subscribers=self.metadata.get('notify_subscribers', False),
                progress_callback=lambda progress: self.progress_signal.emit(progress)
            )

            if response:
                # Якщо завантаження успішне, повертаємо відповідь з API
                return response
            else:
                raise Exception("Не вдалося завантажити відео. API повернув порожню відповідь.")

        except Exception as e:
            self.logger.error(f"Error during video upload: {str(e)}")
            raise

    def run(self):
        """Запускає завантаження відео в окремому потоці."""
        try:
            # Створюємо цикл подій asyncio для поточного потоку
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Запускаємо асинхронну функцію завантаження
            response = loop.run_until_complete(self.upload_async())

            # Закриваємо цикл подій
            loop.close()

            # Формуємо дані для сигналу завершення
            video_data = {
                'id': response.get('id', ''),
                'title': self.metadata.get('title', ''),
                'description': self.metadata.get('description', ''),
                'tags': self.metadata.get('tags', []),
                'category': self.metadata.get('category', ''),
                'privacy_status': self.metadata.get('privacy', ''),
                'file_path': self.video_path
            }

            # Емітуємо сигнал про успішне завершення
            self.completed_signal.emit(video_data)

        except Exception as e:
            # Емітуємо сигнал про помилку
            self.error_signal.emit(str(e))


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
        self.thumbnail_path = None
        self.youtube_api = None
        self.sheets_api = None
        self.upload_worker = None

        # Налаштування інтерфейсу
        self.init_ui()
        self.logger.info("Upload widget initialized")

    def open_spreadsheet(self, spreadsheet_id):
        """
        Відкриває таблицю Google Sheets у браузері.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
        """
        try:
            import webbrowser
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            webbrowser.open(url)
            self.logger.info(f"Opening spreadsheet: {url}")
        except Exception as e:
            self.logger.error(f"Error opening spreadsheet: {str(e)}")
            QMessageBox.critical(
                self,
                "Помилка",
                f"Не вдалося відкрити таблицю у браузері:\n\n{str(e)}"
            )

    def set_api_services(self, youtube_api, sheets_api):
        """
        Встановлює сервіси API для завантаження відео.

        Args:
            youtube_api: Екземпляр класу YouTubeAPI.
            sheets_api: Екземпляр класу GoogleSheetsAPI.
        """
        self.youtube_api = youtube_api
        self.sheets_api = sheets_api

        # Активуємо кнопку завантаження, якщо вибрано файл
        if self.video_path:
            self.upload_button.setEnabled(True)

        self.logger.info("API services set for upload widget")

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
        categories = list(YOUTUBE_CATEGORY_IDS.keys())
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

        # Повідомити підписників
        self.notify_check = QCheckBox("Повідомити підписників")
        self.notify_check.setChecked(False)
        settings_layout.addRow("Повідомлення:", self.notify_check)

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

            # Заповнюємо назву відео на основі імені файлу
            file_name = file_info.stem  # Ім'я файлу без розширення
            self.title_edit.setText(file_name)

            # Активація кнопки завантаження, якщо є API
            if self.youtube_api:
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
            self.thumbnail_path = thumbnail_path
            self.thumbnail_path_label.setText(Path(thumbnail_path).name)
            self.logger.info(f"Selected thumbnail: {thumbnail_path}")

    def start_upload(self):
        """Розпочинає процес завантаження відео на YouTube."""
        if not self.video_path:
            self.logger.warning("Attempted to upload without selecting a file")
            QMessageBox.warning(
                self,
                "Попередження",
                "Будь ласка, виберіть відеофайл для завантаження."
            )
            return

        if not self.youtube_api or not self.youtube_api.service:
            self.logger.warning("Attempted to upload without YouTube API service")
            QMessageBox.warning(
                self,
                "Попередження",
                "Не авторизовано в YouTube API. Будь ласка, спочатку увійдіть в обліковий запис Google."
            )
            return

        # Перевірка обов'язкових полів
        if not self.title_edit.text():
            self.logger.warning("Upload attempted without title")
            QMessageBox.warning(
                self,
                "Попередження",
                "Будь ласка, введіть назву відео."
            )
            return

        self.logger.info("Starting upload process")

        # Збирання метаданих
        metadata = {
            'title': self.title_edit.text(),
            'description': self.description_edit.toPlainText(),
            'tags': [tag.strip() for tag in self.tags_edit.text().split(',') if tag.strip()],
            'category': self.category_combo.currentText(),
            'privacy': self.privacy_combo.currentText(),
            'notify_subscribers': self.notify_check.isChecked(),
            'add_to_sheets': self.sheets_check.isChecked()
        }

        # Перевірка планування
        if self.schedule_check.isChecked():
            metadata['scheduled_time'] = self.schedule_datetime.dateTime().toString(Qt.DateFormat.ISODate)

        # Оновлення інтерфейсу
        self.progress_bar.setValue(0)
        self.upload_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Створення і запуск робітника для завантаження
        self.upload_worker = UploadWorker(self.youtube_api, self.video_path, metadata)
        self.upload_worker.progress_signal.connect(self.update_progress)
        self.upload_worker.completed_signal.connect(self.handle_upload_complete)
        self.upload_worker.error_signal.connect(self.handle_upload_error)

        # Емісія сигналу для початку завантаження
        self.upload_started.emit(self.video_path)

        # Запуск робітника в окремому потоці
        self.upload_worker.start()

    def cancel_upload(self):
        """Скасовує поточне завантаження."""
        if self.upload_worker and self.upload_worker.isRunning():
            # Зупиняємо потік (в реальній реалізації тут має бути механізм безпечної зупинки)
            self.upload_worker.terminate()
            self.upload_worker = None

            self.logger.info("Upload canceled by user")

            # Оновлення інтерфейсу
            self.progress_bar.setValue(0)
            self.upload_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

            QMessageBox.information(
                self,
                "Завантаження скасовано",
                "Завантаження відео було скасовано."
            )

    def update_progress(self, percent):
        """
        Оновлює прогрес-бар під час завантаження.

        Args:
            percent: Відсоток завершення завантаження.
        """
        self.progress_bar.setValue(percent)
        self.upload_progress.emit(percent)

    def handle_upload_complete(self, video_data):
        """
        Обробляє завершення завантаження відео.

        Args:
            video_data: Словник з даними про завантажене відео.
        """
        self.logger.info(f"Video upload completed: {video_data.get('id')}")

        # Встановлення мініатюри, якщо вибрана
        if self.thumbnail_path and video_data.get('id'):
            try:
                success = self.youtube_api.set_thumbnail(video_data['id'], self.thumbnail_path)
                if success:
                    self.logger.info(f"Thumbnail set for video {video_data['id']}")
                else:
                    self.logger.warning(f"Failed to set thumbnail for video {video_data['id']}")
            except Exception as e:
                self.logger.error(f"Error setting thumbnail: {str(e)}")

        # Запис в Google Sheets, якщо вибрано
        if self.sheets_check.isChecked() and self.sheets_api and self.sheets_api.service:
            try:
                # Отримання ID таблиці та назви листа з налаштувань
                from config.settings import AppSettings
                settings = AppSettings()

                spreadsheet_id = settings.get("sheets", "spreadsheet_id", "")
                sheet_name = settings.get("sheets", "sheet_name", "Лист1")
                create_if_not_exists = settings.get("sheets", "create_if_not_exists", True)

                # Якщо ID таблиці не вказано, але дозволено створення
                if not spreadsheet_id and create_if_not_exists:
                    new_spreadsheet_id = self.sheets_api.create_spreadsheet("YouTube Uploader - Завантаження відео")

                    if new_spreadsheet_id:
                        # Збереження ID нової таблиці
                        settings.set("sheets", "spreadsheet_id", new_spreadsheet_id)
                        settings.save()

                        spreadsheet_id = new_spreadsheet_id
                        self.logger.info(f"Created new spreadsheet with ID: {spreadsheet_id}")

                        QMessageBox.information(
                            self,
                            "Створено нову таблицю",
                            f"Створено нову таблицю Google Sheets для запису даних про відео.\n\n"
                            f"ID таблиці: {spreadsheet_id}\n\n"
                            f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
                        )

                        # Запрошення відкрити таблицю
                        reply = QMessageBox.question(
                            self,
                            "Відкрити таблицю?",
                            "Бажаєте відкрити таблицю у браузері?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.Yes
                        )

                        if reply == QMessageBox.StandardButton.Yes:
                            import webbrowser
                            webbrowser.open(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

                # Перевірка наявності ID таблиці
                if not spreadsheet_id:
                    QMessageBox.warning(
                        self,
                        "Увага",
                        "ID таблиці Google Sheets не вказано в налаштуваннях. "
                        "Дані не будуть збережені."
                    )
                    return

                # Додаємо запис у таблицю
                success = self.sheets_api.add_video_record(spreadsheet_id, sheet_name, video_data)

                if success:
                    self.logger.info(f"Video data added to Google Sheets")
                    # Повідомлення додане в основне інформаційне вікно
                else:
                    self.logger.warning("Failed to add video data to Google Sheets")
                    QMessageBox.warning(
                        self,
                        "Увага",
                        "Не вдалося записати дані про відео в Google Sheets."
                    )
            except Exception as e:
                self.logger.error(f"Error adding video data to Google Sheets: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Помилка",
                    f"Сталася помилка при роботі з Google Sheets:\n\n{str(e)}"
                )

        # Оновлення інтерфейсу
        self.progress_bar.setValue(100)
        self.upload_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        # Повідомлення про успішне завантаження
        QMessageBox.information(
            self,
            "Завантаження завершено",
            f"Відео успішно завантажено на YouTube.\n\n"
            f"ID відео: {video_data.get('id')}\n"
            f"URL: https://www.youtube.com/watch?v={video_data.get('id')}"
        )

        # Емісія сигналу про завершення
        self.upload_completed.emit(video_data)

        # Очищення робітника
        self.upload_worker = None

    def handle_upload_error(self, error_message):
        """
        Обробляє помилку завантаження відео.

        Args:
            error_message: Повідомлення про помилку.
        """
        self.logger.error(f"Video upload error: {error_message}")

        # Оновлення інтерфейсу
        self.progress_bar.setValue(0)
        self.upload_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        # Повідомлення про помилку
        QMessageBox.critical(
            self,
            "Помилка завантаження",
            f"Під час завантаження відео сталася помилка:\n\n{error_message}"
        )

        # Емісія сигналу про помилку
        self.upload_error.emit(error_message)

        # Очищення робітника
        self.upload_worker = None
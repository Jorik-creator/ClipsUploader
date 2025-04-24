# gui/main_window.py

"""
Головне вікно додатку YouTube Uploader.
Забезпечує основний інтерфейс користувача та менеджмент підвіджетів.
"""

import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QStatusBar,
    QMessageBox, QFileDialog, QDialog, QTextBrowser
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

from gui.auth_widget import AuthWidget
from gui.upload_widget import UploadWidget
from gui.settings_widget import SettingsWidget
from core.auth import GoogleAuth
from core.youtube_api import YouTubeAPI
from core.sheets_api import GoogleSheetsAPI
from config.settings import APP_DIR, CLIENT_SECRET_FILE, TOKENS_DIR


class OAuthInstructionsDialog(QDialog):
    """
    Діалогове вікно з інструкціями щодо створення OAuth файлу.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Інструкції з отримання OAuth облікових даних")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        instructions = QTextBrowser()
        instructions.setOpenExternalLinks(True)
        instructions.setHtml("""
        <h2>Як отримати файл client_secret.json</h2>
        <p>Для роботи з YouTube API та Google Sheets API вам потрібно створити обліковий запис розробника Google та налаштувати OAuth 2.0.</p>

        <h3>Кроки:</h3>
        <ol>
            <li><b>Створіть проект у Google Cloud Console:</b>
                <ul>
                    <li>Відвідайте <a href="https://console.cloud.google.com/">Google Cloud Console</a></li>
                    <li>Натисніть кнопку "Створити проект"</li>
                    <li>Введіть назву проекту (наприклад, "YouTube Uploader") і натисніть "Створити"</li>
                </ul>
            </li>
            <br>
            <li><b>Активуйте необхідні API:</b>
                <ul>
                    <li>В меню ліворуч виберіть "API і сервіси" > "Бібліотека"</li>
                    <li>Знайдіть і активуйте "YouTube Data API v3"</li>
                    <li>Знайдіть і активуйте "Google Sheets API v4"</li>
                </ul>
            </li>
            <br>
            <li><b>Налаштуйте екран згоди OAuth:</b>
                <ul>
                    <li>В меню ліворуч виберіть "API і сервіси" > "Екран згоди OAuth"</li>
                    <li>Виберіть тип "Зовнішній" і натисніть "Створити"</li>
                    <li>Заповніть обов'язкові поля (назва додатка, email підтримки)</li>
                    <li>Додайте в області доступу (scopes) необхідні API:
                        <ul>
                            <li>https://www.googleapis.com/auth/youtube.upload</li>
                            <li>https://www.googleapis.com/auth/youtube</li>
                            <li>https://www.googleapis.com/auth/spreadsheets</li>
                        </ul>
                    </li>
                    <li>Завершіть налаштування</li>
                </ul>
            </li>
            <br>
            <li><b>Створіть облікові дані OAuth 2.0:</b>
                <ul>
                    <li>В меню ліворуч виберіть "API і сервіси" > "Облікові дані"</li>
                    <li>Натисніть "Створити облікові дані" > "ID клієнта OAuth"</li>
                    <li>Виберіть тип додатка "Десктопний додаток"</li>
                    <li>Введіть назву (наприклад, "YouTube Uploader Desktop Client")</li>
                    <li>Натисніть "Створити"</li>
                </ul>
            </li>
            <br>
            <li><b>Завантажте і налаштуйте файл JSON:</b>
                <ul>
                    <li>Натисніть на іконку завантаження, щоб отримати файл JSON</li>
                    <li>Перейменуйте файл на "client_secret.json"</li>
                    <li>Створіть папку "config" у кореневій директорії цього додатка (якщо вона ще не існує)</li>
                    <li>Помістіть файл client_secret.json у папку "config"</li>
                </ul>
            </li>
        </ol>

        <p><b>Шлях до файлу повинен бути:</b> {}</p>

        <p>Після створення файлу перезапустіть додаток або натисніть кнопку "Увійти" ще раз.</p>
        """.format(str(CLIENT_SECRET_FILE)))

        layout.addWidget(instructions)

        close_button = QPushButton("Закрити")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class MainWindow(QMainWindow):
    """
    Головне вікно додатку YouTube Uploader.
    Забезпечує навігацію між основними функціями програми.
    """

    def __init__(self):
        """Ініціалізує головне вікно програми."""
        super().__init__()

        self.logger = logging.getLogger(__name__)

        # Ініціалізація об'єктів для роботи з API
        self.auth = GoogleAuth(CLIENT_SECRET_FILE, str(TOKENS_DIR))
        self.youtube_api = YouTubeAPI()
        self.sheets_api = GoogleSheetsAPI()

        # Зберігання сервісів API
        self.services = {}

        self.init_ui()
        self.logger.info("Main window initialized")

        # Перевірка наявності збережених токенів і автоматичний вхід
        self.silent_login()

    def init_ui(self):
        """Налаштовує користувацький інтерфейс."""
        # Основні параметри вікна
        self.setWindowTitle("YouTube Uploader з інтеграцією Google Sheets")
        self.setMinimumSize(900, 700)

        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Головний вертикальний макет
        main_layout = QVBoxLayout(central_widget)

        # Верхня панель з інформацією про стан авторизації
        self.create_top_panel(main_layout)

        # Створення вкладок
        self.create_tabs(main_layout)

        # Створення рядка стану
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готовий до роботи")

        # Створення меню
        self.create_menu()

        self.logger.info("UI setup complete")

    def create_top_panel(self, parent_layout):
        """
        Створює верхню панель з інформацією про статус автентифікації.

        Args:
            parent_layout: Батьківський макет, в який додається панель.
        """
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)

        # Інформація про авторизацію
        self.auth_status_label = QLabel("Статус автентифікації: Не авторизовано")
        top_layout.addWidget(self.auth_status_label)

        # Кнопки входу/виходу
        self.login_button = QPushButton("Увійти")
        self.login_button.clicked.connect(self.login)
        self.logout_button = QPushButton("Вийти")
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setEnabled(False)

        top_layout.addWidget(self.login_button)
        top_layout.addWidget(self.logout_button)

        parent_layout.addWidget(top_panel)

    def create_tabs(self, parent_layout):
        """
        Створює систему вкладок для навігації між функціями.

        Args:
            parent_layout: Батьківський макет, в який додаються вкладки.
        """
        self.tabs = QTabWidget()

        # Вкладка завантаження
        self.upload_widget = UploadWidget()
        self.tabs.addTab(self.upload_widget, "Завантаження відео")

        # Вкладка налаштувань
        self.settings_widget = SettingsWidget()
        self.tabs.addTab(self.settings_widget, "Налаштування")

        parent_layout.addWidget(self.tabs)

    def create_menu(self):
        """Створює головне меню програми."""
        menu_bar = self.menuBar()

        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")

        # Дія "Вихід"
        exit_action = QAction("Вихід", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Допомога"
        help_menu = menu_bar.addMenu("Допомога")

        # Дія "Налаштування OAuth"
        oauth_action = QAction("Отримати OAuth облікові дані", self)
        oauth_action.triggered.connect(self.show_oauth_instructions)
        help_menu.addAction(oauth_action)

        # Дія "Про програму"
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def check_client_secret_file(self):
        """
        Перевіряє наявність файлу з обліковими даними OAuth.

        Returns:
            bool: True, якщо файл існує, False інакше.
        """
        if not os.path.exists(CLIENT_SECRET_FILE):
            self.logger.warning(f"OAuth client secret file not found: {CLIENT_SECRET_FILE}")

            reply = QMessageBox.question(
                self,
                "Файл client_secret.json не знайдено",
                f"Файл облікових даних OAuth не знайдено за шляхом:\n{CLIENT_SECRET_FILE}\n\n"
                "Цей файл необхідний для автентифікації з API Google.\n\n"
                "Хочете переглянути інструкції з отримання цього файлу?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.show_oauth_instructions()

            return False

        return True

    def show_oauth_instructions(self):
        """Показує інструкції щодо створення файлу OAuth credentials."""
        dialog = OAuthInstructionsDialog(self)
        dialog.exec()

    def silent_login(self):
        """
        Виконує автоматичний вхід з використанням збережених токенів без відображення браузера.
        """
        if not self.check_client_secret_file():
            return

        try:
            # Перевіряємо наявність збережених токенів
            if self.auth.check_saved_credentials():
                self.logger.info("Found valid saved credentials, attempting silent login")

                # Отримуємо сервіси без відображення браузера
                self.services = self.auth.get_combined_service()

                if self.services and 'youtube' in self.services and 'sheets' in self.services:
                    # Встановлюємо сервіси для API класів
                    self.youtube_api.set_service(self.services['youtube'])
                    self.sheets_api.set_service(self.services['sheets'])

                    # Оновлюємо інтерфейс
                    self.auth_status_label.setText("Статус автентифікації: Авторизовано")
                    self.login_button.setEnabled(False)
                    self.logout_button.setEnabled(True)
                    self.statusBar.showMessage("Успішна автоматична авторизація")

                    # Передаємо сервіси віджету завантаження
                    self.upload_widget.set_api_services(self.youtube_api, self.sheets_api)

                    self.logger.info("Silent login successful")
                    return
                else:
                    self.logger.warning("Silent login failed: could not get API services")
            else:
                self.logger.info("No valid saved credentials found")
        except Exception as e:
            self.logger.error(f"Error during silent login: {str(e)}")

    def login(self, use_saved=False):
        """
        Обробник входу в обліковий запис Google.

        Args:
            use_saved: Використовувати збережені токени без відображення повідомлення.
        """
        self.logger.info("Login button clicked")

        # Перевіряємо наявність файлу client_secret.json
        if not self.check_client_secret_file():
            return

        if not use_saved:
            # Повідомлення для користувача про відкриття браузера
            QMessageBox.information(
                self,
                "Авторизація",
                "Буде відкрито вікно браузера для авторизації в Google."
            )

        try:
            # Отримуємо об'єкти сервісів для YouTube і Google Sheets
            self.services = self.auth.get_combined_service()

            if not self.services or 'youtube' not in self.services or 'sheets' not in self.services:
                self.logger.error("Failed to get API services")
                QMessageBox.critical(
                    self,
                    "Помилка автентифікації",
                    "Не вдалося отримати доступ до API Google. Будь ласка, спробуйте знову."
                )
                return

            # Встановлюємо сервіси для API класів
            self.youtube_api.set_service(self.services['youtube'])
            self.sheets_api.set_service(self.services['sheets'])

            # Оновлюємо інтерфейс
            self.auth_status_label.setText("Статус автентифікації: Авторизовано")
            self.login_button.setEnabled(False)
            self.logout_button.setEnabled(True)
            self.statusBar.showMessage("Успішна авторизація")

            self.logger.info("Successfully authenticated with Google API")

            # Якщо використовувалися збережені токени, не показуємо додаткове повідомлення
            if not use_saved:
                QMessageBox.information(
                    self,
                    "Авторизація",
                    "Успішна авторизація в Google."
                )

            # Передаємо сервіси віджету завантаження
            self.upload_widget.set_api_services(self.youtube_api, self.sheets_api)

        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            QMessageBox.critical(
                self,
                "Помилка автентифікації",
                f"Сталася помилка під час автентифікації: {str(e)}"
            )

    def logout(self):
        """Обробник виходу з облікового запису Google."""
        self.logger.info("Logout button clicked")

        reply = QMessageBox.question(
            self,
            "Підтвердження виходу",
            "Ви впевнені, що хочете вийти з облікового запису Google?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Відкликаємо токен автентифікації
                success = self.auth.revoke_token()

                if success:
                    self.services = {}
                    self.youtube_api.set_service(None)
                    self.sheets_api.set_service(None)

                    # Оновлюємо інтерфейс
                    self.auth_status_label.setText("Статус автентифікації: Не авторизовано")
                    self.login_button.setEnabled(True)
                    self.logout_button.setEnabled(False)
                    self.statusBar.showMessage("Вихід виконано успішно")

                    self.logger.info("Successfully logged out from Google API")
                else:
                    self.logger.warning("Failed to revoke token completely")
                    QMessageBox.warning(
                        self,
                        "Попередження",
                        "Не вдалося повністю відкликати токен доступу. Можливо, деякі токени залишились активними."
                    )
            except Exception as e:
                self.logger.error(f"Logout error: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Помилка виходу",
                    f"Сталася помилка під час виходу: {str(e)}"
                )

    def show_about(self):
        """Показує інформацію про програму."""
        QMessageBox.about(
            self,
            "Про програму",
            "YouTube Uploader з інтеграцією Google Sheets\n\n"
            "Версія: 1.0.0\n"
            "Призначення: Автоматизація завантаження відеоконтенту на YouTube "
            "з подальшим записом метаданих у Google Sheets."
        )

    def closeEvent(self, event):
        """
        Обробляє подію закриття вікна.

        Args:
            event: Подія закриття.
        """
        reply = QMessageBox.question(
            self,
            "Підтвердження",
            "Ви впевнені, що хочете вийти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logger.info("Application closed by user")
            event.accept()
        else:
            event.ignore()
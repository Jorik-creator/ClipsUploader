# gui/main_window.py

"""
Головне вікно додатку YouTube Uploader.
Забезпечує основний інтерфейс користувача та менеджмент підвіджетів.
"""

import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QStatusBar,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

from gui.auth_widget import AuthWidget
from gui.upload_widget import UploadWidget
from gui.settings_widget import SettingsWidget


class MainWindow(QMainWindow):
    """
    Головне вікно додатку YouTube Uploader.
    Забезпечує навігацію між основними функціями програми.
    """

    def __init__(self):
        """Ініціалізує головне вікно програми."""
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.init_ui()
        self.logger.info("Main window initialized")

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

        # Дія "Про програму"
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def login(self):
        """Обробник входу в обліковий запис Google."""
        self.logger.info("Login button clicked")

        # Тут буде логіка автентифікації
        # Для демонстрації відобразимо повідомлення
        QMessageBox.information(
            self,
            "Авторизація",
            "Буде відкрито вікно браузера для авторизації в Google."
        )

        # Тут ви будете використовувати модуль авторизації
        # В реальному додатку тут буде виклик класу GoogleAuth

        # Демонстраційний код для UI
        self.auth_status_label.setText("Статус автентифікації: Авторизовано")
        self.login_button.setEnabled(False)
        self.logout_button.setEnabled(True)
        self.statusBar.showMessage("Успішна авторизація")

    def logout(self):
        """Обробник виходу з облікового запису Google."""
        self.logger.info("Logout button clicked")

        # Тут буде логіка виходу з облікового запису
        # В реальному додатку тут буде виклик методу revoke_token класу GoogleAuth

        # Демонстраційний код для UI
        self.auth_status_label.setText("Статус автентифікації: Не авторизовано")
        self.login_button.setEnabled(True)
        self.logout_button.setEnabled(False)
        self.statusBar.showMessage("Вихід виконано успішно")

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
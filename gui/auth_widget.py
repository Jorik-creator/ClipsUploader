# gui/auth_widget.py

"""
Віджет автентифікації з Google OAuth для додатку YouTube Uploader.
Забезпечує інтерфейс для авторизації та керування обліковими записами.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QListWidget, QListWidgetItem,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class AuthWidget(QWidget):
    """
    Віджет автентифікації з Google.
    Забезпечує інтерфейс для авторизації та керування обліковими записами.
    """

    # Сигнали
    auth_success = pyqtSignal(str)  # Сигнал успішної автентифікації (ім'я облікового запису)
    auth_failure = pyqtSignal(str)  # Сигнал невдалої автентифікації (повідомлення про помилку)

    def __init__(self):
        """Ініціалізує віджет автентифікації."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Ініціалізація інтерфейсу
        self.init_ui()
        self.logger.info("Auth widget initialized")

    def init_ui(self):
        """Налаштовує користувацький інтерфейс віджета."""
        main_layout = QVBoxLayout(self)

        # Секція вибору облікового запису
        self.create_account_selection_section(main_layout)

        # Секція дій з авторизацією
        self.create_auth_actions_section(main_layout)

        # Секція статусу авторизації
        self.create_auth_status_section(main_layout)

        self.logger.info("Auth widget UI setup complete")

    def create_account_selection_section(self, parent_layout):
        """
        Створює секцію вибору облікового запису.

        Args:
            parent_layout: Батьківський макет.
        """
        accounts_group = QGroupBox("Облікові записи Google")
        accounts_layout = QVBoxLayout(accounts_group)

        # Список збережених облікових записів
        self.accounts_list = QListWidget()
        accounts_layout.addWidget(self.accounts_list)

        # Додамо демонстраційний обліковий запис
        item = QListWidgetItem("user@example.com")
        self.accounts_list.addItem(item)

        # Кнопки керування обліковими записами
        buttons_layout = QHBoxLayout()

        self.add_account_button = QPushButton("Додати обліковий запис")
        self.add_account_button.clicked.connect(self.add_account)
        buttons_layout.addWidget(self.add_account_button)

        self.remove_account_button = QPushButton("Видалити обліковий запис")
        self.remove_account_button.clicked.connect(self.remove_account)
        buttons_layout.addWidget(self.remove_account_button)

        accounts_layout.addLayout(buttons_layout)

        parent_layout.addWidget(accounts_group)

    def create_auth_actions_section(self, parent_layout):
        """
        Створює секцію дій з авторизацією.

        Args:
            parent_layout: Батьківський макет.
        """
        actions_group = QGroupBox("Дії з авторизацією")
        actions_layout = QVBoxLayout(actions_group)

        # Поля для вибору сервісів для авторизації
        self.youtube_auth_check = QLabel("YouTube API: Не авторизовано")
        actions_layout.addWidget(self.youtube_auth_check)

        self.sheets_auth_check = QLabel("Google Sheets API: Не авторизовано")
        actions_layout.addWidget(self.sheets_auth_check)

        # Кнопки авторизації
        auth_buttons_layout = QHBoxLayout()

        self.auth_button = QPushButton("Авторизуватися")
        self.auth_button.clicked.connect(self.authenticate)
        auth_buttons_layout.addWidget(self.auth_button)

        self.revoke_button = QPushButton("Відкликати доступ")
        self.revoke_button.clicked.connect(self.revoke_access)
        auth_buttons_layout.addWidget(self.revoke_button)

        actions_layout.addLayout(auth_buttons_layout)

        parent_layout.addWidget(actions_group)

    def create_auth_status_section(self, parent_layout):
        """
        Створює секцію статусу авторизації.

        Args:
            parent_layout: Батьківський макет.
        """
        status_group = QGroupBox("Статус авторизації")
        status_layout = QVBoxLayout(status_group)

        # Інформація про поточний статус
        self.status_label = QLabel("Статус: Не авторизовано")
        status_layout.addWidget(self.status_label)

        # Інформація про термін дії токена
        self.token_expiry_label = QLabel("Термін дії токена: -")
        status_layout.addWidget(self.token_expiry_label)

        parent_layout.addWidget(status_group)

    def add_account(self):
        """Додає новий обліковий запис через OAuth авторизацію."""
        self.logger.info("Adding new account")

        # В реальному додатку тут буде виклик OAuth авторизації
        # Це демонстраційний код
        QMessageBox.information(
            self,
            "Додавання облікового запису",
            "Буде відкрито вікно браузера для авторизації в Google.\n\n"
            "Після завершення авторизації, обліковий запис буде додано до списку."
        )

        # Демонстраційний код додавання облікового запису
        new_account = f"user{self.accounts_list.count() + 1}@example.com"
        self.accounts_list.addItem(new_account)

    def remove_account(self):
        """Видаляє вибраний обліковий запис зі списку."""
        selected_items = self.accounts_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "Видалення облікового запису",
                "Спочатку виберіть обліковий запис для видалення."
            )
            return

        # Підтвердження видалення
        account = selected_items[0].text()
        reply = QMessageBox.question(
            self,
            "Видалення облікового запису",
            f"Ви впевнені, що хочете видалити обліковий запис {account}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Видалення облікового запису
            row = self.accounts_list.row(selected_items[0])
            self.accounts_list.takeItem(row)
            self.logger.info(f"Removed account: {account}")

    def authenticate(self):
        """Виконує автентифікацію з вибраним обліковим записом."""
        selected_items = self.accounts_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "Автентифікація",
                "Спочатку виберіть обліковий запис для автентифікації."
            )
            return

        account = selected_items[0].text()
        self.logger.info(f"Authenticating with account: {account}")

        # В реальному додатку тут буде виклик GoogleAuth.get_combined_service
        # Це демонстраційний код

        # Імітація успішної автентифікації
        self.youtube_auth_check.setText("YouTube API: Авторизовано")
        self.sheets_auth_check.setText("Google Sheets API: Авторизовано")
        self.status_label.setText(f"Статус: Авторизовано як {account}")
        self.token_expiry_label.setText("Термін дії токена: 1 година")

        # Емісія сигналу про успішну автентифікацію
        self.auth_success.emit(account)

    def revoke_access(self):
        """Відкликає токени доступу для вибраного облікового запису."""
        selected_items = self.accounts_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "Відкликання доступу",
                "Спочатку виберіть обліковий запис для відкликання доступу."
            )
            return

        account = selected_items[0].text()
        self.logger.info(f"Revoking access for account: {account}")

        # Підтвердження відкликання
        reply = QMessageBox.question(
            self,
            "Відкликання доступу",
            f"Ви впевнені, що хочете відкликати доступ для облікового запису {account}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # В реальному додатку тут буде виклик GoogleAuth.revoke_token
            # Це демонстраційний код

            # Оновлення інтерфейсу
            self.youtube_auth_check.setText("YouTube API: Не авторизовано")
            self.sheets_auth_check.setText("Google Sheets API: Не авторизовано")
            self.status_label.setText("Статус: Не авторизовано")
            self.token_expiry_label.setText("Термін дії токена: -")

            self.logger.info(f"Access revoked for account: {account}")
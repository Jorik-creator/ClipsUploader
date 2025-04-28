# core/auth.py

"""
Модуль автентифікації з Google API через OAuth 2.0.
Забезпечує отримання та зберігання токенів для доступу до YouTube і Google Sheets.
"""

import os
import pickle
import logging
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GoogleAuth:
    """
    Клас для автентифікації з Google API через OAuth 2.0.

    Підтримує автентифікацію для YouTube Data API та Google Sheets API,
    а також керування та зберігання токенів для повторного використання.
    """

    # Області доступу для API
    YOUTUBE_SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube'
    ]

    SHEETS_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets'
    ]

    def __init__(self, client_secret_file: str, token_dir: str = '.tokens'):
        """
        Ініціалізує об'єкт автентифікації Google.

        Args:
            client_secret_file: Шлях до файлу з секретами клієнта OAuth.
            token_dir: Директорія для зберігання токенів автентифікації.
        """
        self.client_secret_file = client_secret_file
        self.token_dir = Path(token_dir)
        self.credentials = None

        # Токен файл завжди один - спрощений підхід для надійності
        self.token_file = self.token_dir / "google_token.pickle"

        # Створення директорії для токенів, якщо вона не існує
        if not self.token_dir.exists():
            self.token_dir.mkdir(parents=True, exist_ok=True)

        # Налаштування логування
        self.logger = logging.getLogger(__name__)

        # Перевірка прав доступу до директорії токенів
        try:
            test_file = self.token_dir / ".test_write"
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()  # Видаляємо тестовий файл
            self.logger.info(f"Token directory is writable: {self.token_dir}")
        except Exception as e:
            self.logger.error(f"Token directory is not writable: {self.token_dir}. Error: {e}")

        # Спробуємо завантажити збережений токен при ініціалізації
        self.load_token()

    def save_token(self) -> bool:
        """
        Зберігає токен у файл.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        if not self.credentials:
            self.logger.warning("No credentials to save")
            return False

        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)

            self.logger.info(f"Saved token to {self.token_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving token: {e}")
            return False

    def load_token(self) -> bool:
        """
        Завантажує токен з файлу.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        try:
            if self.token_file.exists():
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)

                self.logger.info(f"Loaded token from {self.token_file}")

                # Перевіряємо чи дійсний токен або можна оновити
                if self.credentials.valid:
                    self.logger.info("Token is valid")
                    return True

                if self.credentials.expired and self.credentials.refresh_token:
                    try:
                        self.credentials.refresh(Request())
                        self.logger.info("Token refreshed successfully")
                        self.save_token()  # Зберігаємо оновлений токен
                        return True
                    except Exception as e:
                        self.logger.error(f"Error refreshing token: {e}")
                        self.credentials = None
                        return False

                self.logger.warning("Token is expired and cannot be refreshed")
                self.credentials = None
                return False
            else:
                self.logger.info(f"Token file not found: {self.token_file}")
                return False
        except Exception as e:
            self.logger.error(f"Error loading token: {e}")
            self.credentials = None
            return False

    def authenticate(self) -> bool:
        """
        Автентифікує користувача через OAuth 2.0.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        # Спочатку перевіряємо, чи є дійсний токен
        if self.credentials and self.credentials.valid:
            self.logger.info("Using existing valid credentials")
            return True

        # Якщо токен прострочений, але є refresh_token, намагаємося оновити
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                self.logger.info("Token refreshed successfully")
                self.save_token()
                return True
            except Exception as e:
                self.logger.error(f"Error refreshing token: {e}")
                self.credentials = None

        # Якщо немає дійсного токена, проходимо повну автентифікацію
        try:
            if not os.path.exists(self.client_secret_file):
                self.logger.error(f"Client secret file not found: {self.client_secret_file}")
                return False

            # Об'єднуємо всі області доступу
            scopes = list(set(self.YOUTUBE_SCOPES + self.SHEETS_SCOPES))

            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file, scopes)

            # Використовуємо порт 0 для автоматичного вибору вільного порту
            self.credentials = flow.run_local_server(
                port=0,
                prompt='consent',  # Завжди запитувати згоду
                authorization_prompt_message='Будь ласка, авторизуйтесь в браузері.'
            )
            self.logger.info("Created new credentials through browser auth")

            # Зберігаємо отриманий токен
            self.save_token()
            return True
        except Exception as e:
            self.logger.error(f"Error during authentication: {e}")
            return False

    def check_saved_credentials(self) -> bool:
        """
        Перевіряє наявність збережених облікових даних.

        Returns:
            True, якщо є збережені та дійсні облікові дані, False інакше.
        """
        return self.load_token()

    def get_youtube_service(self) -> Any:
        """
        Створює сервіс для роботи з YouTube API.

        Returns:
            Сервіс YouTube API або None у разі помилки.
        """
        if not self.credentials:
            if not self.authenticate():
                self.logger.error("Failed to get YouTube API credentials")
                return None

        try:
            service = build('youtube', 'v3', credentials=self.credentials)
            self.logger.info("YouTube API service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"Error creating YouTube API service: {e}")
            return None

    def get_sheets_service(self) -> Any:
        """
        Створює сервіс для роботи з Google Sheets API.

        Returns:
            Сервіс Google Sheets API або None у разі помилки.
        """
        if not self.credentials:
            if not self.authenticate():
                self.logger.error("Failed to get Google Sheets API credentials")
                return None

        try:
            service = build('sheets', 'v4', credentials=self.credentials)
            self.logger.info("Google Sheets API service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"Error creating Google Sheets API service: {e}")
            return None

    def get_combined_service(self) -> Dict[str, Any]:
        """
        Створює сервіси для роботи з обома API (YouTube та Google Sheets).

        Returns:
            Словник сервісів API.
        """
        if not self.credentials:
            if not self.authenticate():
                self.logger.error("Failed to get combined API credentials")
                return {}

        services = {}
        try:
            services['youtube'] = build('youtube', 'v3', credentials=self.credentials)
            services['sheets'] = build('sheets', 'v4', credentials=self.credentials)
            self.logger.info("Combined API services created successfully")
        except Exception as e:
            self.logger.error(f"Error creating combined API services: {e}")

        return services

    def revoke_token(self) -> bool:
        """
        Відкликає поточний токен автентифікації та видаляє файл токена.

        Returns:
            True, якщо токен успішно відкликаний, інакше False.
        """
        if not self.credentials or not self.token_file.exists():
            self.logger.warning("No token to revoke")
            return False

        try:
            # Відкликаємо токен, якщо він має refresh_token
            if self.credentials.refresh_token:
                self.credentials.revoke(Request())
                self.logger.info("Token revoked successfully")

            # Видаляємо файл токена
            self.token_file.unlink()
            self.logger.info(f"Token file {self.token_file} deleted")

            # Очищаємо об'єкт credentials
            self.credentials = None

            return True
        except Exception as e:
            self.logger.error(f"Error revoking token: {e}")
            return False
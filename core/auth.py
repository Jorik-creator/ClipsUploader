# core/auth.py

"""
Модуль автентифікації з Google API через OAuth 2.0.
Забезпечує отримання та зберігання токенів для доступу до YouTube і Google Sheets.
"""

import os
import pickle
import logging
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
    а також керування та збереження токенів для повторного використання.
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

        # Створення директорії для токенів, якщо вона не існує
        if not self.token_dir.exists():
            self.token_dir.mkdir(parents=True)

        # Налаштування логування
        self.logger = logging.getLogger(__name__)

    def get_credentials(self, scopes: List[str], user_id: str = 'default') -> Optional[Credentials]:
        """
        Отримання та оновлення облікових даних OAuth.

        Args:
            scopes: Список областей доступу до API.
            user_id: Ідентифікатор користувача для підтримки кількох облікових записів.

        Returns:
            Об'єкт облікових даних Google або None у разі помилки.
        """
        # Формування імені файлу токена
        token_name = f"token_{user_id}_{hash(''.join(sorted(scopes)))}.pickle"
        token_path = self.token_dir / token_name

        # Спроба завантажити існуючий токен
        try:
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
                self.logger.info(f"Loaded credentials from {token_path}")
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")
            self.credentials = None

        # Перевірка дійсності токена
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self.logger.info("Refreshed credentials")
                except Exception as e:
                    self.logger.error(f"Error refreshing credentials: {e}")
                    self.credentials = None

            # Якщо токен не можна оновити, проходимо повну автентифікацію
            if not self.credentials:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secret_file, scopes)
                    self.credentials = flow.run_local_server(port=0)
                    self.logger.info("Created new credentials")
                except Exception as e:
                    self.logger.error(f"Error creating new credentials: {e}")
                    return None

            # Збереження отриманого токена
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
                self.logger.info(f"Saved credentials to {token_path}")
            except Exception as e:
                self.logger.error(f"Error saving credentials: {e}")

        return self.credentials

    def get_youtube_service(self, user_id: str = 'default') -> Any:
        """
        Створює сервіс для роботи з YouTube API.

        Args:
            user_id: Ідентифікатор користувача.

        Returns:
            Сервіс YouTube API або None у разі помилки.
        """
        credentials = self.get_credentials(self.YOUTUBE_SCOPES, user_id)
        if not credentials:
            self.logger.error("Failed to get YouTube API credentials")
            return None

        try:
            service = build('youtube', 'v3', credentials=credentials)
            self.logger.info("YouTube API service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"Error creating YouTube API service: {e}")
            return None

    def get_sheets_service(self, user_id: str = 'default') -> Any:
        """
        Створює сервіс для роботи з Google Sheets API.

        Args:
            user_id: Ідентифікатор користувача.

        Returns:
            Сервіс Google Sheets API або None у разі помилки.
        """
        credentials = self.get_credentials(self.SHEETS_SCOPES, user_id)
        if not credentials:
            self.logger.error("Failed to get Google Sheets API credentials")
            return None

        try:
            service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Google Sheets API service created successfully")
            return service
        except Exception as e:
            self.logger.error(f"Error creating Google Sheets API service: {e}")
            return None

    def get_combined_service(self, user_id: str = 'default') -> Dict[str, Any]:
        """
        Створює сервіси для роботи з обома API (YouTube та Google Sheets).

        Args:
            user_id: Ідентифікатор користувача.

        Returns:
            Словник сервісів API.
        """
        # Об'єднуємо області доступу
        combined_scopes = list(set(self.YOUTUBE_SCOPES + self.SHEETS_SCOPES))

        credentials = self.get_credentials(combined_scopes, user_id)
        if not credentials:
            self.logger.error("Failed to get combined API credentials")
            return {}

        services = {}
        try:
            services['youtube'] = build('youtube', 'v3', credentials=credentials)
            services['sheets'] = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Combined API services created successfully")
        except Exception as e:
            self.logger.error(f"Error creating combined API services: {e}")

        return services

    def revoke_token(self, user_id: str = 'default') -> bool:
        """
        Відкликає поточний токен автентифікації та видаляє файл токена.

        Args:
            user_id: Ідентифікатор користувача.

        Returns:
            True, якщо токен успішно відкликаний, інакше False.
        """
        # Знаходимо всі токени для користувача
        user_tokens = list(self.token_dir.glob(f"token_{user_id}_*.pickle"))

        success = True
        for token_path in user_tokens:
            try:
                # Завантажуємо токен
                with open(token_path, 'rb') as token_file:
                    credentials = pickle.load(token_file)

                # Відкликаємо токен, якщо він існує та має refresh_token
                if credentials and credentials.refresh_token:
                    credentials.revoke(Request())
                    self.logger.info(f"Token {token_path} revoked successfully")

                # Видаляємо файл токена
                token_path.unlink()
                self.logger.info(f"Token file {token_path} deleted")
            except Exception as e:
                self.logger.error(f"Error revoking token {token_path}: {e}")
                success = False

        return success
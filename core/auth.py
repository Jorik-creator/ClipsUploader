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
        self.token_cache = {}  # Кеш для токенів у пам'яті

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

    def _get_token_path(self, scopes: List[str], user_id: str = 'default') -> Path:
        """
        Отримує шлях до файлу токена.

        Args:
            scopes: Список областей доступу до API.
            user_id: Ідентифікатор користувача.

        Returns:
            Шлях до файлу токена.
        """
        # Для стабільності хешу, сортуємо області доступу
        scope_hash = hash(''.join(sorted(scopes)))
        token_name = f"token_{user_id}_{scope_hash}.pickle"
        return self.token_dir / token_name

    def _save_credentials(self, credentials: Credentials, token_path: Path) -> bool:
        """
        Зберігає облікові дані у файл.

        Args:
            credentials: Облікові дані для збереження.
            token_path: Шлях для збереження.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        try:
            # Переконуємося, що директорія існує
            token_path.parent.mkdir(parents=True, exist_ok=True)

            # Збереження токена
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)

            # Також зберігаємо в кеші
            self.token_cache[str(token_path)] = credentials

            self.logger.info(f"Saved credentials to {token_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving credentials to {token_path}: {e}")
            return False

    def _load_credentials(self, token_path: Path) -> Optional[Credentials]:
        """
        Завантажує облікові дані з файлу.

        Args:
            token_path: Шлях до файлу токена.

        Returns:
            Облікові дані або None у разі помилки.
        """
        # Перевіряємо кеш спочатку
        if str(token_path) in self.token_cache:
            self.logger.info(f"Using cached credentials for {token_path}")
            return self.token_cache[str(token_path)]

        try:
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    credentials = pickle.load(token)

                # Зберігаємо в кеші
                self.token_cache[str(token_path)] = credentials

                self.logger.info(f"Loaded credentials from {token_path}")
                return credentials
            else:
                self.logger.info(f"Token file not found: {token_path}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading credentials from {token_path}: {e}")
            return None

    def get_credentials(self, scopes: List[str], user_id: str = 'default') -> Optional[Credentials]:
        """
        Отримання та оновлення облікових даних OAuth.

        Args:
            scopes: Список областей доступу до API.
            user_id: Ідентифікатор користувача для підтримки кількох облікових записів.

        Returns:
            Об'єкт облікових даних Google або None у разі помилки.
        """
        # Отримуємо шлях до файлу токена
        token_path = self._get_token_path(scopes, user_id)

        # Спроба завантажити існуючий токен з кешу або з файлу
        self.credentials = self._load_credentials(token_path)

        # Перевірка дійсності токена
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self.logger.info(f"Refreshed credentials for {token_path}")

                    # Збереження оновленого токена
                    self._save_credentials(self.credentials, token_path)
                except Exception as e:
                    self.logger.error(f"Error refreshing credentials: {e}")
                    self.credentials = None

            # Якщо токен не можна оновити, проходимо повну автентифікацію
            if not self.credentials:
                try:
                    if not os.path.exists(self.client_secret_file):
                        self.logger.error(f"Client secret file not found: {self.client_secret_file}")
                        return None

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secret_file, scopes)

                    # Використовуємо порт 0 для автоматичного вибору вільного порту
                    # та локальний сервер для отримання коду авторизації
                    self.credentials = flow.run_local_server(
                        port=0,
                        prompt='consent',  # Завжди запитувати згоду
                        authorization_prompt_message='Будь ласка, авторизуйтесь в браузері.'
                    )
                    self.logger.info("Created new credentials")

                    # Збереження отриманого токена
                    self._save_credentials(self.credentials, token_path)
                except Exception as e:
                    self.logger.error(f"Error creating new credentials: {e}")
                    return None

        return self.credentials

    def check_saved_credentials(self, user_id: str = 'default') -> bool:
        """
        Перевіряє наявність збережених облікових даних.

        Args:
            user_id: Ідентифікатор користувача.

        Returns:
            True, якщо є збережені та дійсні облікові дані, False інакше.
        """
        # Об'єднуємо області доступу
        combined_scopes = list(set(self.YOUTUBE_SCOPES + self.SHEETS_SCOPES))

        # Отримуємо шлях до файлу токена
        token_path = self._get_token_path(combined_scopes, user_id)

        if not token_path.exists():
            self.logger.info(f"No saved credentials found at {token_path}")
            return False

        try:
            credentials = self._load_credentials(token_path)
            if not credentials:
                return False

            # Перевірка дійсності або можливості оновлення
            if credentials.valid:
                self.logger.info(f"Found valid credentials at {token_path}")
                return True

            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    self.logger.info(f"Refreshed expired credentials at {token_path}")

                    # Збереження оновленого токена
                    self._save_credentials(credentials, token_path)
                    return True
                except Exception as e:
                    self.logger.error(f"Error refreshing saved credentials: {e}")
                    return False

            self.logger.warning(f"Invalid credentials at {token_path} (expired and can't refresh)")
            return False
        except Exception as e:
            self.logger.error(f"Error checking saved credentials: {e}")
            return False

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

        if not user_tokens:
            self.logger.warning(f"No tokens found for user {user_id}")
            return False

        success = True
        for token_path in user_tokens:
            try:
                # Завантажуємо токен
                credentials = self._load_credentials(token_path)

                # Відкликаємо токен, якщо він існує та має refresh_token
                if credentials and credentials.refresh_token:
                    credentials.revoke(Request())
                    self.logger.info(f"Token {token_path} revoked successfully")

                # Видаляємо файл токена
                token_path.unlink()
                self.logger.info(f"Token file {token_path} deleted")

                # Видаляємо з кешу
                if str(token_path) in self.token_cache:
                    del self.token_cache[str(token_path)]
            except Exception as e:
                self.logger.error(f"Error revoking token {token_path}: {e}")
                success = False

        return success

    def serialize_credentials(self, credentials: Credentials) -> Optional[Dict[str, Any]]:
        """
        Серіалізує облікові дані в словник для збереження.

        Args:
            credentials: Облікові дані для серіалізації.

        Returns:
            Словник з даними або None у разі помилки.
        """
        if not credentials:
            return None

        try:
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            return creds_data
        except Exception as e:
            self.logger.error(f"Error serializing credentials: {e}")
            return None
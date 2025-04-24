# core/sheets_api.py

"""
Модуль для взаємодії з Google Sheets API v4.
Забезпечує функціональність для створення, оновлення та читання даних з таблиць Google Sheets.
"""

import logging
from typing import List, Dict, Any, Optional, Union
import datetime

import pandas as pd
from googleapiclient.errors import HttpError


class GoogleSheetsAPI:
    """
    Клас для взаємодії з Google Sheets API v4.

    Надає методи для роботи з таблицями Google Sheets,
    включаючи створення, читання та оновлення даних.
    """

    def __init__(self, service=None):
        """
        Ініціалізує об'єкт для роботи з Google Sheets API.

        Args:
            service: Об'єкт сервісу Google Sheets API, якщо вже створений.
        """
        self.service = service
        self.logger = logging.getLogger(__name__)

    def set_service(self, service):
        """
        Встановлює сервіс Google Sheets API.

        Args:
            service: Об'єкт сервісу Google Sheets API.
        """
        self.service = service
        self.logger.info("Google Sheets API service has been set")

    def create_spreadsheet(self, title: str) -> Optional[str]:
        """
        Створює нову таблицю Google Sheets.

        Args:
            title: Назва нової таблиці.

        Returns:
            ID створеної таблиці або None у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return None

        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }

            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId'
            ).execute()

            spreadsheet_id = spreadsheet.get('spreadsheetId')
            self.logger.info(f"Created spreadsheet with ID: {spreadsheet_id}")

            return spreadsheet_id
        except HttpError as e:
            self.logger.error(f"Google Sheets API HTTP error: {e.content.decode()}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating spreadsheet: {str(e)}")
            return None

    def get_spreadsheet_info(self, spreadsheet_id: str) -> Optional[Dict[str, Any]]:
        """
        Отримує інформацію про таблицю.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.

        Returns:
            Словник з інформацією про таблицю або None у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return None

        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()

            return spreadsheet
        except HttpError as e:
            self.logger.error(f"Google Sheets API HTTP error: {e.content.decode()}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting spreadsheet info: {str(e)}")
            return None

    def create_worksheet(self, spreadsheet_id: str, title: str) -> Optional[int]:
        """
        Створює новий лист у таблиці.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            title: Назва нового листа.

        Returns:
            ID створеного листа або None у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return None

        try:
            request = {
                'addSheet': {
                    'properties': {
                        'title': title
                    }
                }
            }

            response = self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': [request]}
            ).execute()

            sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            self.logger.info(f"Created worksheet '{title}' with ID: {sheet_id}")

            return sheet_id
        except HttpError as e:
            self.logger.error(f"Google Sheets API HTTP error: {e.content.decode()}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating worksheet: {str(e)}")
            return None

    def append_rows(
            self,
            spreadsheet_id: str,
            range_name: str,
            values: List[List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Додає рядки в кінець вказаного діапазону.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            range_name: Діапазон для додавання (наприклад, 'Sheet1!A1:D1').
            values: Список списків значень для додавання.

        Returns:
            Відповідь від API або None у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return None

        try:
            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            self.logger.info(f"Appended {result.get('updates', {}).get('updatedRows', 0)} rows")
            return result
        except HttpError as e:
            self.logger.error(f"Google Sheets API HTTP error: {e.content.decode()}")
            return None
        except Exception as e:
            self.logger.error(f"Error appending rows: {str(e)}")
            return None

    def get_values(self, spreadsheet_id: str, range_name: str) -> Optional[List[List[Any]]]:
        """
        Отримує значення з вказаного діапазону.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            range_name: Діапазон для отримання (наприклад, 'Sheet1!A1:D10').

        Returns:
            Список списків значень або None у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return None

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            self.logger.info(f"Got {len(values)} rows from {range_name}")

            return values
        except HttpError as e:
            self.logger.error(f"Google Sheets API HTTP error: {e.content.decode()}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting values: {str(e)}")
            return None

    def update_values(
            self,
            spreadsheet_id: str,
            range_name: str,
            values: List[List[Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Оновлює значення у вказаному діапазоні.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            range_name: Діапазон для оновлення (наприклад, 'Sheet1!A1:D10').
            values: Список списків нових значень.

        Returns:
            Відповідь від API або None у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return None

        try:
            body = {
                'values': values
            }

            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()

            self.logger.info(f"Updated {result.get('updatedCells', 0)} cells")
            return result
        except HttpError as e:
            self.logger.error(f"Google Sheets API HTTP error: {e.content.decode()}")
            return None
        except Exception as e:
            self.logger.error(f"Error updating values: {str(e)}")
            return None

    def add_video_record(
            self,
            spreadsheet_id: str,
            sheet_name: str,
            video_data: Dict[str, Any]
    ) -> bool:
        """
        Додає запис про завантажене відео до таблиці.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            sheet_name: Назва листа.
            video_data: Словник з даними про відео.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        if not self.service:
            self.logger.error("Google Sheets API service is not initialized")
            return False

        try:
            # Перевірка існування листа та створення/ініціалізація за потреби
            spreadsheet_info = self.get_spreadsheet_info(spreadsheet_id)
            if not spreadsheet_info:
                return False

            sheet_exists = False
            for sheet in spreadsheet_info.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    sheet_exists = True
                    break

            if not sheet_exists:
                self.create_worksheet(spreadsheet_id, sheet_name)

                # Ініціалізація заголовків
                headers = [
                    "Дата завантаження",
                    "Назва відео",
                    "ID відео",
                    "URL відео",
                    "Категорія",
                    "Статус приватності",
                    "Опис",
                    "Теги"
                ]

                self.update_values(
                    spreadsheet_id,
                    f"{sheet_name}!A1:H1",
                    [headers]
                )

            # Підготовка даних про відео
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            video_id = video_data.get('id', '')
            video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ''

            video_row = [
                now,
                video_data.get('title', ''),
                video_id,
                video_url,
                video_data.get('category', ''),
                video_data.get('privacy_status', ''),
                video_data.get('description', ''),
                ", ".join(video_data.get('tags', []))
            ]

            # Додавання запису
            result = self.append_rows(
                spreadsheet_id,
                f"{sheet_name}!A:H",
                [video_row]
            )

            return result is not None
        except Exception as e:
            self.logger.error(f"Error adding video record: {str(e)}")
            return False

    def to_dataframe(self, spreadsheet_id: str, range_name: str) -> Optional[pd.DataFrame]:
        """
        Отримує дані з таблиці у вигляді pandas DataFrame.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            range_name: Діапазон для отримання.

        Returns:
            pandas DataFrame або None у разі помилки.
        """
        values = self.get_values(spreadsheet_id, range_name)
        if not values:
            return None

        try:
            if len(values) > 0:
                headers = values[0]
                data = values[1:] if len(values) > 1 else []

                # Заповнення коротких рядків None, щоб відповідали довжині заголовків
                for row in data:
                    while len(row) < len(headers):
                        row.append(None)

                df = pd.DataFrame(data, columns=headers)
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error converting to DataFrame: {str(e)}")
            return None

    def from_dataframe(
            self,
            spreadsheet_id: str,
            range_name: str,
            df: pd.DataFrame,
            include_headers: bool = True
    ) -> bool:
        """
        Записує pandas DataFrame у таблицю Google Sheets.

        Args:
            spreadsheet_id: ID таблиці Google Sheets.
            range_name: Діапазон для запису.
            df: DataFrame для запису.
            include_headers: Чи включати заголовки стовпців.

        Returns:
            True у разі успіху, False у разі помилки.
        """
        try:
            values = []

            # Додавання заголовків
            if include_headers:
                values.append(df.columns.tolist())

            # Додавання даних
            for _, row in df.iterrows():
                values.append(row.tolist())

            result = self.update_values(spreadsheet_id, range_name, values)
            return result is not None
        except Exception as e:
            self.logger.error(f"Error writing DataFrame to sheet: {str(e)}")
            return False
# core/youtube_api.py

"""
Модуль для взаємодії з YouTube Data API v3.
Забезпечує функціональність для завантаження відео, керування метаданими та отримання статистики.
"""

import os
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable

import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


class YouTubeAPI:
    """
    Клас для взаємодії з YouTube Data API v3.

    Надає методи для завантаження відео, оновлення метаданих,
    отримання інформації про відео та керування списками відтворення.
    """

    def __init__(self, service=None):
        """
        Ініціалізує об'єкт для роботи з YouTube API.

        Args:
            service: Об'єкт сервісу YouTube API, якщо вже створений.
        """
        self.service = service
        self.logger = logging.getLogger(__name__)

    def set_service(self, service):
        """
        Встановлює сервіс YouTube API.

        Args:
            service: Об'єкт сервісу YouTube API.
        """
        self.service = service
        self.logger.info("YouTube API service has been set")

    async def upload_video(
            self,
            file_path: str,
            title: str,
            description: str = "",
            tags: List[str] = None,
            category_id: str = "22",  # "22" - People & Blogs
            privacy_status: str = "private",
            notify_subscribers: bool = False,
            progress_callback: Callable[[int], None] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Асинхронно завантажує відео на YouTube.

        Args:
            file_path: Шлях до відеофайлу.
            title: Назва відео.
            description: Опис відео.
            tags: Список тегів.
            category_id: ID категорії відео.
            privacy_status: Налаштування приватності ('public', 'private', 'unlisted').
            notify_subscribers: Чи повідомляти підписників про завантаження.
            progress_callback: Функція зворотного виклику для відстеження прогресу.

        Returns:
            Словник з інформацією про завантажене відео або None у разі помилки.
        """
        if not self.service:
            self.logger.error("YouTube API service is not initialized")
            return None

        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        # Для PyQt використовуйте QThreadPool або QConcurrent
        # Тут ми просто імітуємо асинхронність

        # Перетворення приватності до формату API
        privacy_mapping = {
            "Публічне": "public",
            "Приватне": "private",
            "Непублічне": "unlisted",
            "public": "public",
            "private": "private",
            "unlisted": "unlisted"
        }

        privacy = privacy_mapping.get(privacy_status, "private")

        # Підготовка метаданих відео
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }

        try:
            # Створення об'єкта медіа для завантаження
            media = MediaFileUpload(
                file_path,
                resumable=True,
                chunksize=1024 * 1024
            )

            # Створення запиту на вставку
            insert_request = self.service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media,
                notifySubscribers=notify_subscribers
            )

            # Виконання завантаження з оновленням прогресу
            response = None
            last_progress = 0

            while response is None:
                # Імітація асинхронності - в реальному додатку використовуйте asyncio або QThreadPool
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress != last_progress:
                        last_progress = progress
                        self.logger.info(f"Upload progress: {progress}%")
                        if progress_callback:
                            progress_callback(progress)

                # Пауза для імітації асинхронності
                await asyncio.sleep(0.1)

            # Завантаження завершено
            self.logger.info(f"Video upload complete: {response['id']}")

            if progress_callback:
                progress_callback(100)

            return response


        except HttpError as e:

            self.logger.error(f"YouTube API HTTP error: {e.content.decode()}")

            return None

        except Exception as e:

            self.logger.error(f"Error uploading video: {str(e)}")

            return None

    def update_video(

            self,

            video_id: str,

            title: Optional[str] = None,

            description: Optional[str] = None,

            tags: Optional[List[str]] = None,

            category_id: Optional[str] = None,

            privacy_status: Optional[str] = None

    ) -> Optional[Dict[str, Any]]:

        """

        Оновлює метадані вже завантаженого відео.


        Args:

            video_id: Ідентифікатор відео на YouTube.

            title: Нова назва відео.

            description: Новий опис відео.

            tags: Новий список тегів.

            category_id: Нова категорія відео.

            privacy_status: Нові налаштування приватності.


        Returns:

            Словник з оновленою інформацією про відео або None у разі помилки.

        """

        if not self.service:
            self.logger.error("YouTube API service is not initialized")

            return None

        # Отримання поточних даних відео

        try:

            videos_response = self.service.videos().list(

                part="snippet,status",

                id=video_id

            ).execute()

            if not videos_response.get("items"):
                self.logger.error(f"Video not found: {video_id}")

                return None

            # Отримання поточних метаданих

            video = videos_response["items"][0]

            snippet = video.get("snippet", {})

            status = video.get("status", {})

            # Підготовка оновлених метаданих

            body = {

                'id': video_id,

                'snippet': {

                    'title': title if title is not None else snippet.get("title", ""),

                    'description': description if description is not None else snippet.get("description", ""),

                    'tags': tags if tags is not None else snippet.get("tags", []),

                    'categoryId': category_id if category_id is not None else snippet.get("categoryId", "22")

                },

                'status': {

                    'privacyStatus': privacy_status if privacy_status is not None else status.get("privacyStatus",
                                                                                                  "private")

                }

            }

            # Оновлення метаданих

            update_response = self.service.videos().update(

                part="snippet,status",

                body=body

            ).execute()

            self.logger.info(f"Video {video_id} updated successfully")

            return update_response


        except HttpError as e:

            self.logger.error(f"YouTube API HTTP error: {e.content.decode()}")

            return None

        except Exception as e:

            self.logger.error(f"Error updating video: {str(e)}")

            return None

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:

        """

        Встановлює мініатюру для відео.


        Args:

            video_id: Ідентифікатор відео на YouTube.

            thumbnail_path: Шлях до файлу мініатюри.


        Returns:

            True у разі успіху, False у разі помилки.

        """

        if not self.service:
            self.logger.error("YouTube API service is not initialized")

            return False

        if not os.path.exists(thumbnail_path):
            self.logger.error(f"Thumbnail file not found: {thumbnail_path}")

            return False

        try:

            # Завантаження мініатюри

            self.service.thumbnails().set(

                videoId=video_id,

                media_body=MediaFileUpload(thumbnail_path)

            ).execute()

            self.logger.info(f"Thumbnail set for video {video_id}")

            return True

        except HttpError as e:

            self.logger.error(f"YouTube API HTTP error: {e.content.decode()}")

            return False

        except Exception as e:

            self.logger.error(f"Error setting thumbnail: {str(e)}")

            return False

    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:

        """

        Отримує інформацію про відео.


        Args:

            video_id: Ідентифікатор відео на YouTube.


        Returns:

            Словник з інформацією про відео або None у разі помилки.

        """

        if not self.service:
            self.logger.error("YouTube API service is not initialized")

            return None

        try:

            response = self.service.videos().list(

                part="snippet,contentDetails,statistics,status",

                id=video_id

            ).execute()

            if not response.get("items"):
                self.logger.error(f"Video not found: {video_id}")

                return None

            return response["items"][0]

        except HttpError as e:

            self.logger.error(f"YouTube API HTTP error: {e.content.decode()}")

            return None

        except Exception as e:

            self.logger.error(f"Error getting video info: {str(e)}")

            return None

    def get_channel_videos(self, max_results: int = 50) -> Optional[List[Dict[str, Any]]]:

        """

        Отримує список відео поточного каналу.


        Args:

            max_results: Максимальна кількість результатів.


        Returns:

            Список словників з інформацією про відео або None у разі помилки.

        """

        if not self.service:
            self.logger.error("YouTube API service is not initialized")

            return None

        try:

            # Отримання ID поточного каналу

            channels_response = self.service.channels().list(

                part="contentDetails",

                mine=True

            ).execute()

            if not channels_response.get("items"):
                self.logger.error("Cannot get channel information")

                return None

            # Отримання ID плейлиста завантажень

            uploads_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

            # Отримання відео з плейлиста

            playlist_items = []

            next_page_token = None

            while True:

                playlist_response = self.service.playlistItems().list(

                    part="snippet",

                    playlistId=uploads_playlist_id,

                    maxResults=min(max_results - len(playlist_items), 50),

                    pageToken=next_page_token

                ).execute()

                playlist_items.extend(playlist_response["items"])

                next_page_token = playlist_response.get("nextPageToken")

                if not next_page_token or len(playlist_items) >= max_results:
                    break

            return playlist_items

        except HttpError as e:

            self.logger.error(f"YouTube API HTTP error: {e.content.decode()}")

            return None

        except Exception as e:

            self.logger.error(f"Error getting channel videos: {str(e)}")

            return None

    def schedule_video(self, video_id: str, publish_at: str) -> bool:

        """

        Планує публікацію відео на певний час.


        Args:

            video_id: Ідентифікатор відео на YouTube.

            publish_at: Дата та час публікації у форматі ISO 8601 (наприклад, '2023-12-31T12:00:00Z').


        Returns:

            True у разі успіху, False у разі помилки.

        """

        if not self.service:
            self.logger.error("YouTube API service is not initialized")

            return False

        try:

            self.service.videos().update(

                part="status",

                body={

                    "id": video_id,

                    "status": {

                        "privacyStatus": "private",

                        "publishAt": publish_at

                    }

                }

            ).execute()

            self.logger.info(f"Video {video_id} scheduled for {publish_at}")

            return True

        except HttpError as e:

            self.logger.error(f"YouTube API HTTP error: {e.content.decode()}")

            return False

        except Exception as e:

            self.logger.error(f"Error scheduling video: {str(e)}")

            return False
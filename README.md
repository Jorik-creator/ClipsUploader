# 📺 YouTube Uploader з інтеграцією Google Sheets

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?cacheSeconds=2592000)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.13-green.svg)

</div>

<p align="center">
  <img src="https://i.imgur.com/example.png" alt="YouTube Uploader Screenshot" width="600"/>
</p>

> Десктопний додаток на Python для автоматизації процесу завантаження відеоконтенту на платформу YouTube з подальшим записом метаданих про завантаження у таблиці Google Sheets.

## ✨ Функціональні можливості

- 🔐 Автентифікація через Google OAuth 2.0
- 🎥 Завантаження відео на YouTube з усіма метаданими
- 📊 Автоматичне створення та оновлення таблиць Google Sheets
- ⏰ Планування часу публікації відео
- 👥 Керування кількома обліковими записами Google
- 📋 Налаштування шаблонів метаданих
- 🌓 Підтримка темної/світлої теми інтерфейсу

## 🛠️ Технічний стек

- 🐍 Python 3.13
- 🖥️ PyQt6 для графічного інтерфейсу
- 🔌 Google API клієнтські бібліотеки (YouTube API v3, Google Sheets API v4)
- 🔑 OAuth 2.0 для безпечної автентифікації
- 📈 pandas для структурованої роботи з даними

## 📥 Встановлення

### Передумови

- Python 3.13 або вище
- pip (менеджер пакетів Python)
- Доступ до Інтернету для взаємодії з API Google

### Метод 1: Встановлення з GitHub

```bash
# Клонуйте репозиторій
git clone https://github.com/yourusername/youtube-uploader-sheets.git
cd youtube-uploader-sheets

# Створіть віртуальне середовище
python -m venv venv

# Активуйте віртуальне середовище
# Для Windows:
venv\Scripts\activate
# Для macOS/Linux:
source venv/bin/activate

# Встановіть залежності
pip install -r requirements.txt
```

### Метод 2: Використання виконуваного файлу

Для Windows, macOS та Linux доступні готові виконувані файли у розділі [Releases](https://github.com/yourusername/youtube-uploader-sheets/releases).

## 🔐 Налаштування Google API

<details>
<summary>Розгорнути детальну інструкцію</summary>

Перед використанням додатку необхідно отримати облікові дані OAuth для доступу до API Google:

1. Створіть проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Увімкніть YouTube Data API v3 та Google Sheets API v4
3. Налаштуйте екран згоди OAuth
4. Створіть облікові дані OAuth для десктопного додатку
5. Завантажте JSON файл з обліковими даними OAuth

### Покрокові інструкції:

1. Відвідайте [Google Cloud Console](https://console.cloud.google.com/)
2. Натисніть "Створити проект", введіть назву, натисніть "Створити"
3. У меню ліворуч виберіть "API і сервіси" > "Бібліотека"
4. Знайдіть і активуйте "YouTube Data API v3" та "Google Sheets API v4"
5. Налаштуйте екран згоди OAuth: меню ліворуч > "API і сервіси" > "Екран згоди OAuth"
6. Виберіть тип "Зовнішній" і заповніть обов'язкові поля
7. Додайте області доступу:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`
   - `https://www.googleapis.com/auth/spreadsheets`
8. Створіть облікові дані: меню ліворуч > "API і сервіси" > "Облікові дані"
9. Натисніть "Створити облікові дані" > "ID клієнта OAuth"
10. Виберіть тип "Десктопний додаток", введіть назву
11. Завантажте JSON-файл і перейменуйте його на `client_secret.json`
12. Помістіть цей файл у папку `config/` додатку

</details>

## 🚀 Запуск додатку

```bash
# З активованим віртуальним середовищем
python main.py
```

Або запустіть виконуваний файл, якщо ви використовуєте готовий дистрибутив.

## 📋 Використання

<div align="center">

| Крок | Опис |
|------|------|
| **1. Перший запуск** | При першому запуску програма створить необхідні папки та файли налаштувань |
| **2. Автентифікація** | Натисніть кнопку "Увійти" та авторизуйтеся через браузер у своєму обліковому записі Google |
| **3. Завантаження відео** | Виберіть файл, заповніть метадані, налаштуйте параметри та натисніть "Завантажити на YouTube" |
| **4. Інтеграція з Sheets** | Після успішного завантаження додаток автоматично додасть запис до вказаної таблиці |

</div>

### Детальніше про завантаження відео:
- Виберіть відеофайл
- Заповніть метадані (назва, опис, теги, категорія тощо)
- Виберіть налаштування приватності
- Опціонально додайте мініатюру
- За потреби вкажіть час запланованої публікації
- Натисніть "Завантажити на YouTube"

## 📂 Структура проекту

```
youtube-uploader-sheets/
├── config/                 # Конфігураційні файли
│   ├── __init__.py
│   ├── settings.py         # Налаштування додатку
│   └── client_secret.json  # Облікові дані OAuth (потрібно додати)
├── core/                   # Основна бізнес-логіка
│   ├── __init__.py
│   ├── auth.py             # Автентифікація з Google API
│   ├── youtube_api.py      # Взаємодія з YouTube API
│   └── sheets_api.py       # Взаємодія з Google Sheets API
├── gui/                    # Графічний інтерфейс
│   ├── __init__.py
│   ├── main_window.py      # Головне вікно програми
│   ├── auth_widget.py      # Віджет автентифікації
│   ├── upload_widget.py    # Віджет завантаження відео
│   └── settings_widget.py  # Віджет налаштувань
├── utils/                  # Утиліти
│   ├── __init__.py
│   ├── logger.py           # Налаштування логування
│   └── file_manager.py     # Робота з файлами
├── .tokens/                # Директорія для зберігання токенів (створюється автоматично)
├── logs/                   # Директорія для логів (створюється автоматично)
├── temp/                   # Директорія для тимчасових файлів (створюється автоматично)
├── main.py                 # Точка входу в програму
├── requirements.txt        # Залежності проекту
└── README.md               # Цей файл
```

## 🔨 Збірка виконуваного файлу

Для створення автономного виконуваного файлу використовується PyInstaller:

```bash
# З активованим віртуальним середовищем
pip install pyinstaller
pyinstaller --onefile --windowed --icon=resources/icon.ico main.py
```

Виконуваний файл буде створено в папці `dist/`.

## ❓ Вирішення проблем

<details>
<summary><b>🔐 Проблеми з автентифікацією</b></summary>

1. Переконайтеся, що файл `client_secret.json` розміщено у папці `config/`
2. Перевірте, чи активовані необхідні API в консолі Google Cloud
3. Перевірте, чи додано всі необхідні області доступу в екрані згоди OAuth
4. Спробуйте видалити папку `.tokens/` і повторити авторизацію
</details>

<details>
<summary><b>🎥 Помилки завантаження відео</b></summary>

1. Перевірте підключення до Інтернету
2. Переконайтеся, що файл відео відповідає підтримуваним форматам (MP4, AVI, MOV тощо)
3. Перевірте, чи не перевищує розмір файлу ліміт YouTube (зазвичай 128 ГБ)
4. Перевірте логи в папці `logs/` для більш детальної інформації про помилку
</details>

## 📜 Ліцензія

Цей проект розповсюджується під ліцензією MIT. Детальніше дивіться у файлі [LICENSE](LICENSE).

## 👨‍💻 Автори

- Ваше ім'я - [GitHub](https://github.com/yourusername)

## 🙏 Подяки

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/download) - за потужний фреймворк для створення GUI
- [Google API Python Client](https://github.com/googleapis/google-api-python-client) - за інструменти для роботи з API Google

---

<div align="center">
  <p>🌟 Не забудьте поставити зірочку на GitHub, якщо вам сподобався цей проект! 🌟</p>
</div>

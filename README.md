# Приложение для анализа банковских транзакций

Приложение читает Excel-файл с транзакциями и генерирует JSON-ответы для веб-страниц, а также предоставляет сервисы и отчёты.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Anna-eliza/coursework_1.git
   cd coursework_1
   ```

2. Установите зависимости:

   ```bash
   poetry install
   ```

3. Создайте файл `.env` на основе `.env_template` и добавьте API-ключ Finnhub:

   ```
   FINNHUB_API_KEY=ваш_ключ
   ```

## Запуск

```bash
poetry run python -m src.main
```

## Структура проекта

- `src/utils.py` — чтение Excel, работа с датами.
- `src/views.py` — генерация JSON для веб-страниц («Главная», «События»).
- `src/services.py` — сервисы (кешбэк, поиск).
- `src/reports.py` — отчёты и декоратор записи в файл.
- `src/main.py` — точка входа, демонстрация.
- `tests/` — тесты (pytest).
- `data/operations.xlsx` — исходные данные.
- `user_settings.json` — настройки валют и акций.

## Тесты

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

Покрытие: **95%**.

## Технологии

- Python 3.14
- pandas, openpyxl — работа с Excel.
- requests — API валют.
- finnhub-python — API акций.
- python-dotenv — хранение ключей.
- pytest, pytest-cov — тестирование.
- Poetry — управление зависимостями.
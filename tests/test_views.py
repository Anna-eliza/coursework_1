import pytest
from datetime import datetime
import json

from src.reports import report_to_file
from src.views import main_page, aggregate_expenses, aggregate_income, events_page
from src.views import get_greeting, get_cards_info, get_top_transactions, get_stock_prices
from unittest.mock import patch, MagicMock

from src.views import get_currency_rates


@pytest.mark.parametrize(
    "hour, expected",
    [
        (6, "Доброе утро"),       # нижняя граница
        (8, "Доброе утро"),
        (11, "Доброе утро"),
        (12, "Добрый день"),      # граница
        (15, "Добрый день"),
        (17, "Добрый день"),
        (18, "Добрый вечер"),     # граница
        (22, "Добрый вечер"),
        (23, "Доброй ночи"),      # граница
        (0, "Доброй ночи"),
        (3, "Доброй ночи"),
        (5, "Доброй ночи"),       # граница
    ],
)
def test_get_greeting(hour, expected):
    dt = datetime(2021, 12, 20, hour, 0, 0)
    assert get_greeting(dt) == expected


def test_get_cards_info():
    """Проверяет расчёт расходов и кешбэка по картам."""
    transactions = [
        {"Номер карты": "*1234", "Сумма операции": -1500.0},  # расход
        {"Номер карты": "*1234", "Сумма операции": -500.0},  # расход
        {"Номер карты": "*1234", "Сумма операции": 1000.0},  # поступление (пропустить)
        {"Номер карты": "*5678", "Сумма операции": -200.0},  # расход
        {"Номер карты": None, "Сумма операции": -300.0},  # нет карты (пропустить)
    ]

    result = get_cards_info(transactions)

    assert len(result) == 2

    card_1234 = next(c for c in result if c["last_digits"] == "1234")
    assert card_1234["total_spent"] == 2000.0
    assert card_1234["cashback"] == 20.0

    card_5678 = next(c for c in result if c["last_digits"] == "5678")
    assert card_5678["total_spent"] == 200.0
    assert card_5678["cashback"] == 2.0


def test_get_top_transactions():
    """Проверяет, что возвращаются 5 транзакций, отсортированных по убыванию."""
    transactions = [
        {"Дата операции": datetime(2021, 12, 1), "Сумма платежа": 1000, "Категория": "A", "Описание": "a"},
        {"Дата операции": datetime(2021, 12, 2), "Сумма платежа": 5000, "Категория": "B", "Описание": "b"},
        {"Дата операции": datetime(2021, 12, 3), "Сумма платежа": 500, "Категория": "C", "Описание": "c"},
        {"Дата операции": datetime(2021, 12, 4), "Сумма платежа": 3000, "Категория": "D", "Описание": "d"},
        {"Дата операции": datetime(2021, 12, 5), "Сумма платежа": 2000, "Категория": "E", "Описание": "e"},
        {"Дата операции": datetime(2021, 12, 6), "Сумма платежа": 100, "Категория": "F", "Описание": "f"},
    ]

    result = get_top_transactions(transactions)

    assert len(result) == 5
    assert [t["amount"] for t in result] == [5000, 3000, 2000, 1000, 500]
    assert result[0]["date"] == "02.12.2021"
    assert set(result[0].keys()) == {"date", "amount", "category", "description"}


@patch("src.views.requests.get")
def test_get_currency_rates(mock_get):
    """Проверяет получение курсов валют с моком API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": "success",
        "rates": {
            "USD": 0.0125,   # 1 / 80
            "EUR": 0.0111,   # ~1 / 90
        },
    }
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD", "EUR"])

    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 80.0
    assert result[1]["currency"] == "EUR"

@patch("src.views.finnhub.Client")
def test_get_stock_prices(mock_client):
    """Проверяет получение цен акций с моком клиента Finnhub."""
    mock_instance = MagicMock()
    mock_instance.quote.return_value = {"c": 150.5}
    mock_client.return_value = mock_instance

    result = get_stock_prices(["AAPL"])

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.5


def test_main_page_structure():
    """Проверяет, что main_page возвращает JSON с нужными ключами."""
    result = main_page("2021-12-20 14:30:00")
    data = json.loads(result)

    assert "greeting" in data
    assert "cards" in data
    assert "top_transactions" in data
    assert "currency_rates" in data
    assert "stock_prices" in data
    assert data["greeting"] == "Добрый день"
    assert isinstance(data["cards"], list)
    assert isinstance(data["top_transactions"], list)


def test_aggregate_expenses():
    """Проверяет группировку расходов, топ-7 и переводы."""
    filtered = [
        {"Сумма операции": -1000, "Категория": "Супермаркеты"},
        {"Сумма операции": -500, "Категория": "Супермаркеты"},
        {"Сумма операции": -2000, "Категория": "Каршеринг"},
        {"Сумма операции": -3000, "Категория": "Переводы"},
        {"Сумма операции": -1500, "Категория": "Наличные"},
        {"Сумма операции": 5000, "Категория": "Пополнения"},
    ]
    result = aggregate_expenses(filtered)

    assert result["total_amount"] == 8000
    assert {"category": "Переводы", "amount": 3000} in result["transfers_and_cash"]
    assert {"category": "Наличные", "amount": 1500} in result["transfers_and_cash"]
    assert {"category": "Каршеринг", "amount": 2000} in result["main"]
    assert {"category": "Супермаркеты", "amount": 1500} in result["main"]


def test_aggregate_income():
    """Проверяет группировку поступлений."""
    filtered = [
        {"Сумма операции": 5000, "Категория": "Пополнения"},
        {"Сумма операции": 2000, "Категория": "Бонусы"},
        {"Сумма операции": -1000, "Категория": "Супермаркеты"},  # расход
    ]
    result = aggregate_income(filtered)

    assert result["total_amount"] == 7000
    assert result["main"] == [
        {"category": "Пополнения", "amount": 5000},
        {"category": "Бонусы", "amount": 2000},
    ]


def test_events_page_structure():
    """Проверяет структуру JSON-ответа events_page."""
    result = events_page("2021-12-20 14:30:00", "M")
    data = json.loads(result)

    assert "expenses" in data
    assert "income" in data
    assert "currency_rates" in data
    assert "stock_prices" in data
    assert "total_amount" in data["expenses"]
    assert "main" in data["expenses"]
    assert "transfers_and_cash" in data["expenses"]
    assert isinstance(data["expenses"]["main"], list)


def test_report_to_file_default_name(tmp_path, monkeypatch):
    """Проверяет, что декоратор без параметра создаёт файл с автоименем."""
    monkeypatch.chdir(tmp_path)

    @report_to_file()
    def sample():
        return {"test": True}

    sample()
    files = list(tmp_path.glob("report_*.json"))
    assert len(files) == 1
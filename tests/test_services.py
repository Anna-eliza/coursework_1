import json
from datetime import datetime

from src.services import cashback_categories, simple_search


def test_cashback_categories():
    """Проверяет расчёт кешбэка по категориям за месяц."""
    transactions = [
        {
            "Дата операции": datetime(2021, 12, 5),
            "Сумма операции": -1000,
            "Категория": "Супермаркеты",
        },
        {
            "Дата операции": datetime(2021, 12, 10),
            "Сумма операции": -500,
            "Категория": "Супермаркеты",
        },
        {
            "Дата операции": datetime(2021, 12, 15),
            "Сумма операции": -2000,
            "Категория": "Каршеринг",
        },
        {
            "Дата операции": datetime(2021, 11, 20),
            "Сумма операции": -3000,
            "Категория": "Аптеки",
        },  # другой месяц
        {
            "Дата операции": datetime(2021, 12, 1),
            "Сумма операции": 5000,
            "Категория": "Пополнения",
        },  # поступление
    ]

    result = json.loads(cashback_categories(transactions, 2021, 12))

    assert result == {
        "Каршеринг": 20.0,
        "Супермаркеты": 15.0,
    }


def test_simple_search():
    """Проверяет поиск по подстроке (регистронезависимый)."""
    transactions = [
        {
            "Дата операции": datetime(2021, 12, 1),
            "Сумма операции": -100,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
        },
        {
            "Дата операции": datetime(2021, 12, 2),
            "Сумма операции": -200,
            "Категория": "Каршеринг",
            "Описание": "Ситидрайв",
        },
        {
            "Дата операции": datetime(2021, 12, 3),
            "Сумма операции": -300,
            "Категория": "Супермаркеты",
            "Описание": "Пятёрочка",
        },
    ]

    result = json.loads(simple_search(transactions, "супермаркеты"))
    assert len(result) == 2

    result = json.loads(simple_search(transactions, "МАГНИТ"))
    assert len(result) == 1

    result = json.loads(simple_search(transactions, "аптека"))
    assert result == []

from datetime import datetime

import pytest

from src.utils import (BASE_DIR, filter_by_date, get_date_range, parse_date,
                       read_transactions_from_excel)


def test_parse_date_ok():
    """Проверяет, что дата парсится в объект datetime."""
    result = parse_date("2021-12-20 14:30:00")
    assert isinstance(result, datetime)
    assert result == datetime(2021, 12, 20, 14, 30, 0)


def test_parse_date_wrong_format():
    """Проверяет, что при неверном формате падает ValueError."""
    with pytest.raises(ValueError):
        parse_date("20.12.2021 14:30:00")


def test_get_date_range_month():
    """M: начало месяца — сама дата."""
    start, end = get_date_range("2021-12-20 14:30:00", "M")
    assert start == datetime(2021, 12, 1)
    assert end == datetime(2021, 12, 20, 14, 30, 0)


def test_get_date_range_week():
    """W: понедельник недели — сама дата."""
    start, end = get_date_range("2021-12-20 14:30:00", "W")
    assert start == datetime(2021, 12, 20)  # 20.12.2021 — понедельник
    assert end == datetime(2021, 12, 20, 14, 30, 0)


def test_get_date_range_year():
    """Y: начало года — сама дата."""
    start, end = get_date_range("2021-12-20 14:30:00", "Y")
    assert start == datetime(2021, 1, 1)
    assert end == datetime(2021, 12, 20, 14, 30, 0)


def test_get_date_range_all():
    """ALL: очень старая дата — сама дата."""
    start, end = get_date_range("2021-12-20 14:30:00", "ALL")
    assert start == datetime(1900, 1, 1)
    assert end == datetime(2021, 12, 20, 14, 30, 0)


def test_get_date_range_invalid_period():
    """Неизвестный период → ValueError."""
    with pytest.raises(ValueError):
        get_date_range("2021-12-20 14:30:00", "X")


def test_read_transactions_from_excel():
    """Проверяет, что функция читает Excel и фильтрует FAILED."""
    transactions = read_transactions_from_excel(BASE_DIR / "data" / "operations.xlsx")

    assert isinstance(transactions, list)
    assert len(transactions) > 0

    for t in transactions:
        assert t["Статус"] == "OK"

    assert isinstance(transactions[0]["Дата операции"], datetime)

    assert all(t["Кэшбэк"] is not None for t in transactions)
    assert all(t["Категория"] is not None for t in transactions)


def test_filter_by_date():
    """Проверяет фильтрацию по дате."""
    transactions = [
        {"Дата операции": datetime(2021, 12, 1), "Сумма операции": -100},
        {"Дата операции": datetime(2021, 12, 10), "Сумма операции": -200},
        {"Дата операции": datetime(2021, 12, 20), "Сумма операции": -300},
        {"Дата операции": datetime(2022, 1, 5), "Сумма операции": -400},
    ]

    start = datetime(2021, 12, 5)
    end = datetime(2021, 12, 20)

    result = filter_by_date(transactions, start, end)

    assert len(result) == 2
    assert result[0]["Сумма операции"] == -200
    assert result[1]["Сумма операции"] == -300

import json
import os
from datetime import datetime

import finnhub
import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import (BASE_DIR, filter_by_date, get_date_range, parse_date,
                       read_transactions_from_excel)

load_dotenv()


def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие в зависимости от часа."""
    hour = dt.hour

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_cards_info(transactions: list[dict]) -> list[dict]:
    """
    Возвращает информацию по каждой карте: сумму расходов, маску карты, кешбэк
    """
    cards = {}
    for t in transactions:
        card = t["Номер карты"]
        amount = t["Сумма операции"]

        if pd.isna(card):
            continue

        if amount >= 0:
            continue

        last_digits = card[-4:]

        if last_digits not in cards:
            cards[last_digits] = {"total_spent": 0.0}

        cards[last_digits]["total_spent"] += abs(amount)

    return [
        {
            "last_digits": digits,
            "total_spent": round(data["total_spent"], 2),
            "cashback": round(data["total_spent"] / 100, 2),
        }
        for digits, data in cards.items()
    ]


def get_top_transactions(transactions: list[dict], limit: int = 5) -> list[dict]:
    """Возвращает топ N транзакций по сумме платежа"""
    top = sorted(transactions, key=lambda t: t["Сумма платежа"], reverse=True)[:limit]

    return [
        {
            "date": t["Дата операции"].strftime("%d.%m.%Y"),
            "amount": t["Сумма платежа"],
            "category": t["Категория"],
            "description": t["Описание"],
        }
        for t in top
    ]


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Возвращает курс валют к рублю."""
    url = "https://open.er-api.com/v6/latest/RUB"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return []

        rates = data["rates"]
        return [
            {"currency": cur, "rate": round(1 / rates[cur], 2)} for cur in currencies
        ]
    except (requests.RequestException, KeyError, ZeroDivisionError):
        return []


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Возвращает стоимость акций из S&P500."""
    api_key = os.environ.get("FINNHUB_API_KEY")

    if not api_key:
        print("FINNHUB_API_KEY не найден в .env")
        return []

    client = finnhub.Client(api_key=api_key)

    try:
        result = []
        for symbol in stocks:
            quote = client.quote(symbol)
            price = quote["c"]  # c = current price
            if price and price > 0:
                result.append({"stock": symbol, "price": round(price, 2)})
        return result
    except Exception as e:
        print(f"Ошибка получения котировок: {e}")
        return []


def main_page(date_str: str) -> str:
    """Возвращает JSON для главной страницы."""
    dt = parse_date(date_str)
    transactions = read_transactions_from_excel(BASE_DIR / "data" / "operations.xlsx")
    start, end = get_date_range(date_str, "M")
    filtered = filter_by_date(transactions, start, end)

    with open(BASE_DIR / "user_settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    result = {
        "greeting": get_greeting(dt),
        "cards": get_cards_info(filtered),
        "top_transactions": get_top_transactions(filtered),
        "currency_rates": get_currency_rates(settings["user_currencies"]),
        "stock_prices": get_stock_prices(settings["user_stocks"]),
    }

    return json.dumps(result, ensure_ascii=False, indent=2)


def aggregate_expenses(filtered: list[dict]) -> dict:
    """Формирует блок 'expenses' для страницы событий."""
    expenses = [t for t in filtered if t["Сумма операции"] < 0]

    total_amount = round(sum(abs(t["Сумма операции"]) for t in expenses))

    by_category = {}
    for t in expenses:
        cat = t["Категория"]
        amount = abs(t["Сумма операции"])
        by_category[cat] = by_category.get(cat, 0) + amount

    transfers_and_cash = {}
    main = {}
    for cat, amount in by_category.items():
        if cat in ("Наличные", "Переводы"):
            transfers_and_cash[cat] = round(amount)
        else:
            main[cat] = round(amount)

    sorted_main = sorted(main.items(), key=lambda x: x[1], reverse=True)
    top7 = sorted_main[:7]
    rest_sum = sum(amount for _, amount in sorted_main[7:])

    main_list = [{"category": cat, "amount": amt} for cat, amt in top7]
    if rest_sum > 0:
        main_list.append({"category": "Остальное", "amount": rest_sum})

    transfers_list = [
        {"category": cat, "amount": amt}
        for cat, amt in sorted(
            transfers_and_cash.items(), key=lambda x: x[1], reverse=True
        )
    ]

    return {
        "total_amount": total_amount,
        "main": main_list,
        "transfers_and_cash": transfers_list,
    }


def aggregate_income(filtered: list[dict]) -> dict:
    """Формирует блок 'income' для страницы событий."""
    income = [t for t in filtered if t["Сумма операции"] > 0]

    total_amount = round(sum(t["Сумма операции"] for t in income))

    by_category = {}
    for t in income:
        cat = t["Категория"]
        amount = t["Сумма операции"]
        by_category[cat] = by_category.get(cat, 0) + amount

    sorted_income = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_amount": total_amount,
        "main": [{"category": cat, "amount": round(amt)} for cat, amt in sorted_income],
    }


def events_page(date_str: str, period: str = "M") -> str:
    """Возвращает JSON для страницы «События»."""
    transactions = read_transactions_from_excel(BASE_DIR / "data" / "operations.xlsx")

    date_from, date_to = get_date_range(date_str, period)
    filtered = filter_by_date(transactions, date_from, date_to)

    with open(BASE_DIR / "user_settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    result = {
        "expenses": aggregate_expenses(filtered),
        "income": aggregate_income(filtered),
        "currency_rates": get_currency_rates(settings["user_currencies"]),
        "stock_prices": get_stock_prices(settings["user_stocks"]),
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

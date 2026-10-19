import json
from src.utils import BASE_DIR, read_transactions_from_excel


def filter_by_month(transactions: list[dict], year: int, month: int) -> list[dict]:
    """Оставляет транзакции за указанный месяц и год."""
    return [
        t for t in transactions
        if t["Дата операции"].year == year and t["Дата операции"].month == month
    ]


def cashback_categories(data: list[dict], year: int, month: int) -> str:
    """Анализ выгодности категорий кешбэка за указанный месяц."""
    filtered = filter_by_month(data, year, month)

    expenses_by_category = {}
    for t in filtered:
        if t["Сумма операции"] < 0:
            category = t["Категория"]
            amount = abs(t["Сумма операции"])
            expenses_by_category[category] = expenses_by_category.get(category, 0) + amount

    cashback_by_category = {
        category: round(amount / 100, 2)
        for category, amount in expenses_by_category.items()
    }
    sorted_cashback = dict(
        sorted(cashback_by_category.items(), key=lambda x: x[1], reverse=True)
    )

    return json.dumps(sorted_cashback, ensure_ascii=False, indent=2)


def _serialize_transaction(t: dict) -> dict:
    """Преобразует транзакцию в JSON-совместимый вид."""
    return {
        "date": t["Дата операции"].strftime("%d.%m.%Y %H:%M:%S"),
        "amount": t["Сумма операции"],
        "category": t["Категория"],
        "description": t["Описание"],
    }


def simple_search(transactions: list[dict], query: str) -> str:
    """Ищет транзакции по подстроке в описании или категории."""
    query_lower = query.lower()

    found = [
        t for t in transactions
        if query_lower in t["Описание"].lower()
        or query_lower in t["Категория"].lower()
    ]

    serialized = [_serialize_transaction(t) for t in found]

    return json.dumps(serialized, ensure_ascii=False, indent=2)





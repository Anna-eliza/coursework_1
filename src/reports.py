import functools
import json
from datetime import datetime

import pandas as pd


def report_to_file(filename: str | None = None):
    """Декоратор-фабрика: принимает имя файла или использует автоимя."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            name = (
                filename
                or f"report_{func.__name__}_{datetime.now():%Y%m%d_%H%M%S}.json"
            )
            with open(name, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: str | None = None,
) -> list[dict]:
    """Возвращает траты по категории за последние 3 месяца."""
    if date is None:
        end_date = pd.Timestamp.now()
    else:
        end_date = pd.to_datetime(date)

    start_date = end_date - pd.DateOffset(months=3)

    filtered = transactions[
        (transactions["Категория"] == category)
        & (transactions["Сумма операции"] < 0)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ]

    result = [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": row["Сумма операции"],
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for _, row in filtered.iterrows()
    ]

    return result

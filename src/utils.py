from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def read_transactions_from_excel(file_path):
    """Читает содержимое Exel файла, фильтрует наличие кешбэка и форматирует дату"""
    df = pd.read_excel(file_path)
    df = df[df["Статус"] == "OK"]
    df["Кэшбэк"] = df["Кэшбэк"].fillna(0)
    df["Категория"] = df["Категория"].fillna("Остальное")
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    return df.to_dict(orient="records")


def parse_date(date_str: str) -> datetime:
    """Превращает строку 'YYYY-MM-DD HH:MM:SS' в datetime."""

    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def get_date_range(date_str: str, period: str = "M") -> tuple[datetime, datetime]:
    """Возвращает начало и конец указанного периода"""
    date_to = parse_date(date_str)
    if period == "M":
        date_from = date_to.replace(day=1, hour=0, minute=0, second=0)
    elif period == "W":
        date_from = (date_to - timedelta(days=date_to.weekday())).replace(
            hour=0, minute=0, second=0
        )
    elif period == "Y":
        date_from = date_to.replace(month=1, day=1, hour=0, minute=0, second=0)
    elif period == "ALL":
        date_from = datetime(1900, 1, 1)
    else:
        raise ValueError(f"Неизвестный период: {period}")
    return date_from, date_to


def filter_by_date(
    transactions: list[dict], date_from: datetime, date_to: datetime
) -> list[dict]:
    """Оставляет транзакции, у которых 'Дата операции' в диапазоне [start, end]."""
    return [t for t in transactions if date_from <= t["Дата операции"] <= date_to]

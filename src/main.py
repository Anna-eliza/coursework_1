import json

import pandas as pd

from src.reports import spending_by_category
from src.services import cashback_categories, simple_search
from src.utils import BASE_DIR, filter_by_date, get_date_range, read_transactions_from_excel
from src.views import events_page, main_page


def main() -> None:
    """Демонстрация работы всех функций проекта."""
    date_str = "2021-12-20 14:30:00"

    print("=" * 60)
    print("ГЛАВНАЯ СТРАНИЦА")
    print("=" * 60)
    print(main_page(date_str))

    print("\n" + "=" * 60)
    print("СТРАНИЦА «СОБЫТИЯ»")
    print("=" * 60)
    print(events_page(date_str, "M"))

    print("\n" + "=" * 60)
    print("СЕРВИСЫ")
    print("=" * 60)
    transactions = read_transactions_from_excel(BASE_DIR / "data" / "operations.xlsx")
    date_from, date_to = get_date_range(date_str, "M")
    filtered = filter_by_date(transactions, date_from, date_to)

    print("\nКешбэк по категориям:")
    print(cashback_categories(filtered, 2021, 12))

    print("\nПоиск по запросу 'супермаркеты':")
    result = json.loads(simple_search(filtered, "супермаркеты"))
    print(f"Найдено: {len(result)} транзакций")

    print("\n" + "=" * 60)
    print("ОТЧЁТ: Траты по категории 'Супермаркеты'")
    print("=" * 60)
    df = pd.DataFrame(transactions)
    report = spending_by_category(df, "Супермаркеты", date_str)
    print(f"Найдено: {len(report)} транзакций")
    print(f"Файл отчёта создан в {BASE_DIR}")


if __name__ == "__main__":
    main()
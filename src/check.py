import pandas as pd
from src.utils import read_transactions_from_excel, BASE_DIR
from src.reports import spending_by_category

# ВАЖНО: функция принимает DataFrame, конвертируем список обратно
transactions = read_transactions_from_excel(BASE_DIR / "data" / "operations.xlsx")
df = pd.DataFrame(transactions)

result = spending_by_category(df, "Супермаркеты", "2021-12-20 14:30:00")
print(f"Найдено транзакций: {len(result)}")
for t in result[:5]:
    print(t)

# Проверьте, что создался файл отчёта
from src.views import events_page

result = events_page("2021-12-20 14:30:00", "M")
print(result)
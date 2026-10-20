import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.reports import report_to_file, spending_by_category


def test_report_to_file_with_custom_name(tmp_path):
    """Проверяет, что декоратор с параметром записывает файл с заданным именем."""
    output_file = tmp_path / "test_report.json"

    @report_to_file(str(output_file))
    def sample_report():
        return {"test": "works", "value": 42}

    result = sample_report()

    assert result == {"test": "works", "value": 42}

    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"test": "works", "value": 42}


def test_spending_by_category(tmp_path):
    """Проверяет фильтрацию по категории и дате."""
    data = [
        {
            "Дата операции": pd.Timestamp("2021-12-15"),
            "Сумма операции": -500,
            "Категория": "Супермаркеты",
            "Описание": "Магнит",
        },
        {
            "Дата операции": pd.Timestamp("2021-12-10"),
            "Сумма операции": -300,
            "Категория": "Каршеринг",
            "Описание": "Ситидрайв",
        },
        {
            "Дата операции": pd.Timestamp("2021-08-01"),
            "Сумма операции": -700,
            "Категория": "Супермаркеты",
            "Описание": "Лента",
        },
        {
            "Дата операции": pd.Timestamp("2021-12-05"),
            "Сумма операции": 1000,
            "Категория": "Супермаркеты",
            "Описание": "Возврат",
        },
    ]
    df = pd.DataFrame(data)

    result = spending_by_category(df, "Супермаркеты", "2021-12-20 14:30:00")

    assert len(result) == 1
    assert result[0]["amount"] == -500
    assert result[0]["description"] == "Магнит"

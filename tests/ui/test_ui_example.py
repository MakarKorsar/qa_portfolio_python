# tests/ui/test_ui_example.py
# import pytest

def test_google_title(browser):
    """Проверка заголовка главной страницы Google."""

    # 1. Действие: Открыть страницу
    browser.get("https://www.google.com/")

    # 2. Проверка: Заголовок должен быть "Google"
    assert "Google" in browser.title, "Заголовок страницы не содержит 'Google'"

    print(f"\nТекущий заголовок: {browser.title}")
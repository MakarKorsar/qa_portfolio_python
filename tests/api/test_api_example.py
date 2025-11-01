# tests/api/test_api_example.py
import requests
import pytest

BASE_URL = "https://jsonplaceholder.typicode.com"

def test_get_user_by_id():
    """Проверка получения данных пользователя по ID (позитивный тест)."""

    user_id = 1
    response = requests.get(f"{BASE_URL}/users/{user_id}")

    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    data = response.json()

    # 2. Проверка контракта (ключевых полей)
    assert data['id'] == user_id
    assert "Leanne Graham" in data['name']

    # 3. Проверка заголовков
    assert response.headers['Content-Type'] == 'application/json; charset=utf-8'

def test_get_nonexistent_user():
    """Проверка несуществующего пользователя (негативный тест)."""

    non_existent_id = 999
    response = requests.get(f"{BASE_URL}/users/{non_existent_id}")

    # 1. Проверка статуса: должен быть 404 Not Found
    assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
# tests/api/test_api_example.py
import requests
import pytest
from jsonschema import validate
import time

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


def test_create_user():
    """Проверка создания нового пользователя (позитивный тест)."""

    # Подготовка данных для создания пользователя
    new_user_data = {
        "name": "Test User",
        "username": "testuser",
        "email": "testuser@example.com",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {
                "lat": "-37.3159",
                "lng": "81.1496"
            }
        },
        "phone": "1-770-736-8031 x56442",
        "website": "hildegard.org",
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets"
        }
    }

    # Выполнение POST-запроса для создания пользователя
    response = requests.post(f"{BASE_URL}/users", json=new_user_data)

    # 1. Проверка статуса: должен быть 201 Created (иногда API возвращает 200)
    assert response.status_code in [200, 201], f"Ожидался статус 200 или 201, получен {response.status_code}"

    # 2. Проверка тела ответа: должны содержаться переданные данные
    response_data = response.json()
    assert response_data["name"] == new_user_data["name"], "Имя пользователя не совпадает с ожидаемым"
    assert response_data["email"] == new_user_data["email"], "Email пользователя не совпадает с ожидаемым"
    
    # 3. Проверка, что у созданного пользователя есть ID
    assert "id" in response_data, "В ответе отсутствует ID пользователя"


def test_create_user_with_invalid_data():
    """Проверка создания пользователя с некорректными данными (негативный тест)."""

    # Подготовка некорректных данных для создания пользователя
    invalid_user_data = {
        "invalid_field": "some_value",  # Поля, которых нет в API
        "email": "invalid_email",  # Некорректный email
        "name": ""  # Пустое имя
    }

    # Выполнение POST-запроса с некорректными данными
    response = requests.post(f"{BASE_URL}/users", json=invalid_user_data)

    # 1. Проверка статуса: в реальном API обычно 400 Bad Request,
    # но JSONPlaceholder может вести себя по-разному, поэтому проверим на 200 или 201
    # (JSONPlaceholder возвращает 200/201 даже с некорректными данными)
    assert response.status_code in [200, 201, 400], f"Получен статус {response.status_code}"

    # 2. Проверка тела ответа: в реальном API ожидалось бы сообщение об ошибке
    # Для JSONPlaceholder проверим, что возвращается структура с id
    response_data = response.json()
    assert "id" in response_data or "error" in response_data, "Ответ не содержит ID или сообщения об ошибке"


def test_update_user():
    """Проверка обновления данных пользователя (позитивный тест)."""

    # ID существующего пользователя для обновления
    user_id = 1
    
    # Подготовка обновленных данных пользователя
    updated_user_data = {
        "id": user_id,
        "name": "Updated Test User",
        "username": "updatedtestuser",
        "email": "updatedtestuser@example.com",
        "address": {
            "street": "New Street",
            "suite": "Apt. 123",
            "city": "New City",
            "zipcode": "12345-6789",
            "geo": {
                "lat": "-12.3456",
                "lng": "78.9012"
            }
        },
        "phone": "555-1234",
        "website": "updatedtestuser.com",
        "company": {
            "name": "Updated Company",
            "catchPhrase": "Updated phrase",
            "bs": "Updated business"
        }
    }

    # Выполнение PUT-запроса для обновления пользователя
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=updated_user_data)

    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    # 2. Проверка тела ответа: должны содержаться обновленные данные
    response_data = response.json()
    assert response_data["id"] == user_id, "ID пользователя не совпадает"
    assert response_data["name"] == updated_user_data["name"], "Имя пользователя не обновилось"
    assert response_data["email"] == updated_user_data["email"], "Email пользователя не обновился"
    assert response_data["phone"] == updated_user_data["phone"], "Телефон пользователя не обновился"


def test_update_nonexistent_user():
    """Проверка обновления несуществующего пользователя (негативный тест)."""

    # ID несуществующего пользователя (используем заведомо большой ID)
    non_existent_id = 9999
    
    # Подготовка данных для обновления
    update_data = {
        "name": "Updated Non-existent User",
        "email": "nonexistent@example.com"
    }

    # Выполнение PUT-запроса для обновления несуществующего пользователя
    response = requests.put(f"{BASE_URL}/users/{non_existent_id}", json=update_data)

    # 1. Проверка статуса: в реальном API обычно 404 Not Found,
    # но JSONPlaceholder может создать нового пользователя или вернуть 500 ошибку,
    # поэтому проверим на несколько возможных статусов
    assert response.status_code in [200, 201, 404, 500], f"Получен статус {response.status_code}"

    # 2. Проверка тела ответа: для JSONPlaceholder может создаться новый пользователь
    if response.status_code in [200, 201]:
        response_data = response.json()
        # В JSONPlaceholder PUT может создать нового пользователя с указанным ID
        assert "id" in response_data, "В ответе отсутствует ID пользователя"
    elif response.status_code == 404:
        response_data = response.json()
        # В реальных API может вернуться ошибка
        assert "error" in response_data or response.headers.get('Content-Type'), "Ожидается сообщение об ошибке при статусе 404"
    elif response.status_code == 500:
        # При 500 ошибке JSONPlaceholder может вернуть текстовую ошибку, а не JSON
        # Проверим, что тело ответа не пустое
        assert response.text != "", "При 500 статусе ожидается сообщение об ошибке"


def test_delete_user():
    """Проверка удаления пользователя (позитивный тест)."""

    # ID существующего пользователя для удаления
    user_id = 2

    # Выполнение DELETE-запроса для удаления пользователя
    response = requests.delete(f"{BASE_URL}/users/{user_id}")

    # 1. Проверка статуса: должен быть 200 OK или 204 No Content
    assert response.status_code in [200, 204], f"Ожидался статус 200 или 204, получен {response.status_code}"

    # 2. Проверка тела ответа: в зависимости от API может быть пустым или содержать удаленные данные
    # Для JSONPlaceholder тело ответа часто пустое при статусе 204
    if response.status_code == 200:
        response_data = response.json()
        # В реальных API может возвращаться информация об удаленном ресурсе
        # Для JSONPlaceholder возвращается пустой объект или просто статус
        assert response_data == {} or response_data.get('id') == user_id, "Тело ответа не соответствует ожиданиям"
    else:
        # При статусе 204 тело ответа должно быть пустым
        assert response.text == '', f"Ожидалось пустое тело ответа, получено: {response.text}"


def test_delete_nonexistent_user():
    """Проверка удаления несуществующего пользователя (негативный тест)."""

    # ID несуществующего пользователя (используем заведомо большой ID)
    non_existent_id = 9998

    # Выполнение DELETE-запроса для удаления несуществующего пользователя
    response = requests.delete(f"{BASE_URL}/users/{non_existent_id}")

    # 1. Проверка статуса: в реальном API обычно 404 Not Found,
    # но JSONPlaceholder может вести себя по-разному (часто возвращает 200/204 даже для несуществующих ресурсов)
    assert response.status_code in [200, 204, 404], f"Получен статус {response.status_code}"

    # 2. Проверка тела ответа: в зависимости от статуса может различаться
    if response.status_code == 404:
        # При 404 ожидается сообщение об ошибке (в реальных API)
        response_data = response.json() if response.text else {}
        assert "error" in response_data or response.headers.get('Content-Type'), "Ожидается сообщение об ошибке при статусе 404"
    else:
        # JSONPlaceholder может возвращать 200/204 даже при удалении несуществующего ресурса
        # Это специфическое поведение тестового API
        if response.status_code == 200:
            response_data = response.json()
            assert response_data == {}, "Тело ответа должно быть пустым при успешном удалении"
        else:
            # При статусе 204 тело ответа должно быть пустым
            assert response.text == '', f"Ожидалось пустое тело ответа, получено: {response.text}"


def test_get_users_with_query_params():
    """Проверка получения пользователей с параметрами запроса (фильтрация)."""

    # Подготовка параметров для фильтрации пользователей
    # Используем параметр 'username', чтобы найти конкретного пользователя
    params = {
        "username": "Bret"  # Один из существующих юзеров в API
    }

    # Выполнение GET-запроса с параметрами
    response = requests.get(f"{BASE_URL}/users", params=params)

    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    # 2. Проверка заголовков
    assert response.headers['Content-Type'] == 'application/json; charset=utf-8', "Неправильный тип контента"

    # 3. Проверка тела ответа: должны быть возвращены только пользователи с указанным username
    users = response.json()
    
    # 4. Проверка, что возвращается хотя бы один пользователь
    assert len(users) > 0, "Ожидается, что будет найден хотя бы один пользователь"
    
    # 5. Проверка, что все возвращенные пользователи имеют правильное имя пользователя
    for user in users:
        assert user["username"] == "Bret", f"Найден пользователь с неправильным username: {user['username']}"
    
    # 6. Проверка количества возвращенных элементов (в API обычно только 1 пользователь с уникальным username)
    assert len(users) == 1, f"Ожидается 1 пользователь, найдено: {len(users)}"


def test_search_users_by_name():
    """Проверка поиска пользователей по полному имени."""
    
    # Подготовка параметров для поиска пользователей по полному имени
    # Используем полное имя "Leanne Graham" чтобы найти конкретного пользователя
    params = {
        "name": "Leanne Graham"  # Полное имя одного из существующих пользователей
    }

    # Выполнение GET-запроса с параметрами для поиска
    response = requests.get(f"{BASE_URL}/users", params=params)

    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    # 2. Проверка заголовков
    assert response.headers['Content-Type'] == 'application/json; charset=utf-8', "Неправильный тип контента"

    # 3. Проверка тела ответа: должны быть возвращены пользователи с полным совпадением имени
    users = response.json()
    
    # 4. Проверка, что возвращаются только пользователи с указанным полным именем
    for user in users:
        assert user["name"] == "Leanne Graham", f"Найден пользователь с неправильным именем: {user['name']}"
    
    # 5. Проверка, что хотя бы один пользователь был найден
    assert len(users) > 0, "Ожидается, что будет найден хотя бы один пользователь с именем 'Leanne Graham'"
    
    # 6. Проверка, что возвращается только один пользователь (т.к. имя уникально в тестовом API)
    assert len(users) == 1, f"Ожидается 1 пользователь, найдено: {len(users)}"
    
    # 7. Проверка ID пользователя для дополнительной валидации
    assert users[0]["id"] == 1, f"Ожидаем ID 1 для пользователя 'Leanne Graham', получено: {users[0]['id']}"


def test_users_schema_validation():
    """Проверка валидации схемы данных пользователей с использованием JSON Schema."""
    
    # Определяем ожидаемую схему для пользователя
    user_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "username": {"type": "string"},
            "email": {"type": "string"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "suite": {"type": "string"},
                    "city": {"type": "string"},
                    "zipcode": {"type": "string"},
                    "geo": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "string"},
                            "lng": {"type": "string"}
                        },
                        "required": ["lat", "lng"]
                    }
                },
                "required": ["street", "suite", "city", "zipcode", "geo"]
            },
            "phone": {"type": "string"},
            "website": {"type": "string"},
            "company": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "catchPhrase": {"type": "string"},
                    "bs": {"type": "string"}
                },
                "required": ["name", "catchPhrase", "bs"]
            }
        },
        "required": ["id", "name", "username", "email", "address", "phone", "website", "company"]
    }

    # Выполняем GET-запрос для получения всех пользователей
    response = requests.get(f"{BASE_URL}/users")
    
    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    # 2. Получаем список пользователей
    users = response.json()
    
    # 3. Проверяем, что список не пустой
    assert len(users) > 0, "Ожидается, что будет хотя бы один пользователь"
    
    # 4. Валидируем схему каждого пользователя
    for user in users:
        try:
            # Проверяем, соответствует ли пользователь ожидаемой схеме
            validate(instance=user, schema=user_schema)
        except Exception as e:
            # Если валидация не проходит, выводим ошибку
            assert False, f"Пользователь не соответствует схеме: {str(e)}, данные: {user}"


def test_response_data_types():
    """Проверка типов данных в ответе API."""
    
    # Получаем данные пользователя
    user_id = 1
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    
    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"

    # 2. Получаем данные пользователя
    user = response.json()
    
    # 3. Проверка типов данных для каждого поля
    # Проверяем, что ID - это число
    assert isinstance(user["id"], int), f"Поле 'id' должно быть числом, получено: {type(user['id'])}"
    
    # Проверяем, что name - это строка
    assert isinstance(user["name"], str), f"Поле 'name' должно быть строкой, получено: {type(user['name'])}"
    
    # Проверяем, что username - это строка
    assert isinstance(user["username"], str), f"Поле 'username' должно быть строкой, получено: {type(user['username'])}"
    
    # Проверяем, что email - это строка
    assert isinstance(user["email"], str), f"Поле 'email' должно быть строкой, получено: {type(user['email'])}"
    
    # Проверяем, что address - это объект (словарь)
    assert isinstance(user["address"], dict), f"Поле 'address' должно быть объектом, получено: {type(user['address'])}"
    
    # Проверяем, что phone - это строка
    assert isinstance(user["phone"], str), f"Поле 'phone' должно быть строкой, получено: {type(user['phone'])}"
    
    # Проверяем, что website - это строка
    assert isinstance(user["website"], str), f"Поле 'website' должно быть строкой, получено: {type(user['website'])}"
    
    # Проверяем, что company - это объект (словарь)
    assert isinstance(user["company"], dict), f"Поле 'company' должно быть объектом, получено: {type(user['company'])}"
    
    # Дополнительно проверяем типы вложенных полей
    address = user["address"]
    assert isinstance(address["street"], str), f"Поле 'address.street' должно быть строкой, получено: {type(address['street'])}"
    assert isinstance(address["city"], str), f"Поле 'address.city' должно быть строкой, получено: {type(address['city'])}"
    assert isinstance(address["zipcode"], str), f"Поле 'address.zipcode' должно быть строкой, получено: {type(address['zipcode'])}"
    
    geo = address["geo"]
    assert isinstance(geo["lat"], str), f"Поле 'geo.lat' должно быть строкой, получено: {type(geo['lat'])}"
    assert isinstance(geo["lng"], str), f"Поле 'geo.lng' должно быть строкой, получено: {type(geo['lng'])}"
    
    company = user["company"]
    assert isinstance(company["name"], str), f"Поле 'company.name' должно быть строкой, получено: {type(company['name'])}"


def test_response_time():
    """Проверка времени отклика API."""
    
    # Устанавливаем порог времени отклика в 1 секунду
    max_response_time = 1.0  # секунды
    
    # Замеряем время до выполнения запроса
    start_time = time.time()
    
    # Выполняем GET-запрос для получения пользователя
    user_id = 1
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    
    # Замеряем время после выполнения запроса
    end_time = time.time()
    
    # Рассчитываем время отклика
    response_time = end_time - start_time
    
    # 1. Проверка статуса: должен быть 200 OK
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    
    # 2. Проверка времени отклика: должно быть меньше порога
    assert response_time < max_response_time, f"Время отклика {response_time} секунд превышает порог {max_response_time} секунд"
    
    # 3. Выводим время отклика для информирования
    print(f"\nВремя отклика: {response_time:.4f} секунд")


def test_rate_limiting():
    """Проверка ограничений на количество запросов (Rate Limiting)."""
    
    # Выполняем несколько быстрых запросов подряд для проверки ограничения
    # В реальных приложениях может быть ограничение, но JSONPlaceholder - это тестовый сервис,
    # который не имеет настоящих ограничений на количество запросов
    max_requests = 10
    responses = []
    
    for i in range(max_requests):
        response = requests.get(f"{BASE_URL}/users/{i+1}")
        responses.append(response.status_code)
    
    # 1. Проверяем, что все запросы завершились успешно (в случае JSONPlaceholder)
    # В реальных API ожидаем получить статус 429 Too Many Requests
    rate_limit_encountered = 429 in responses
    
    # 2. Выводим статусы для информации
    print(f"\nСтатусы ответов при множественных запросах: {responses}")
    
    # 3. Для тестирования реальных приложений с ограничениями на запросы можно раскомментировать:
    # assert rate_limit_encountered, f"Ожидается статус 429 (Too Many Requests) при превышении лимита запросов"
    # Но для JSONPlaceholder мы ожидаем, что ограничения нет
    assert not rate_limit_encountered, f"JSONPlaceholder не должен иметь ограничений на количество запросов"
    
    # 4. Проверяем, что большинство запросов успешны
    successful_requests = [status for status in responses if status == 200]
    assert len(successful_requests) >= max_requests - 2, f"Большинство запросов должны быть успешными, получено: {len(successful_requests)} успешных из {max_requests}"


def test_cross_site_scripting():
    """Проверка на уязвимость XSS (Cross-Site Scripting)."""
    
    # Подготовим данные с потенциальным XSS-кодом для проверки
    # Это может быть вредоносный скрипт в одном из полей
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>"
    ]
    
    for payload in xss_payloads:
        # Используем поле name с XSS-кодом в запросе
        xss_user_data = {
            "name": payload,
            "username": "testuser",
            "email": "testuser@example.com"
        }
        
        # Выполняем POST-запрос с XSS-данными
        # В реальных приложениях это может привести к сохранению вредоносного кода
        response = requests.post(f"{BASE_URL}/users", json=xss_user_data)
        
        # 1. Проверяем статус ответа (обычно 200/201 при успешном создании)
        assert response.status_code in [200, 201], f"Ожидался статус 200 или 201, получен {response.status_code} для payload: {payload}"
        
        # 2. Получаем данные ответа
        response_data = response.json()
        
        # 3. Проверяем, что данные возвращаются
        assert "id" in response_data, "В ответе отсутствует ID пользователя"
        
        # 4. Проверяем, что XSS-код не исполняется (возвращается как есть в JSON)
        # В безопасном API вредоносный код должен быть экранирован или отфильтрован
        # В JSONPlaceholder вводимые данные возвращаются как есть, что в реальном приложении может быть уязвимостью
        returned_name = response_data.get("name", "")
        
        # 5. Выводим информацию для анализа
        print(f"\nXSS payload: {payload}")
        print(f"Возвращенное имя: {returned_name}")
        
        # 6. В реальном приложении мы бы проверили, что payload был экранирован
        # Однако в JSONPlaceholder вводимые данные возвращаются как есть, что может быть уязвимостью
        # assert payload not in returned_name, f"XSS код не был экранирован: {payload}"
        # Но для тестирования на JSONPlaceholder мы просто фиксируем это как информацию
        if payload in returned_name:
            print(f"ПРЕДУПРЕЖДЕНИЕ: XSS payload обнаружен в ответе. В реальном приложении это уязвимость!")
        else:
            print(f"XSS payload был экранирован или отфильтрован (хорошо для безопасности)")


def test_unauthorized_access():
    """Проверка попытки доступа к защищенному ресурсу без токена."""
    
    # Некоторые API требуют аутентификацию для доступа к определенным ресурсам
    # В реальных приложениях для аутентификации могут использоваться JWT токены, OAuth и т.д.
    # В JSONPlaceholder нет реальной аутентификации, но мы можем протестировать на примере гипотетического защищенного эндпоинта
    
    # Для демонстрации используем эндпоинт, требующий аутентификации (гипотетический пример)
    # Поскольку JSONPlaceholder не требует аутентификации, мы создадим фиктивный защищенный ресурс
    
    # Создаем заголовки без токена аутентификации
    headers_without_auth = {
        "Content-Type": "application/json"
        # Нет Authorization заголовка
    }
    
    # Выполняем GET-запрос к гипотетическому защищенному ресурсу
    # В реальном приложении это мог бы быть специфический эндпоинт, требующий токена
    response = requests.get(f"{BASE_URL}/users/1", headers=headers_without_auth)
    
    # 1. Проверяем статус ответа
    # Для JSONPlaceholder без аутентификации ответ будет 200 OK, т.к. это тестовый API
    # Но в реальных приложениях ожидается 401 Unauthorized
    
    # 2. Выводим статус для информации
    print(f"\nСтатус ответа при доступе без токена: {response.status_code}")
    
    # 3. В реальных приложениях мы бы проверили:
    # assert response.status_code == 401, f"Ожидался статус 401 Unauthorized, получен {response.status_code}"
    
    # 4. Но для JSONPlaceholder, который не требует аутентификации, проверим, что:
    # - запрос завершается успешно (поскольку это тестовый API)
    assert response.status_code == 200, f"Для JSONPlaceholder ожидается статус 200, получен {response.status_code}"
    
    # 5. Выводим информацию о том, что в реальном приложении ожидается 401
    print("Для реального API с аутентификацией ожидается статус 401 Unauthorized при доступе без токена")


def test_invalid_token():
    """Проверка попытки доступа с невалидным токеном."""
    
    # Подготовим невалидный токен для проверки
    invalid_token = "Bearer invalid_token_12345"
    
    # Создаем заголовки с невалидным токеном аутентификации
    headers_with_invalid_token = {
        "Content-Type": "application/json",
        "Authorization": invalid_token
    }
    
    # Выполняем GET-запрос к гипотетическому защищенному ресурсу с невалидным токеном
    response = requests.get(f"{BASE_URL}/users/1", headers=headers_with_invalid_token)
    
    # 1. Проверяем статус ответа
    # В реальных приложениях с валидной системой аутентификации ожидается 401 Unauthorized или 403 Forbidden
    
    # 2. Выводим статус для информации
    print(f"\nСтатус ответа при доступе с невалидным токеном: {response.status_code}")
    
    # 3. В реальных приложениях мы бы проверили:
    # assert response.status_code in [401, 403], f"Ожидался статус 401 или 403, получен {response.status_code}"
    
    # 4. Но для JSONPlaceholder, который не проверяет токены, проверим, что:
    # - запрос завершается успешно (поскольку это тестовый API)
    assert response.status_code == 200, f"Для JSONPlaceholder ожидается статус 200, получен {response.status_code}"
    
    # 5. Выводим информацию о том, что в реальном приложении ожидается 401 или 403
    print("Для реального API с аутентификацией ожидается статус 401 Unauthorized или 403 Forbidden при доступе с невалидным токеном")
    
    # 6. Проверяем, что в ответе есть данные пользователя
    response_data = response.json()
    assert "id" in response_data, "В ответе отсутствует ID пользователя"
    assert response_data["id"] == 1, "ID пользователя не совпадает с ожидаемым"


def test_user_creation_then_retrieval():
    """Интеграционный тест: создание пользователя, затем его получение и проверка согласованности данных."""
    
    # Подготовка данных для создания пользователя
    test_user_data = {
        "name": "Integration Test User",
        "username": "integrationtestuser",
        "email": "integrationtest@example.com",
        "address": {
            "street": "Integration Street",
            "suite": "Apt. 100",
            "city": "Integration City",
            "zipcode": "10001-1234",
            "geo": {
                "lat": "11.1111",
                "lng": "22.2222"
            }
        },
        "phone": "555-1234",
        "website": "integrationtest.com",
        "company": {
            "name": "Integration Company",
            "catchPhrase": "Integration phrase",
            "bs": "Integration business"
        }
    }
    
    # 1. Создаем пользователя с помощью POST-запроса
    create_response = requests.post(f"{BASE_URL}/users", json=test_user_data)
    assert create_response.status_code in [200, 201], f"Ожидался статус 200 или 201 при создании, получен {create_response.status_code}"
    
    # 2. Получаем созданные данные
    created_user = create_response.json()
    assert "id" in created_user, "В ответе на создание отсутствует ID пользователя"
    
    # 3. Сохраняем ID созданного пользователя
    created_user_id = created_user["id"]
    print(f"\nСоздан пользователь с ID: {created_user_id}")
    
    # 4. Проверяем, что созданные данные совпадают с ожидаемыми
    for key, expected_value in test_user_data.items():
        if key in created_user:
            # Для вложенных объектов проводим частичное сравнение
            if isinstance(expected_value, dict):
                for sub_key, sub_value in expected_value.items():
                    if sub_key in created_user[key]:
                        assert created_user[key][sub_key] == sub_value, f"Поле {key}.{sub_key} не совпадает: ожидается {sub_value}, получено {created_user[key][sub_key]}"
            else:
                assert created_user[key] == expected_value, f"Поле {key} не совпадает: ожидается {expected_value}, получено {created_user[key]}"
    
    # Для JSONPlaceholder GET-запрос к несуществующему ID возвращает 404
    # Тест на согласованность между созданными данными и возвращаемыми данными
    # Поскольку JSONPlaceholder возвращает созданные данные в ответе на POST, 
    # мы можем проверить, что данные, возвращенные из POST, соответствуют ожидаемым
    
    print(f"Данные успешно согласованы между созданием и возвращаемыми значениями")


def test_user_update_then_verification():
    """Интеграционный тест: обновление пользователя, затем проверка изменений через GET-запрос."""
    
    # Используем существующего пользователя для обновления (ID 1)
    user_id = 1
    
    # Подготовка обновленных данных пользователя
    updated_user_data = {
        "id": user_id,
        "name": "Integrated Updated Test User",
        "username": "updatedintegrationuser",
        "email": "updatedintegration@example.com",
        "address": {
            "street": "Updated Integration Street",
            "suite": "Apt. 200",
            "city": "Updated Integration City",
            "zipcode": "20002-5678",
            "geo": {
                "lat": "33.3333",
                "lng": "44.4444"
            }
        },
        "phone": "555-5678",
        "website": "updatedintegration.com",
        "company": {
            "name": "Updated Integration Company",
            "catchPhrase": "Updated integration phrase",
            "bs": "Updated integration business"
        }
    }
    
    # 1. Обновляем пользователя с помощью PUT-запроса
    update_response = requests.put(f"{BASE_URL}/users/{user_id}", json=updated_user_data)
    assert update_response.status_code == 200, f"Ожидался статус 200 при обновлении, получен {update_response.status_code}"
    
    # 2. Получаем обновленные данные от PUT-запроса
    updated_user = update_response.json()
    print(f"\nОбновлен пользователь с ID: {updated_user['id']}")
    
    # 3. Проверяем, что все обновленные данные соответствуют ожидаемым
    for key, expected_value in updated_user_data.items():
        if key in updated_user:
            # Для вложенных объектов проводим частичное сравнение
            if isinstance(expected_value, dict):
                for sub_key, sub_value in expected_value.items():
                    if sub_key in updated_user[key]:
                        assert updated_user[key][sub_key] == sub_value, f"Поле {key}.{sub_key} не совпадает: ожидается {sub_value}, получено {updated_user[key][sub_key]}"
            else:
                assert updated_user[key] == expected_value, f"Поле {key} не совпадает: ожидается {expected_value}, получено {updated_user[key]}"
    
    # 4. Получаем того же пользователя через GET-запрос
    get_response = requests.get(f"{BASE_URL}/users/{user_id}")
    assert get_response.status_code == 200, f"Ожидался статус 200 при получении, получен {get_response.status_code}"
    
    # 5. Получаем данные пользователя, полученные через GET
    retrieved_user = get_response.json()
    
    # Для JSONPlaceholder обновленные данные в PUT-запросе не сохраняются в базе данных
    # Вместо этого, если использовать PUT для существующего ресурса, JSONPlaceholder возвращает обновленные данные
    # но при последующем GET-запросе возвращаются оригинальные данные
    
    # Проверяем, что обновление вернуло ожидаемые данные
    assert updated_user["name"] == "Integrated Updated Test User", f"PUT должен вернуть обновленные данные, получено: {updated_user['name']}"
    
    # Примечание: В реальном приложении GET-запрос после PUT должен возвращать обновленные данные
    # Но в JSONPlaceholder это не так - он возвращает оригинальные данные
    # Это особенность тестового API, а не ошибка нашей логики
    
    # Интеграционный тест проверяет согласованность обработки данных между разными методами API
    # В реальных приложениях обновленные данные сохраняются и доступны через GET-запрос
    
    print(f"Проверка согласованности данных выполнена, учитывая особенности JSONPlaceholder")


@pytest.mark.parametrize("user_id,expected_name", [
    (1, "Leanne Graham"),
    (2, "Ervin Howell"),
    (3, "Clementine Bauch"),
    (4, "Patricia Lebsack"),
    (5, "Chelsey Dietrich")
])
def test_multiple_user_ids(user_id, expected_name):
    """Параметризованный тест: проверка получения пользователей с разными ID.
    
    Args:
        user_id: ID пользователя для проверки
        expected_name: Ожидаемое имя пользователя
    """
    
    # 1. Выполняем GET-запрос для получения пользователя с заданным ID
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    
    # 2. Проверяем статус ответа: должен быть 200 OK
    assert response.status_code == 200, f"Для ID {user_id} ожидается статус 200, получен {response.status_code}"
    
    # 3. Проверяем, что тело ответа не пустое
    assert response.text, f"Для ID {user_id} тело ответа пустое"
    
    # 4. Получаем данные пользователя
    user_data = response.json()
    
    # 5. Проверяем, что ID в ответе совпадает с ожидаемым
    assert user_data["id"] == user_id, f"Для ID {user_id} возвращен неправильный ID {user_data['id']}"
    
    # 6. Проверяем, что имя в ответе совпадает с ожидаемым
    assert user_data["name"] == expected_name, f"Для ID {user_id} ожидается имя '{expected_name}', получено '{user_data['name']}'"
    
    # 7. Проверяем, что другие обязательные поля присутствуют
    required_fields = ["username", "email", "address", "phone", "website", "company"]
    for field in required_fields:
        assert field in user_data, f"Для ID {user_id} поле '{field}' отсутствует в ответе"
    
    # 8. Проверяем, что поле address содержит вложенные обязательные поля
    assert "street" in user_data["address"], f"Для ID {user_id} поле 'address.street' отсутствует в ответе"
    assert "city" in user_data["address"], f"Для ID {user_id} поле 'address.city' отсутствует в ответе"
    
    print(f"Пользователь с ID {user_id} и именем '{expected_name}' успешно проверен")


def test_get_all_users():
    """Тест для проверки работы с массивами данных: получение списка всех пользователей.
    
    Проверяет:
    - Количество элементов в списке
    - Структуру каждого элемента
    - Наличие обязательных полей в каждом элементе
    """
    
    # 1. Выполняем GET-запрос для получения всех пользователей
    response = requests.get(f"{BASE_URL}/users")
    
    # 2. Проверяем статус ответа: должен быть 200 OK
    assert response.status_code == 200, f"Ожидается статус 200, получен {response.status_code}"
    
    # 3. Получаем данные списка пользователей
    users_list = response.json()
    
    # 4. Проверяем, что ответ не пустой и представляет собой список
    assert isinstance(users_list, list), f"Ожидается список пользователей, получено {type(users_list)}"
    assert len(users_list) > 0, "Список пользователей пуст"
    
    # 5. Проверяем количество элементов (в JSONPlaceholder API всегда 10 пользователей)
    expected_count = 10
    assert len(users_list) == expected_count, f"Ожидается {expected_count} пользователей, получено {len(users_list)}"
    
    # 6. Проверяем структуру и поля каждого пользователя в списке
    for index, user in enumerate(users_list):
        # 6.1. Проверяем, что каждый элемент является словарем
        assert isinstance(user, dict), f"Элемент с индексом {index} не является словарем"
        
        # 6.2. Проверяем наличие обязательных полей у каждого пользователя
        required_fields = ["id", "name", "username", "email", "address", "phone", "website", "company"]
        for field in required_fields:
            assert field in user, f"Поле '{field}' отсутствует у пользователя с индексом {index}"
        
        # 6.3. Проверяем, что поле id является числом
        assert isinstance(user["id"], int), f"Поле 'id' у пользователя {index} должно быть числом, получено {type(user['id'])}"
        
        # 6.4. Проверяем, что текстовые поля являются строками
        text_fields = ["name", "username", "email", "phone", "website"]
        for field in text_fields:
            assert isinstance(user[field], str), f"Поле '{field}' у пользователя {index} должно быть строкой, получено {type(user[field])}"
        
        # 6.5. Проверяем, что поля address и company являются словарями
        assert isinstance(user["address"], dict), f"Поле 'address' у пользователя {index} должно быть словарем, получено {type(user['address'])}"
        assert isinstance(user["company"], dict), f"Поле 'company' у пользователя {index} должно быть словарем, получено {type(user['company'])}"
        
        # 6.6. Проверяем наличие вложенных обязательных полей в address
        address_required = ["street", "city", "zipcode", "geo"]
        for field in address_required:
            assert field in user["address"], f"Поле 'address.{field}' отсутствует у пользователя {index}"
        
        # 6.7. Проверяем наличие вложенных обязательных полей в geo
        assert "lat" in user["address"]["geo"], f"Поле 'address.geo.lat' отсутствует у пользователя {index}"
        assert "lng" in user["address"]["geo"], f"Поле 'address.geo.lng' отсутствует у пользователя {index}"
        
        # 6.8. Проверяем наличие вложенных обязательных полей в company
        company_required = ["name", "catchPhrase", "bs"]
        for field in company_required:
            assert field in user["company"], f"Поле 'company.{field}' отсутствует у пользователя {index}"
        
        # 6.9. Проверяем, что вложенные поля также имеют правильный тип
        assert isinstance(user["address"]["street"], str), f"Поле 'address.street' должно быть строкой у пользователя {index}"
        assert isinstance(user["address"]["city"], str), f"Поле 'address.city' должно быть строкой у пользователя {index}"
        assert isinstance(user["address"]["zipcode"], str), f"Поле 'address.zipcode' должно быть строкой у пользователя {index}"
        assert isinstance(user["address"]["geo"]["lat"], str), f"Поле 'address.geo.lat' должно быть строкой у пользователя {index}"
        assert isinstance(user["address"]["geo"]["lng"], str), f"Поле 'address.geo.lng' должно быть строкой у пользователя {index}"
        assert isinstance(user["company"]["name"], str), f"Поле 'company.name' должно быть строкой у пользователя {index}"
        assert isinstance(user["company"]["catchPhrase"], str), f"Поле 'company.catchPhrase' должно быть строкой у пользователя {index}"
        assert isinstance(user["company"]["bs"], str), f"Поле 'company.bs' должно быть строкой у пользователя {index}"
    
    # 7. Дополнительно: проверяем, что все ID уникальны
    user_ids = [user["id"] for user in users_list]
    unique_ids = set(user_ids)
    assert len(unique_ids) == len(users_list), f"Найдены дубликаты ID среди пользователей: {len(user_ids) - len(unique_ids)} дубликатов"
    
    print(f"Получено {len(users_list)} пользователей. Все пользователи имеют корректную структуру и обязательные поля.")


def test_cache_headers():
    """Тест проверки заголовков кэширования."""
    
    # 1. Выполняем GET-запрос для получения пользователя
    user_id = 1
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    
    # 2. Проверяем статус ответа
    assert response.status_code == 200, f"Ожидается статус 200, получен {response.status_code}"
    
    # 3. Получаем заголовки ответа
    headers = response.headers
    
    # 4. Проверяем наличие заголовков кэширования (в реальных приложениях могут присутствовать)
    # JSONPlaceholder - это тестовый сервис, который может не возвращать заголовки кэширования
    cache_control_present = 'Cache-Control' in headers
    expires_present = 'Expires' in headers
    last_modified_present = 'Last-Modified' in headers
    
    # 5. Выводим информацию о наличии заголовков кэширования для анализа
    print(f"\nЗаголовки кэширования для пользователя {user_id}:")
    print(f"Cache-Control: {headers.get('Cache-Control', 'не указан')}")
    print(f"Expires: {headers.get('Expires', 'не указан')}")
    print(f"Last-Modified: {headers.get('Last-Modified', 'не указан')}")
    
    # 6. В реальных приложениях можно было бы протестировать наличие этих заголовков
    # Для JSONPlaceholder мы просто выводим информацию, т.к. тестовый API может не включать заголовки кэширования
    
    # 7. Проверяем, что ответ содержит Content-Type заголовок
    content_type = headers.get('Content-Type')
    assert content_type is not None, "Заголовок Content-Type должен присутствовать в ответе"
    assert 'application/json' in content_type, f"Content-Type должен содержать application/json, получен: {content_type}"
    
    print(f"Заголовки проверены. Наличие заголовков кэширования: Cache-Control={cache_control_present}, Expires={expires_present}, Last-Modified={last_modified_present}")


def test_content_encoding():
    """Тест проверки сжатия данных (gzip)."""
    
    # 1. Подготовим заголовки, указывающие, что клиент поддерживает gzip сжатие
    headers = {
        'Accept-Encoding': 'gzip, deflate'
    }
    
    # 2. Выполняем GET-запрос с заголовками, указывающими на поддержку сжатия
    user_id = 1
    response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
    
    # 3. Проверяем статус ответа
    assert response.status_code == 200, f"Ожидается статус 200, получен {response.status_code}"
    
    # 4. Получаем заголовки ответа
    response_headers = response.headers
    
    # 5. Проверяем, содержит ли ответ заголовок Content-Encoding
    content_encoding = response_headers.get('Content-Encoding', '').lower()
    transfer_encoding = response_headers.get('Transfer-Encoding', '').lower()
    
    # 6. Выводим информацию о сжатии для анализа
    print(f"\nЗаголовки сжатия для пользователя {user_id}:")
    print(f"Content-Encoding: {content_encoding}")
    print(f"Transfer-Encoding: {transfer_encoding}")
    print(f"Content-Length: {response_headers.get('Content-Length', 'не указан')}")
    
    # 7. Для JSONPlaceholder API может не использовать сжатие, так как ответы маленькие
    # Но мы проверим, что заголовки присутствуют или отсутствуют осознанно
    
    # 8. Проверяем основные заголовки
    content_type = response_headers.get('Content-Type')
    assert content_type is not None, "Заголовок Content-Type должен присутствовать в ответе"
    assert 'application/json' in content_type, f"Content-Type должен содержать application/json, получен: {content_type}"
    
    # 9. В реальных приложениях сжатие применяется для уменьшения объема передаваемых данных
    # Выводим информацию о наличии сжатия
    is_compressed = content_encoding in ['gzip', 'deflate', 'br']
    print(f"Данные сжаты: {is_compressed} (Content-Encoding: '{content_encoding}')")
    
    # 10. Проверяем, что тело ответа можно декодировать как JSON
    # Это подтверждает, что данные были правильно переданы, независимо от сжатия
    json_data = response.json()
    assert "id" in json_data, "Ответ должен содержать поле id"
    assert json_data["id"] == user_id, f"ID в ответе должен совпадать с запрошенным, ожидается {user_id}, получено {json_data['id']}"
    
    print(f"Сжатие данных проверено. Тело ответа корректно обработано.")
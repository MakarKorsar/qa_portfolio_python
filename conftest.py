import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import allure

@pytest.fixture(scope="module")
def browser():
    # Настройки для headless режима
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск без GUI
    chrome_options.add_argument("--no-sandbox")  # Обход проблем в контейнере/CI
    chrome_options.add_argument("--disable-dev-shm-usage")  # Обход проблем с памятью
    chrome_options.add_argument("--disable-gpu")  # Отключение GPU (важно для headless)
    chrome_options.add_argument("--window-size=1920,1080")  # Установка размера окна
    
    # Используем webdriver_manager для автоматической установки драйвера
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit() # Закрываем браузер после всех тестов в модуле

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Attach screenshots to Allure reports on test failure
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        if hasattr(item.instance, "driver"):
            try:
                allure.attach(
                    item.instance.driver.get_screenshot_as_png(),
                    name="Screenshot on failure",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"Failed to take screenshot: {e}")
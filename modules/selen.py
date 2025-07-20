from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def save_cookies(driver, filename):
    cookies = driver.get_cookies()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)


def accept_cookies_and_save(url, cookie_button_selector, cookie_file):
    options = Options()
    options.add_argument("--headless")  # запускаем без GUI
    options.add_argument("--disable-gpu")  # для стабильности
    options.add_argument("--no-sandbox")  # если запускается на Linux сервере
    options.add_argument("--window-size=1920,1080")  # иногда помогает отобразить элементы

    driver = webdriver.Chrome(options=options)

    driver.get(url)

    try:
        button = driver.find_element(By.XPATH, "//button[.//text()[normalize-space(.)='Принять все']]")
        button.click()
        print("Нажали кнопку 'Принять всё'")
    except Exception:
        print("Кнопка 'Принять всё' не найдена или уже нажата")

    # Немного подождать, чтобы куки установились
    WebDriverWait(driver, 3).until(lambda d: True)

    save_cookies(driver, cookie_file)
    print(f"Куки сохранены в {cookie_file}")

    driver.quit()


def initiate_selenium():
    url = "https://www.youtube.com"
    cookie_button_selector = "button[aria-label='Принять все']"  # пример для YouTube
    cookie_file = "cookies.json"

    accept_cookies_and_save(url, cookie_button_selector, cookie_file)
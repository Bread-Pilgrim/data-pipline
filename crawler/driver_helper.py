import time

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

from core.config import Configs

configs = Configs()


def get_driver():
    """크롬 드라이버 가져오기."""
    return webdriver.Chrome()


def open_crawl_url(driver):
    """크롤링할 사이트 접근."""
    driver.get(configs.CRAWL_URL)
    time.sleep(2)

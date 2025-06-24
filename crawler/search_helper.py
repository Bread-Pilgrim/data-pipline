from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def extract_search_results(driver):
    """검색 결과로 나타난 모든 PlaceItem 요소들을 반환"""
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".PlaceItem"))
    )
    return driver.find_elements(By.CSS_SELECTOR, ".PlaceItem")


def search_place(driver, keyword: str):
    """장소 검색"""
    search_box = driver.find_element(By.ID, "search.keyword.query")
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.ENTER)

    # 검색 결과가 로딩될 때까지 기다리기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".PlaceItem"))
    )


def go_to_next_page(driver, current_page: int) -> int:
    """다음 페이지로 넘어가기"""
    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "dimmedLayer"))
        )
    except Exception as e:
        print("dimmedLayer 아직 있음", e)

    try:
        if current_page == 1:
            btn = driver.find_element(By.ID, "info.search.place.more")
        else:
            btn = driver.find_element(By.ID, f"info.search.page.no{current_page+1}")

        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        driver.execute_script("arguments[0].click();", btn)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".PlaceItem"))
        )
        return 1
    except:
        return 0  # 종료 신호

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.processor import extract_gu_and_dong, process_hours

EXCLUDED_MENU_TARGETS = [
    "아메리카노",
    "라떼",
    "아이스티",
    "빙수",
    "에스프레소",
    "카푸치노",
    "에이드",
    "핸드드립",
    "유자차",
    "자몽차",
    "레몬차",
    "드립 커피",
    "루이보스" "잉글리시브렉퍼스트",
    "카페모카",
    "카라멜마키아토",
    "더치",
    "아포가토",
    "스무디",
    "우유",
    "밀크티",
]


def extract_base_info(element):
    """바로 긁어올 수 있는 요소 반환"""

    name = element.find_element(By.CSS_SELECTOR, '[data-id="name"]').get_attribute(
        "title"
    )
    address = element.find_element(By.CSS_SELECTOR, '[data-id="address"]').text
    other_address = element.find_element(By.CSS_SELECTOR, '[data-id="otherAddr"]').text
    phone = element.find_element(By.CSS_SELECTOR, '[data-id="phone"]').text
    gu, dong, area = extract_gu_and_dong(address, other_address)
    return {
        "name": name,  # 📦 빵집 이름
        "address": address,  # 📦 주소 전문
        "gu": gu,  # 📦 자치구
        "dong": dong,  # 📦 동
        "area": area,  # 📦 상권지역
        "phone": phone,  # 📦 연락처
    }


def extract_operation_hours(driver, main_detail):
    """영업시간 추출하는 메소드 ."""

    try:
        op_section = main_detail.find_element(
            By.CSS_SELECTOR, ".default_info .info_operation"
        )
        more_btn = op_section.find_element(
            By.XPATH, '//button[@aria-controls="foldDetail2"]'
        )

        # 버튼 클릭
        driver.execute_script("arguments[0].click();", more_btn)
        time.sleep(1)

        if more_btn.get_attribute("aria-expanded"):
            # 클릭이 제대로 먹혔을 때
            details = main_detail.find_element(By.ID, "foldDetail2").find_elements(
                By.CSS_SELECTOR, ".line_fold"
            )

            detail_list = []

            for d in details:
                title = None
                try:
                    titles = d.find_elements(By.CSS_SELECTOR, ".tit_fold")
                    title = titles[0].text if titles else None
                except:
                    print("title 따로 없음.")

                hours = d.find_element(By.CSS_SELECTOR, ".txt_detail").text
                detail_list.append({"title": title, "hours": hours})
            return detail_list
        else:
            print("버튼 안눌린")
    except Exception as e:
        print(f"영업시간 가져오기 실패 : ", e)
        return []


def extract_menu_items(driver):
    """가게 메뉴 가져오는 메소드."""

    try:
        # 메뉴 탭 클릭-전환 --------------------------------------------------
        tab = driver.find_element(By.CSS_SELECTOR, "#mainContent ul.list_tab")
        menu_btn = tab.find_element(By.CSS_SELECTOR, 'a[href="#menuInfo"]')
        driver.execute_script(
            "arguments[0].setAttribute('aria-selected', 'true');", menu_btn
        )

        driver.execute_script("window.scrollTo(0, 1200)")

        menu_items = []
        menu_list = driver.find_elements(By.CSS_SELECTOR, "ul.list_goods > li")

        for li in menu_list:
            name = li.find_element(By.CSS_SELECTOR, "strong.tit_item").text
            if not any(target in name for target in EXCLUDED_MENU_TARGETS):
                price = li.find_element(By.CSS_SELECTOR, "p.desc_item").text
                desc = li.find_elements(By.CSS_SELECTOR, "p.desc_item2")
                signature = li.find_elements(By.CSS_SELECTOR, "span.badge_label")
                img = li.find_elements(By.CSS_SELECTOR, "a.link_thumb > img")

                menu_items.append(
                    {
                        "name": name,
                        "price": price,
                        "desc": desc[0].text if desc else None,
                        "signature": signature[0].text if signature else None,
                        "thumbnail": img[0].get_attribute("src") if img else None,
                    }
                )
                time.sleep(1)
        return menu_items
    except Exception as e:
        print("메뉴 추출 실패 : ", e)
        return []


def extract_detail_info(driver, room_element):
    """상세보기에서 필요한 데이터 가져오는 메소드."""

    # 현재 창 저장
    main_window = driver.current_window_handle

    # 상세보기 진입
    detail_button = room_element.find_element(By.CSS_SELECTOR, '[data-id="moreview"]')
    driver.execute_script("arguments[0].click();", detail_button)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    new_window = [w for w in driver.window_handles if w != main_window][0]
    driver.switch_to.window(new_window)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainContent"))
        )
        section = driver.find_element(By.CSS_SELECTOR, "#mainContent")

        # 📦 썸네일
        thumbnail = section.find_element(
            By.CSS_SELECTOR, ".link_photo > img.img-thumb"
        ).get_attribute("src")

        main_detail = section.find_element(
            By.CSS_SELECTOR, ".main_detail > .detail_cont"
        )

        # 📦 어느 역에서 도보 몇 분
        rows = main_detail.find_elements(By.CSS_SELECTOR, "div.row_detail")
        second_row = rows[1]

        way_to_go = (
            second_row.find_element(By.CSS_SELECTOR, "span.txt_detail").text
            + main_detail.find_element(By.CSS_SELECTOR, "span.add_mdot").text
        )

        # 📦 영업시간
        hours = extract_operation_hours(driver, main_detail)
        proceed_hours = process_hours(hours)
        # 📦 메뉴
        menus = extract_menu_items(driver)

        return {
            "thumbnail": thumbnail,
            "way_to_go": way_to_go,
            "open_hours": proceed_hours,
            "menus": menus,
        }
    finally:
        driver.close()
        driver.switch_to.window(main_window)

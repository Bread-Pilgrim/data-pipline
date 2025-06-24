import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import Configs

configs = Configs()


def crawl_bakery_infos(keyword="부산 빵집", max_page=3):

    driver = webdriver.Chrome()
    driver.get(configs.CRAWL_URL)
    time.sleep(2)

    # 검색
    search_box = driver.find_element(By.ID, "search.keyword.query")
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.ENTER)

    # 검색 결과가 로딩될 때까지 기다리기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".PlaceItem"))
    )

    results = []
    page = 1

    # TODO : 같은 베이커리 중복으로 크롤링 못하게 하는 로직 필요함.
    # TODO : 추후에 크론잡 돌릴 예정.
    while page <= max_page:
        print(f"================== {page} 페이지 크롤링 시작 ==================")

        # 매 페이지마다 빵집 리스트 다시 수집
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".PlaceItem"))
        )
        room_lists = driver.find_elements(By.CSS_SELECTOR, ".PlaceItem")

        room_lists = driver.find_elements(By.CSS_SELECTOR, ".PlaceItem")

        for room in room_lists[:2]:
            try:
                # ----------------------------------- 1차 수집데이터
                # 가게명
                name = room.find_element(
                    By.CSS_SELECTOR, '[data-id="name"]'
                ).get_attribute("title")
                # 2. full_address
                full_address = room.find_element(
                    By.CSS_SELECTOR, '[data-id="address"]'
                ).text
                # 3. 지번 주소
                other_address = room.find_element(
                    By.CSS_SELECTOR, '[data-id="otherAddr"]'
                ).text
                # 4. 전화번호
                phone = room.find_element(By.CSS_SELECTOR, '[data-id="phone"]').text
            except Exception as e:
                print("1차 수집데이터 오류 발생 :  ", e)

            # ----------------------------------- 상세페이지 들어갔다 나와야 함 (썸네일, 영업시간, 메뉴)
            try:
                # 현재 창 저장
                main_window = driver.current_window_handle

                # 상세페이지 - 새 탭으로 열기
                detail_button = room.find_element(
                    By.CSS_SELECTOR, '[data-id="moreview"]'
                )

                # 오버레이 때문에 클릭 안되는 이슈 -> dimmedlayer 없어질 때 까지 대기
                driver.execute_script("arguments[0].click();", detail_button)
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

                # 새 탭으로 전환
                new_window = [w for w in driver.window_handles if w != main_window][0]
                driver.switch_to.window(new_window)

            except Exception as e:
                print("전환되지 않음", e)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#mainContent"))
                )
                main_section = driver.find_element(By.CSS_SELECTOR, "#mainContent")

                # 썸네일
                thumb_nail = main_section.find_element(
                    By.CSS_SELECTOR, ".link_photo > img.img-thumb"
                ).get_attribute("src")

                main_detail = main_section.find_element(
                    By.CSS_SELECTOR, ".main_detail > .detail_cont"
                )
                # how to 도보
                way_to_go = (
                    main_detail.find_element(By.CSS_SELECTOR, "span.txt_detail").text
                    + main_detail.find_element(By.CSS_SELECTOR, "span.add_mdot").text
                )

            except Exception as e:
                print("수집되지 않음", e)

            try:
                operation_section = main_detail.find_element(
                    By.CSS_SELECTOR, ".default_info .info_operation"
                )
                more_button = operation_section.find_element(
                    By.XPATH, '//button[@aria-controls="foldDetail2"]'
                )
                # 버튼 클릭
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(1)

                if more_button.get_attribute("aria-expanded"):
                    # 클릭이 제대로 먹혔을 때
                    operation_section_detail = main_detail.find_element(
                        By.ID, "foldDetail2"
                    )

                    open_hours = operation_section_detail.find_elements(
                        By.CSS_SELECTOR, ".line_fold"
                    )

                    for o in open_hours:
                        try:
                            # 요일 / 휴무일 같은 오픈 시간
                            tit = o.find_element(By.CSS_SELECTOR, ".tit_fold").text
                        except:
                            print("tit 없음")

                        try:
                            # 찐 시간대
                            hours = o.find_element(By.CSS_SELECTOR, ".txt_detail").text
                        except:
                            print("tit 없음")

            except Exception as e:
                print("영업시간 수집 X", e)

            # 메뉴 크롤링
            try:
                # 메뉴 탭 클릭
                tab_section = driver.find_element(
                    By.CSS_SELECTOR, "#mainContent ul.list_tab"
                )
                menu_button = tab_section.find_element(
                    By.CSS_SELECTOR, 'a[href="#menuInfo"]'
                )
                driver.execute_script(
                    "arguments[0].setAttribute('aria-selected', 'true');", menu_button
                )

                menu_list = driver.find_elements(By.CSS_SELECTOR, "ul.list_goods > li")
                for m in menu_list:
                    thumbs = m.find_elements(By.CSS_SELECTOR, "a.link_thumb > img")
                    # 메뉴 썸네일
                    thumb_nail_src = thumbs[0].get_attribute("src") if thumbs else None

                    signatures = m.find_elements(By.CSS_SELECTOR, "span.badge_label")
                    # 시그니처 메뉴여부
                    signature = signatures[0].text if signatures else None

                    menu_names = m.find_elements(By.CSS_SELECTOR, "strong.tit_item")
                    # 메뉴이름
                    menu_name = menu_names[0].text

                    prices = m.find_elements(By.CSS_SELECTOR, "p.desc_item")
                    # 가격
                    price = prices[0].text
            except Exception as e:
                print("메뉴수집 X", e)
            finally:
                # 다시 원래창으로 돌아오기
                driver.close()
                driver.switch_to.window(main_window)

        results = []

        # 다음 페이지
        try:
            print("이보세요.", page)
            if page == 1:  # 첫 페이지 땐 더 보기 뉼러야 함.
                try:
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((By.ID, "dimmedLayer"))
                    )
                except:
                    print("dimmedLayer 아직 있음")

                place_more = driver.find_element(By.ID, "info.search.place.more")
                driver.execute_script("arguments[0].scrollIntoView(true);", place_more)
                driver.execute_script("arguments[0].click();", place_more)
                time.sleep(10)
                page += 1
            else:
                next_page_id = f"info.search.page.no{page+1}"
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, next_page_id))
                )
                next_page_btn = driver.find_element(By.ID, next_page_id)
                driver.execute_script("arguments[0].click();", next_page_btn)
                time.sleep(10)
                page += 1

        except Exception as e:
            print("다음 페이지 없음 또는 클릭 실패:", e)
            break

    print("크롤링 완료. 5초 뒤 종료합니다.")
    time.sleep(5)
    driver.quit()
    return results


if __name__ == "__main__":
    crawl_bakery_infos("부산 빵집", max_page=3)

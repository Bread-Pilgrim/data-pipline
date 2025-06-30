import json
import time
from parser.bakery_parser import extract_base_info, extract_detail_info

from selenium.webdriver.support import expected_conditions as EC

from crawler.driver_helper import get_driver, open_crawl_url
from crawler.search_helper import extract_search_results, go_to_next_page, search_place


def crawl_bakery_infos(keyword="부산 빵집", max_page=3):

    # 드라이버 세팅
    driver = get_driver()
    open_crawl_url(driver)
    # 부산 빵집 검색
    search_place(driver, keyword)

    results = []

    page = 1

    # TODO : 같은 베이커리 중복으로 크롤링 못하게 하는 로직 필요함.
    # TODO : 추후에 크론잡 돌릴 예정.
    while page <= max_page:
        rooms = extract_search_results(driver)

        print(f"================== {page} 페이지 크롤링 시작 ==================")

        for room in rooms:
            try:
                base_info = extract_base_info(room)
                detail_info = extract_detail_info(driver, room)
                if detail_info.get("menus"):  # menu에 빵메뉴가 하나도 없는 카페 추가 X
                    # results.append({**detail_info})
                    results.append({**base_info, **detail_info})
            except Exception as e:
                print("1차 수집데이터 오류 발생 :  ", e)

        page += go_to_next_page(driver, page)
    driver.quit()
    return results


if __name__ == "__main__":
    res = crawl_bakery_infos("부산 빵집", max_page=1)
    with open("bakery_data2.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

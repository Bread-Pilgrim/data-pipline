from utils.dto import HourInfo

DAY_TO_IDX = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}
GU_TO_AREA = {
    "부산진구": "서면•전포",
    "영구": "광안리•민락",
    "중구": "남포•광복",
    "연제구": "연산•거제",
    "해운대구": "해운대•송정",
    "동래구": "동래•온천장",
    "사하구": "하단•다대포",
    "사상구": "괘법•엄궁",
    "금정구": "장전•부산대",
    "기장군": "기장읍•일광",
    "강서구": "명지•대저",
    "남구": "대연•문현",
    "북구": "기타 지역",
    "서구": "기타 지역",
    "영도구": "기타 지역",
}


def day_to_int(day: str):
    """요일 -> 숫자로 파싱해주는 메소드."""
    return next((idx for d, idx in DAY_TO_IDX.items() if d in day), None)


def tokenize(text: str):
    """공백정리 + 토큰화"""
    return " ".join(text.replace("~", " ~ ").split()).split()


def process_hours(rows):
    """영업시간 가공하는 메소드."""
    infos: list[HourInfo] = []

    for row in rows:
        title, hours = row.get("title"), row.get("hours", "")
        tokens = tokenize(hours)

        # 매일
        if title is None and tokens[:1] == ["매일"] and "~" in tokens:
            open_, close_ = tokens[1], tokens[-1]
            infos.extend(HourInfo(d, open_, close_, True) for d in DAY_TO_IDX.values())
            continue

        # title=휴무일, hours=매주 화요일
        if title == "휴무일" and "매주" in tokens[:3]:
            dow = day_to_int(tokens[-1])
            infos.append(HourInfo(dow, None, None, False))
            continue

        # title=휴무일, hours=설날·추석
        if title == "휴무일":
            infos.append(HourInfo(None, None, None, False, occasion=hours))
            continue

        # title=화, hours=09:00 ~ 20:00
        if title in DAY_TO_IDX:
            dow = DAY_TO_IDX[title]
            if "~" in tokens:
                open_, close_ = tokens[0], tokens[-1]
                infos.append(HourInfo(dow, open_, close_, True))
            elif hours.strip() == "휴무일":
                infos.append(HourInfo(dow, None, None, False))
    return [info.to_dict() for info in infos]


def extract_gu_and_dong(full_adr: str, other_adr: str):
    """주소 전문으로부터 행정구역 추출하는 메소드."""
    gu = None
    dong = None
    area = None

    try:
        gu = full_adr.split(" ")[1] if len(full_adr.split(" ")) > 1 else None
        parts = other_adr.split(", ")
        jibeon = next((p for p in parts if "(지번)" in p), None)

        if jibeon:
            dong_part = jibeon.replace("(지번)", "").strip()
            dong = dong_part.split(" ")[0] if dong_part else None

        area = GU_TO_AREA.get(f"{gu}", "기타 지역")

    except Exception:
        pass

    return gu, dong, area

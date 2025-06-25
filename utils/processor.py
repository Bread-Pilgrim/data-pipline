import json
from dataclasses import asdict
from typing import List

from utils.dto import HourInfo

DAY_TO_IDX = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}


def day_to_int(day: str):
    """요일 -> 숫자로 파싱해주는 메소드."""
    return next((idx for d, idx in DAY_TO_IDX.items() if d in day), None)


def tokenize(text: str):
    """공백정리 + 토큰화"""
    return " ".join(text.replace("~", " ~ ").split()).split()


# ========================== 주소파싱
def extract_gu_and_dong(full_adr: str, other_adr: str):
    """주소 전문으로부터 행정구역 추출하는 메소드."""
    gu = None
    dong = None

    try:
        gu = full_adr.split(" ")[1] if len(full_adr.split(" ")) > 1 else None
        parts = other_adr.split(", ")
        jibeon = next((p for p in parts if "(지번)" in p), None)

        if jibeon:
            dong_part = jibeon.replace("(지번)", "").strip()
            dong = dong_part.split(" ")[0] if dong_part else None

    except Exception:
        pass

    return gu, dong


# ========================== 영업시간 파싱
def parse_open_hours(rows: List[dict]) -> List[HourInfo]:
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
    return infos


def process_bakery_info(raw: List[dict]) -> None:
    for idx, data in enumerate(raw):
        # 영업시간
        hour_infos = parse_open_hours(data.get("open_hours", []))

        with open(f"op_hour_{idx}.json", "w", encoding="utf-8") as f:
            json.dump([asdict(h) for h in hour_infos], f, ensure_ascii=False, indent=2)

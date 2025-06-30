from dataclasses import dataclass
from typing import Optional


@dataclass
class HourInfo:
    """영업시간 정보 모델"""

    day_of_week: Optional[int]  # 0~6 or None (0 : 월, 6 : 일)
    open_time: Optional[str]
    close_time: Optional[str]
    is_opened: bool
    occasion: Optional[str] = None

    def to_dict(self):
        return {
            "day_of_week": self.day_of_week,
            "open_time": self.open_time,
            "close_time": self.close_time,
            "is_opened": self.is_opened,
            "occasion": self.occasion,
        }

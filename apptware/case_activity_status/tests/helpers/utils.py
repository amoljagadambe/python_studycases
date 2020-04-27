import datetime
from typing import Optional


def parse_dt(dt_str: str) -> Optional[datetime.datetime]:
    return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc) if dt_str else None

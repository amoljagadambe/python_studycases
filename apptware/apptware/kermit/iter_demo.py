import itertools
import operator
from dataclasses import dataclass
from typing import Optional



@dataclass
class CaseInfo:
    case_id: int
    bed: str
    room: str
    share_bed: Optional[bool] = False


list_cases = [CaseInfo(case_id=1, bed="b4", room="r1"), CaseInfo(case_id=2, bed="", room="r5"),
              CaseInfo(case_id=1, bed="b4", room="r1")]

list_cases.sort(key=operator.attrgetter('bed','room'))
iter_func = itertools.groupby(list_cases, key=lambda x: (x.bed, x.room))


for key, group in iter_func:
    print("--", key, "--")
    for things in group:
        print(things)

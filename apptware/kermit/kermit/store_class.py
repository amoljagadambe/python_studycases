from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass()
class CaseInfo:
    case_id: str
    date_of_admission: Optional[datetime.datetime] = None


@dataclass()
class CaseNoteInfo:
    case_id: str
    note_type: str = ""
    user_response_type: str = ""
    note_text: str = ""
    last_modified_by: str = ""

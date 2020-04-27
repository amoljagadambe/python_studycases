import logging
import datetime as dt
import itertools
import operator
from typing import Optional
from dataclasses import dataclass
from elasticsearch_dsl import Search, Q
from case_activity_status_update import models as cs_model
from case_activity_status_update import models as case_utils

logger = logging.getLogger(__name__)


@dataclass
class CaseInfo:
    case_id: str
    room: str
    bed: str
    case_activity_status: str
    los: int
    prolonged_los: bool
    has_notes: bool
    share_bed: bool
    future_admission: bool
    date_of_admission: Optional[dt.datetime] = None
    date_of_discharge: Optional[dt.datetime] = None


def get_has_note(es_conn, case_id, dormant_time, note_index):
    q = Q(
        "bool",
        must=[
            Q("term", case_id=case_id),
            Q('range', modified_date={"gte": dormant_time})
        ]
    )
    s = Search(using=es_conn) \
        .index(note_index) \
        .doc_type(cs_model.Note) \
        .query(q) \
        .source()
    has_notes = s.count() > 0
    return has_notes


def get_share_bed(list_cases):
    share_bed_case_ids = []
    nonEmptyList = []
    for itm in list_cases:
        if itm.bed is not "" and itm.room is not "":
            nonEmptyList.append(itm)
    nonEmptyList.sort(key=operator.attrgetter('bed', 'room'))
    for k, group in itertools.groupby(nonEmptyList, key=lambda x: (x.bed, x.room)):
        lst = list(group)
        length = len(lst)
        if length > 1:
            for item in lst:
                share_bed_case_ids.append(item.case_id)
    return share_bed_case_ids


def update_active_dormant_status_esquery(es_conn, relos_index):
    q = Q(
        "bool",
        must_not=[
            Q("exists", field="date_of_discharge")
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_index) \
        .doc_type(cs_model.Relos) \
        .query(q) \
        .source(['case_id', 'room', 'bed', 'date_of_admission'])
    return s


# change case_activity_status of cases that are not discharged
def update_active_dormant_status(es_conn, relos_index, patient_dormant_day, note_dormant_day,
                                 TIME_FORMAT, note_index):
    """Returns an iterator of CaseInfo objects for cases which are not discharged."""
    es_search = update_active_dormant_status_esquery(es_conn, relos_index)
    # if s.count() == 0:
    #     return 0
    count = 0
    for _ in es_search.scan():
        count = count + 1

    if count == 0:
        return

    list_cases = []
    actions = []
    curr_runtime = dt.datetime.now()
    service_date = curr_runtime.strftime(TIME_FORMAT)
    for res in es_search.scan():
        # dao = dt.datetime.strptime(res.date_of_admission, "%m/%d/%y %H:%M:%S")
        dao = dt.datetime.strptime(res.date_of_admission, "%Y-%m-%d %H:%M:%S")
        los = (curr_runtime - dao).days
        prolonged_los = (los > patient_dormant_day)
        note_dormant_day = (curr_runtime - dt.timedelta(days=note_dormant_day)).strftime(TIME_FORMAT)
        has_notes = get_has_note(es_conn, res.meta.id, note_dormant_day, note_index)
        if prolonged_los & has_notes is False:
            case_activity_status = "Dormant"
        else:
            case_activity_status = "Active"
        list_cases.append \
                (CaseInfo(
                case_id=res.meta.id,
                room=res.room,
                bed=res.bed,
                date_of_admission=dao,
                case_activity_status=case_activity_status,
                los=los,
                prolonged_los=prolonged_los,
                future_admission=dao > curr_runtime,
                has_notes=has_notes
                # share_bed=share_bed
            ))
    share_bed_case_ids = get_share_bed(list_cases)
    for item in list_cases:
        if item.case_id in share_bed_case_ids:
            item.share_bed = True
            if item.has_notes is False:
                item.case_activity_status = "Dormant"
            else:
                item.case_activity_status = "Active"

        action = {
            "_id": item.case_id,
            "_index": relos_index,
            "_op_type": 'update',
            "_type": cs_model.Relos,
            "_source": {
                "doc": {
                    "length_of_stay": item.los,
                    "current_hours_of_stay": item.los,
                    "case_activity_status": item.case_activity_status,
                    "service_date": service_date
                }
            }
        }
        actions.append(action)
    return actions


def update_discharged_status_esquery(es_conn, relos_index):
    q = Q(
        "bool",
        must=[
            Q('exists', field="date_of_discharge")
        ],
        must_not=[
            Q('term', case_activity_status__keyword="Discharged")
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_index) \
        .doc_type(cs_model.Relos) \
        .query(q) \
        .source(['case_id', 'date_of_admission', 'date_of_discharge'])
    return s


# change case_activity_status of cases that are discharged
def update_discharged_status(es_conn, relos_index, TIME_FORMAT, actions):
    curr_runtime = dt.datetime.now()
    es_search = update_discharged_status_esquery(es_conn, relos_index)
    if es_search.count() == 0:
        return

    list_cases = []

    service_date = (curr_runtime - dt.timedelta(hours=1)).strftime(TIME_FORMAT)
    for res in es_search.scan():
        case_activity_status = "Discharged"
        doa = dt.datetime.strptime(res.date_of_admission, "%Y-%m-%d %H:%M:%S")
        dod = dt.datetime.strptime(res.date_of_discharge, "%Y-%m-%d %H:%M:%S")
        los = (dod - doa).days

        list_cases.append \
                (CaseInfo(
                case_id=res.meta.id,
                date_of_admission=doa,
                case_activity_status=case_activity_status,
                los=los,
                date_of_discharge=dod
            ))
    for item in list_cases:
        action = {
            "_id": item.case_id,
            "_index": relos_index,
            "_op_type": 'update',
            "_type": cs_model.Relos,
            "_source": {
                "doc": {
                    "length_of_stay": item.los,
                    "current_hours_of_stay": item.los,
                    "case_activity_status": item.case_activity_status,
                    "service_date": service_date
                }
            }
        }
        actions.append(action)
    return actions

import time
import pytest
from elasticsearch import helpers
from elasticsearch_dsl import Index
from pytest_elasticsearch import factories
from case_activity_status_update import models as al_models
from tests.helpers import utils as tutils


elasticsearch_nooproc = factories.elasticsearch_noproc(port=9200)
elasticsearch_proc = factories.elasticsearch('elasticsearch_nooproc')


@pytest.fixture
def relos_index(elasticsearch_proc):
    yield elasticsearch_proc.indices.create("relos")


@pytest.fixture
def note_index(elasticsearch_proc):
    yield elasticsearch_proc.indices.create("note")


@pytest.fixture
def relos_data(relos_index, elasticsearch_proc):
    # 'case_id', 'bed', 'room', 'date_of_admission', 'date_of_discharge', 'case_activity_status'
    data = [
        ("CID_1", "B_1", "R_1", "2020-04-02 07:49:02", "", "Active"),
        ("CID_2", "B_3", "R_4", "2020-04-04 22:33:40", "2020-04-08 22:33:40", "Discharged"),
        ("CID_3", "B_3", "R_2", "2020-04-02 07:52:27", "", "Dormant"),
        ("CID_4", "B_5", "R_3", "2020-04-06 08:43:37", "", "Active"),
        ("CID_5", "B_2", "R_4", "2020-04-02 13:08:41", "", "Dormant"),
        ("CID_6", "B_7", "R_1", "2020-04-04 07:49:02", "2020-04-20 22:33:40", ""),
        ("CID_7", "B_9", "R_4", "2020-04-04 22:33:40", "", "Active"),
        ("CID_8", "B_2", "R_2", "2020-04-02 07:52:27", "", "Dormant"),
        ("CID_9", "B_4", "R_3", "2020-04-06 08:43:37", "2020-04-21 07:52:27", "Discharged"),
        ("CID_10", "B_6", "R_4", "2020-04-02 13:08:41", "2020-04-10 13:08:41", "Discharged")
    ]
    index = Index("relos")
    index.document(al_models.Relos)
    _actions = (
        n.to_dict(True) for n in (
            al_models.Relos(
                case_id=i[0], bed=i[1], room=i[2], date_of_admission=tutils.parse_dt(i[3]),
                date_of_discharge=tutils.parse_dt(i[4]), case_activity_status=i[5]
            ) for i in data
        ))
    result = helpers.bulk(elasticsearch_proc, _actions)

    time.sleep(2)
    yield result


@pytest.fixture
def note_data(note_index, elasticsearch_proc):
    # case_id, modified_date, has_note
    data = [
        ("CID_1", "2020-04-02 07:49:02", True),
        ("CID_2", "2020-03-10 07:52:27", False),
        ("CID_3", "2020-04-06 08:43:37", True),
        ("CID_4", "2020-04-14 07:49:02", False),
        ("CID_5", "2020-03-16 08:43:37", False),
        ("CID_6", "2020-03-21 07:49:02", True),
        ("CID_7", "2020-04-01 07:52:27", False),
        ("CID_8", "2020-04-08 08:43:37", True),
        ("CID_9", "2020-04-10 07:49:02", False),
        ("CID_10", "2020-04-02 08:43:37", False)

    ]
    index = Index("note")
    index.document(al_models.Note)
    _actions = (
        n.to_dict(True) for n in (
            al_models.Note(
                case_id=i[0], modified_date=tutils.parse_dt(i[1]), has_note=i[2]
            ) for i in data
        ))
    result = helpers.bulk(elasticsearch_proc, _actions)

    time.sleep(2)
    yield result

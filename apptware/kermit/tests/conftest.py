import time
import pytest
from elasticsearch import helpers
from elasticsearch_dsl import Index
from pytest_elasticsearch import factories
from kermit import models as al_models
from tests.helpers import utils as tutils


elasticsearch_nooproc = factories.elasticsearch_noproc(port=9200)
elasticsearch_proc = factories.elasticsearch('elasticsearch_nooproc')


@pytest.fixture
def relos_index(elasticsearch_proc):
    yield elasticsearch_proc.indices.create("relos")


@pytest.fixture
def ann_index(elasticsearch_proc):
    yield elasticsearch_proc.indices.create("ann")



@pytest.fixture
def relos_data(relos_index, elasticsearch_proc):
    # case_id, hospital_id, service_date, date_of_discharge, latest_review_start_time, latest_review_status
    data = [
        ("CID_1", "HP_1", "2020-04-02 07:49:02",
         "", "2020-04-02 07:49:02", "review"),
        ("CID_2", "HP_4", "2020-04-04 22:33:40",
         "", "2020-04-04 22:33:40", "audit"),
        ("CID_3", "HP_2", "2020-04-02 07:52:27",
         "2020-04-03 16:19:38", "2020-04-02 07:52:27", "submit"),
        ("CID_4", "HP_3", "2020-04-06 08:43:37",
         "", "2020-04-06 08:43:37", "audit"),
        ("CID_5", "HP_4", "2020-04-02 13:08:41",
         "2020-04-06 08:43:37", "2020-04-02 13:08:41", "submit"),
        ("CID_6", "HP_1", "2020-04-04 07:49:02",
         "2020-04-04 22:33:40", "2020-04-03 07:49:02", "review"),
        ("CID_7", "HP_4", "2020-04-04 22:33:40",
         "", "2020-04-04 22:33:40", "dismiss"),
        ("CID_8", "HP_2", "2020-04-02 07:52:27",
         "", "2020-04-02 07:52:27", "dismiss"),
        ("CID_9", "HP_3", "2020-04-06 08:43:37",
         "2020-04-07 07:52:27", "2020-04-06 08:43:37", "dismiss"),
        ("CID_10", "HP_4", "2020-04-02 13:08:41",
         "", "2020-04-02 13:08:41", "submit")
    ]
    index = Index("relos")
    index.document(al_models.Relos)
    _actions = (
        n.to_dict(True) for n in (
            al_models.Relos(
                case_id=i[0], hospital=i[1], service_date=tutils.parse_dt(
                    i[2]),
                date_of_discharge=tutils.parse_dt(i[3]),
                latest_review_start_time=tutils.parse_dt(i[4]),
                latest_review_status=i[5]
            ) for i in data
        ))
    result = helpers.bulk(elasticsearch_proc, _actions)

    time.sleep(2)
    yield result


@pytest.fixture
def ann_data(ann_index, elasticsearch_proc):
    # case_id, ann_id, snippet_label, note_type, note_date, kermit_probability, similarity_group, kermit_label
    data = [
        ("CID_1", "CID_1_ANN_1", "SL_1", "NT_1", "2020-04-02 07:49:02", 0.1, 1, "KL_1"),
        ("CID_1", "CID_1_ANN_2", "SL_2", "NT_2", "2020-04-01 07:52:27", 0.2, 3, "KL_1"),
        ("CID_1", "CID_1_ANN_3", "SL_3", "NT_1", "2020-04-06 08:43:37", 0.4, 2, "KL_3"),
        ("CID_1", "CID_1_ANN_4", "SL_2", "NT_3", "2020-04-04 07:49:02", 0.6, 2, "KL_2"),
        ("CID_1", "CID_1_ANN_5", "SL_1", "NT_4", "2020-04-06 08:43:37", 0.8, 1, "KL_3"),
        ("CID_2", "CID_2_ANN_1", "SL_3", "NT_4", "2020-04-01 07:49:02", 0.1, 1, "KL_1"),
        ("CID_2", "CID_2_ANN_2", "SL_2", "NT_5", "2020-04-01 07:52:27", 0.2, 3, "KL_1"),
        ("CID_2", "CID_2_ANN_3", "SL_1", "NT_3", "2020-04-03 08:43:37", 0.4, 2, "KL_3"),
        ("CID_2", "CID_2_ANN_4", "SL_3", "NT_3", "2020-04-02 07:49:02", 0.6, 2, "KL_2"),
        ("CID_2", "CID_2_ANN_5", "SL_2", "NT_1", "2020-04-02 08:43:37", 0.8, 1, "KL_3"),

    ]
    index = Index("ann")
    index.document(al_models.Ann)
    _actions = (
        n.to_dict(True) for n in (
            al_models.Ann(
                case_id=i[0], ann_id=i[1], snippet_label=i[2], note_type=i[3],
                note_date=tutils.parse_dt(i[4]), kermit_probability=i[5],
                similarity_group=i[6], kermit_label=i[7]
            ) for i in data
        ))
    result = helpers.bulk(elasticsearch_proc, _actions)

    time.sleep(2)
    yield result

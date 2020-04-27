import time

from note_preprocessor import es
import pytest
from pytest_elasticsearch import factories
from elasticsearch_dsl import Search


elasticsearch_nooproc = factories.elasticsearch_noproc(port=9200)
elasticsearch_proc = factories.elasticsearch('elasticsearch_nooproc')

TEST_INDEX_NAME = "noteindex"

def get_notes(note_data):
    yield es.Note(**note_data)


@pytest.fixture(autouse=True)
def note_index(elasticsearch_proc):
    elasticsearch_proc.indices.create(index=TEST_INDEX_NAME)


@pytest.mark.parametrize(
    "note_data",
    [
        {"case_id": "cid_1", "de_id": False, "note_id": "NID_1", "note_date": "2021-04-30 05:34:33", "text": "text1"},
        {"case_id": "cid_2", "de_id": True, "note_id": "NID_2", "sentence_offsets": [1,5], "text": "• point one \n • point two"},
        {"case_id": "cid_3", "de_id": True, "note_id": "NID_3", "patient_id": "PID_3", "note_date": "2021-02-30 15:04:33", "note_provider_name": ["ABC", "DEF"]},
        {"case_id": "cid_4", "patient_id": "PID_4", "note_id": "NID_4"},
    ]
)
def test_index_notes(note_data, note_index, elasticsearch_proc):
    equery = Search(using=elasticsearch_proc, index=TEST_INDEX_NAME).query("match_all")

    es.index_notes(
        elasticsearch_proc,
        get_notes(note_data),
        TEST_INDEX_NAME
    )

    time.sleep(1)  # Because writes are lazy unless explicit with "wait_for" flag

    # Test that doc added
    assert equery.count() == 1
    results = equery[0:1].execute()
    hit = results[0]

    # Test that doc_id updated
    assert hit.meta.id == "{case_id}_{note_id}".format(**note_data)

    # Test that all data in note_data exists in the document created on ES
    _result = hit.to_dict()
    assert all( note_data[k]==_result[k] for k in note_data )

    # Test that start_date and end_date get set on the doc from note.to_dict
    assert "add_date" in _result
    assert "update_date" in _result
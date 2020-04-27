from dataclasses import dataclass

import pytest
from case_activity_status_update import utils as al_utils
from tests.helpers import utils as tutils


@dataclass
class TestCaseInfo:
    case_id: str
    room: str
    bed: str


@pytest.fixture
def case_info_fix(request):
    # ((case_id, ann_id, kermit_probability, similarity_group), output_sinfo)
    return ((
                TestCaseInfo(
                    case_id=item[0],
                    room=item[1],
                    bed=item[2]
                ) for item in request.param[0]), request.param[1])


@pytest.mark.parametrize(
    "case_id, dormant_time, p_has_notes",
    [
        ("CID_1", "2020-04-01 07:49:02", True),
        ("CID_5", "2020-03-16 08:43:37", False),
        ("CID_2", "2020-03-10 07:52:27", False)
    ]
)
def test_get_has_note(case_id, dormant_time, note_index, p_has_notes, elasticsearch_proc):
    # config = configuration.get("is_local")
    has_notes = al_utils.get_has_note(
        case_id=case_id,
        note_index="note",
        dormant_time=dormant_time,
        es_conn=elasticsearch_proc
    )
    assert (p_has_notes == has_notes)


@pytest.mark.parametrize(
    "case_info_fix",
    [
        (
                [
                    ("CID_1", "B_1", "R_1"),
                    ("CID_2", "B_1", "R_1"),
                    ("CID_3", "B_2", "R_3"),
                    ("CID_4", "B_4", "R_2"),
                ],
                ["CID_1", "CID_2"]
        ),
        (
                [
                    ("CID_1", "B_1", "R_1"),
                    ("CID_2", "B_3", "R_1"),
                    ("CID_3", "B_2", "R_3"),
                    ("CID_4", "B_4", "R_2"),
                ],
                []
        )
    ],
    indirect=True
)
def test_get_share_bed(case_info_fix):
    input_iter, output_sinfo = case_info_fix
    res = al_utils.get_share_bed(input_iter)

    assert len(res) == len(output_sinfo)
    assert all(i in res for i in output_sinfo)


@pytest.mark.parametrize(
    "relos_index, output_count",
    [
        ("relos", 6)
        # ("2020-04-02 00:00:00", "2020-04-03 00:00:00", 1),
        # ("2020-04-03 00:00:00", "2020-04-04 00:00:00", 0),
        # ("2020-04-04 00:00:00", "2020-04-05 00:00:00", 0)
    ]
)
def test_update_active_dormant_status_esquery(relos_data, output_count, elasticsearch_proc):
    relos_index = "relos"
    qry_res = al_utils.update_active_dormant_status_esquery \
        (es_conn=elasticsearch_proc,
         relos_index=relos_index)
    ocount = qry_res.count()
    assert output_count == ocount


@pytest.mark.parametrize(
    "relos_index, output_count",
    [
        ("relos", 1),
        # ("2020-04-02 00:00:00", "2020-04-03 00:00:00", 1)
        # ("2020-04-03 00:00:00", "2020-04-04 00:00:00", 0),
        # ("2020-04-04 00:00:00", "2020-04-05 00:00:00", 0)
    ]
)
def test_update_discharged_status_esquery(relos_data, output_count, elasticsearch_proc):
    relos_index = "relos"
    qry_res = al_utils.update_discharged_status_esquery \
        (es_conn=elasticsearch_proc,
         relos_index=relos_index)
    count = qry_res.count()
    assert output_count == count

# @pytest.fixture(
#     "list_cases", "list_case_ids",
#     [
#         ([TestCaseInfo(case_id="CID_1", room="R_1", bed="B_1"),
#          TestCaseInfo(case_id="CID_2", room="R_2", bed="B_2"),
#          TestCaseInfo(case_id="CID_3", room="R_1", bed="B_1")],
#         ["CID_1", "CID_3"])
#     ]
# )
# def test_get_share_bed(list_cases, list_case_ids):
#     res_list_case_ids = al_utils.get_share_bed(list_cases)
#     assert len(res_list_case_ids) == len(list_case_ids)
#     assert all(i in res_list_case_ids for i in list_case_ids)

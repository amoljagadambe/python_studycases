import pytest

from elasticsearch_dsl import Search

from active_learner import utils as al_utils
from active_learner.models import RelosAnn
from tests.helpers import utils as tutils


@pytest.fixture
def snippet_info_fix(request):
    # ((case_id, ann_id, kermit_probability, similarity_group), output_sinfo)
    return ((
        al_utils.CaseSnippetInfo(
            case_id=item[0],
            ann_id=item[1],
            kermit_probability=item[2],
            similarity_group=item[3]
        ) for item in request.param[0]), request.param[1])


@pytest.mark.parametrize(
    "hospital_codes,from_date,to_date,output_id_list",
    [
        (["HP_1", "HP_3", "HP_4", "HP_2"], "2020-03-01 00:00:00",
         "2020-05-03 00:00:00", ["CID_1", "CID_2", "CID_4", "CID_10"]),
        (["HP_1"], "2020-03-01 00:00:00", "2020-05-03 00:00:00", ["CID_1"]),
        (["HP_4"], "2020-03-01 00:00:00",
         "2020-05-03 00:00:00", ["CID_2", "CID_10"]),
        (["HP_1", "HP_4", ], "2020-04-01 00:00:00",
         "2020-04-04 00:00:00", ["CID_1", "CID_10"]),
        (["HP_1", "HP_3", "HP_2"], "2021-05-01 00:00:00", "2021-05-03 00:00:00", []),
    ]
)
def test_get_all_non_discharge_cases_iter(hospital_codes, from_date, to_date, output_id_list, relos_data, elasticsearch_proc):
    from_date_obj = tutils.parse_dt(from_date)
    to_date_obj = tutils.parse_dt(to_date)
    output_iter = al_utils.get_all_non_discharge_cases_iter(
        es_conn=elasticsearch_proc,
        hospital_codes=hospital_codes,
        relos_index="relos",
        from_date_obj=from_date_obj,
        to_date_obj=to_date_obj
    )
    output_list = [item.case_id for item in output_iter]
    assert len(output_id_list) == len(output_list)
    assert all(i in output_list for i in output_id_list)


@pytest.mark.parametrize(
    "from_date,output_id_list",
    [
        ("2020-04-01 00:00:00", ["CID_1", "CID_6"]),
        ("2020-04-02 00:00:00", ["CID_1", "CID_6"]),
        ("2020-04-03 00:00:00", ["CID_6"]),
        ("2020-04-04 00:00:00", [])
    ]
)
def test_get_cases_under_review(from_date, output_id_list, relos_data, elasticsearch_proc):
    from_date_obj = tutils.parse_dt(from_date)
    output_list = al_utils.get_cases_under_review(
        es_conn=elasticsearch_proc,
        relos_index="relos",
        from_date_obj=from_date_obj,
    )
    assert len(output_id_list) == len(output_list)
    assert all(i in output_list for i in output_id_list)


@pytest.mark.parametrize(
    "from_date,to_date,output_count",
    [
        ("2020-04-01 00:00:00", "2020-04-02 00:00:00", 1),
        ("2020-04-02 00:00:00", "2020-04-03 00:00:00", 1),
        ("2020-04-03 00:00:00", "2020-04-04 00:00:00", 0),
        ("2020-04-04 00:00:00", "2020-04-05 00:00:00", 0)
    ]
)
def test_get_submitted_in_relos_ann_sobj(from_date, to_date, output_count, relos_ann_data, elasticsearch_proc):
    from_date_obj = tutils.parse_dt(from_date)
    to_date_obj = tutils.parse_dt(to_date)
    output_sobj = al_utils.get_submitted_in_relos_ann_sobj(
        es_conn=elasticsearch_proc,
        relos_ann_index="relos-ann",
        from_date_obj=from_date_obj,
        to_date_obj=to_date_obj
    )
    ocount = output_sobj.count()

    assert output_count == ocount


@pytest.mark.parametrize(
    "snippet_info_fix",
    [
        (
            [
                ("CID_1", "CID_1_ANN_1", 0.2, 1),
                ("CID_1", "CID_1_ANN_2", 0.3, 2),
                ("CID_1", "CID_1_ANN_3", 0.6, 4),
                ("CID_1", "CID_1_ANN_5", 0.3, 1),
            ],
            ["CID_1_ANN_1", "CID_1_ANN_2", "CID_1_ANN_3", "CID_1_ANN_5"]
        ),
        (
            [
                ("CID_1", "CID_1_ANN_1", 0.2, 1),
                ("CID_1", "CID_1_ANN_2", 0.3, 2),
                ("CID_1", "CID_1_ANN_3", 0.6, 2),
            ],
            ["CID_1_ANN_1", "CID_1_ANN_3"]
        ),
        (
            # Does not depend on case_id
            [
                ("CID_1", "CID_1_ANN_1", 0.2, 1),
                ("CID_2", "CID_2_ANN_2", 0.3, 2),
                ("CID_3", "CID_3_ANN_3", 0.6, 2),
            ],
            ["CID_1_ANN_1", "CID_3_ANN_3"]
        )
    ],
    indirect=True
)
def test_get_representative_snippet_for_each_similarity_group_iter(snippet_info_fix):
    input_iter, output_sinfo = snippet_info_fix
    op = al_utils.get_representative_snippet_for_each_similarity_group_iter(
        sinfo_iter=input_iter)
    op_ann_ids = [item.ann_id for item in op]

    assert len(op_ann_ids) == len(output_sinfo)
    assert all(i in op_ann_ids for i in output_sinfo)


@pytest.mark.parametrize(
    "review_action,exp_output_list",
    [
        ("submit", ["CID_3", "CID_5"]),
        ("dismiss", ["CID_1"]),
        ("no decision", ["CID_6", "CID_9"])
    ]
)
def test_get_case_info_from_relos_ann_sobj_iter(review_action, exp_output_list, relos_ann_data, elasticsearch_proc):
    s = Search(using=elasticsearch_proc) \
        .index("relos-ann") \
        .doc_type(RelosAnn) \
        .filter("term", review_action__keyword=review_action) \
        .source(["case_id", "review_action_time"])
    oiter = al_utils.get_case_info_from_relos_ann_sobj_iter(sobj=s)
    op_cid_list = [item.case_id for item in oiter]

    assert len(op_cid_list) == len(exp_output_list)
    assert all(i in op_cid_list for i in exp_output_list)


@pytest.mark.parametrize(
    "case_infod,from_date,primary_note_types,event_candidates,exp_output_list",
    [
        (
            ("CID_1", "2020-04-01 00:00:00"),
            "2020-04-01 00:00:00",
            ["NT_1", "NT_2", "NT_5"], ["SL_1", "SL_2", "SL_3"],
            ["CID_1_ANN_1", "CID_1_ANN_2", "CID_1_ANN_3"]
        ),
        (
            ("CID_1", "2020-04-02 00:00:00"),
            "2020-04-01 00:00:00",
            ["NT_1", "NT_2"], ["SL_1", "SL_2", "SL_3"],
            ["CID_1_ANN_1", "CID_1_ANN_3"]
        ),
        (
            ("CID_2", "2020-04-01 00:00:00"),
            "2020-04-01 00:00:00",
            ["NT_1", "NT_2", "NT_5"], ["SL_1", "SL_2", "SL_3"],
            ["CID_2_ANN_2", "CID_2_ANN_5"]
        ),
        (
            ("CID_2", "2020-04-02 00:00:00"),
            "2020-04-01 00:00:00",
            ["NT_1", "NT_2"], ["SL_1", "SL_2", "SL_3"],
            ["CID_2_ANN_5"]
        ),
    ]
)
def test_get_snippet_info_for_case_info_iter(case_infod, from_date, primary_note_types, event_candidates, exp_output_list, ann_data, elasticsearch_proc):
    from_date_obj = tutils.parse_dt(from_date)
    output_iter = al_utils.get_snippet_info_for_case_info_iter(
        case_info=al_utils.CaseInfo(
            case_id=case_infod[0], review_action_time=tutils.parse_dt(case_infod[1])),
        from_date_obj=from_date_obj,
        es_conn=elasticsearch_proc,
        ann_index="ann",
        primary_note_types=primary_note_types,
        event_candidates=event_candidates
    )

    op_ann_ids = [item.ann_id for item in output_iter]
    assert len(op_ann_ids) == len(exp_output_list)
    assert all(i in op_ann_ids for i in exp_output_list)


@pytest.mark.parametrize(
    "hospital_codes,from_date,to_date,output_id_list",
    [
        (["HP_1", "HP_3", "HP_4", "HP_2"], "2020-03-01 00:00:00",
         "2020-05-03 00:00:00", ["CID_3", "CID_1", "CID_5", "CID_2"]),
        (["HP_1"], "2020-03-01 00:00:00",
         "2020-05-03 00:00:00", ["CID_3", "CID_1"]),
        (["HP_4"], "2020-03-01 00:00:00",
         "2020-05-03 00:00:00", ["CID_3", "CID_2", "CID_5", "CID_10"]),
        (["HP_1", "HP_4", ], "2020-04-01 00:00:00",
         "2020-04-04 00:00:00", ["CID_3", "CID_1", "CID_5", "CID_10"]),
        (["HP_1", "HP_3", "HP_2"], "2021-05-01 00:00:00", "2021-05-03 00:00:00", []),
    ]
)
def test_get_case_last_decision_iter(hospital_codes, from_date, to_date, output_id_list, relos_data, relos_ann_data, elasticsearch_proc):
    from_date_obj = tutils.parse_dt(from_date)
    to_date_obj = tutils.parse_dt(to_date)
    output_iter = al_utils.get_case_last_decision_iter(
        es_conn=elasticsearch_proc,
        hospital_codes=hospital_codes,
        relos_index="relos",
        relos_ann_index="relos-ann",
        from_date_obj=from_date_obj,
        to_date_obj=to_date_obj
    )
    output_list = [item.case_id for item in output_iter]

    assert len(output_id_list) == len(output_list)
    assert all(i in output_list for i in output_id_list)

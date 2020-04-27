import pytest
from kermit import utils as al_utils
from tests.helpers import utils as tutils


@pytest.mark.parametrize(
    "from_date, to_date,hospital_codes, output_id_list",
    [
        ("2020-04-02 00:00:00", "2020-04-03  08:43:37",
         ["HP_1", "HP_4", "HP_2"], ['CID_1', 'CID_8', 'CID_10']),
        ("2020-04-04 00:00:00", "2020-04-05  14:43:37",
         ["HP_4"], ['CID_2', 'CID_7']),
        ("2020-04-06 00:00:00", "2020-04-07  08:43:37",
         ["HP_3", "HP_6"], ['CID_4']),
        ("2020-04-10 12:45:23", "2020-04-15  08:43:37",
         ["HP_1", "HP_4", "HP_2"], [])
    ]
)
def test_get_adm_disch_data_genrater(from_date, to_date, hospital_codes, output_id_list, relos_data,
                                     elasticsearch_proc):
    # config = configuration.get("is_local")
    from_date_obj = tutils.parse_dt(from_date)
    to_date_obj = tutils.parse_dt(to_date)
    output_iter = al_utils.get_adm_disch_data_genrater(
        hospital_codes=hospital_codes,
        relos_index="relos",
        from_date_obj=from_date_obj,
        to_date_obj=to_date_obj,
        es_conn=elasticsearch_proc
    )
    op_ann_ids = [item.case_id for item in output_iter]
    assert len(op_ann_ids) == len(output_id_list)
    assert all(i in op_ann_ids for i in output_id_list)


@pytest.mark.parametrize(
    "from_date, output_id_list",
    [
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
    "from_date, to_date, note_types, event_candidates_by_group, output_id_list",
    [

        (
                "2020-04-02 07:49:02", "2020-04-02 07:49:02", ["NT_1", "NT_3"], ["SL_1", "SL_3"], ["CID_1", "CID_2"]
        ),
        (
                "2020-04-02 07:49:02", "2020-04-02 07:49:02", ["NT_1"], ["SL_1"], ["CID_1"]
        ),
        (
                "2020-04-01 07:49:02", "2020-04-01 07:49:02", ["NT_4"], ["SL_3"], ["CID_2"]
        )
    ]
)
def test_get_ann_data_from_ann_genrater(from_date, to_date, note_types, event_candidates_by_group, output_id_list,
                                        ann_data,
                                        elasticsearch_proc):
    from_date_obj = tutils.parse_dt(from_date)
    to_date_obj = tutils.parse_dt(to_date)
    output_iter = al_utils.get_ann_data_from_ann_genrater(
        note_types=note_types,
        event_candidates_by_group=event_candidates_by_group,
        ann_index="ann",
        from_date_obj=from_date_obj,
        to_date_obj=to_date_obj,
        es_conn=elasticsearch_proc
    )

    op_ann_ids = [item.case_id for item in output_iter]
    assert len(op_ann_ids) == len(output_id_list)
    assert all(i in op_ann_ids for i in output_id_list)

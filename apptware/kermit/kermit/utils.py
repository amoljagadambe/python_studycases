import datetime
from dataclasses import asdict
import itertools
from elasticsearch_dsl import Search, Q
from kermit import models as k_models
from kermit import kermit_model_eval as kermit_eval
from elasticsearch import helpers
from time import localtime, strftime
from kermit.store_class import CaseInfo, CaseNoteInfo
import scipy as sp


def imerge(a, b):
    for i, j in zip(a, b):
        yield i
        yield j


def get_dict(merge: object):
    known_keys = []
    list_iter = []
    for key, group in merge:
        # print(list(group))
        for data in group:
            if key in known_keys:
                list_iter.append(asdict(data))
            else:
                known_keys.append(key)
                list_iter.append(asdict(data))

    return list_iter


def get_adm_disch_data_genrater(hospital_codes, relos_index, from_date_obj, to_date_obj, es_conn):
    q = Q(
        "bool",
        must=[
            Q("terms", hospital__keyword=hospital_codes),
            Q('range', service_date={"gte": from_date_obj, "lte": to_date_obj})
        ],
        must_not=[
            Q("exists", field="date_of_discharge")
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_index) \
        .doc_type(k_models.Relos) \
        .query(q) \
        .source(['case_id', 'date_of_admission'])

    for res in s.scan():
        yield CaseInfo(
            case_id=res.meta.id,
            date_of_admission=res.date_of_admission
        )


def get_ann_data_from_ann_genrater(note_types, event_candidates_by_group, ann_index, from_date_obj, to_date_obj, es_conn):
    q = Q(
        "bool",
        must=[
            Q("terms", snippet_label__keyword=event_candidates_by_group),
            Q("terms", note_type__keyword=note_types),
            Q('range', note_date={"gte": from_date_obj, "lte": to_date_obj})
        ])

    s = Search(using=es_conn) \
        .index(ann_index) \
        .doc_type(k_models.Ann) \
        .query(q) \
        .source(['case_id', 'note_type', 'user_response_type', 'note_text', 'last_modified_by'])

    for res in s.scan():
        if hasattr(res, 'last_modified_by'):
            yield CaseNoteInfo(
                case_id=res.case_id,
                note_type=res.note_type,
                user_response_type=res.user_response_type,
                note_text=res.note_text,
                last_modified_by=res.last_modified_by
            )
        else:
            yield CaseNoteInfo(
                case_id=res.case_id,
                note_type=res.note_type,
                user_response_type=res.user_response_type

            )


def get_ann_contents_genrater(hospital_codes, relos_index, note_types, event_candidates_by_group, ann_index, es_conn, from_date: datetime.datetime, to_date: datetime):
    ann_index_value_iter = get_ann_data_from_ann_genrater(note_types, event_candidates_by_group, ann_index, from_date, to_date, es_conn)
    doa_value_iter = get_adm_disch_data_genrater(hospital_codes, relos_index, from_date, to_date, es_conn)

    # Group & Merge all_ann_index_vaule_iter and cases_info_with_DOA iter by case_id
    all_ann_index_grouped_by_case_id = itertools.groupby(
        ann_index_value_iter, lambda item: item.case_id)
    all_doa_grouped_by_case_id = itertools.groupby(
        doa_value_iter, lambda item: item.case_id)
    merged_iter = imerge(all_ann_index_grouped_by_case_id,
                         all_doa_grouped_by_case_id)

    merge_dict = get_dict(merged_iter)
    iter_obj_dict = itertools.groupby(merge_dict, lambda item: item['case_id'])
    required_keys = ['case_id', 'note_text', 'last_modified_by', 'note_type', 'user_response_type']
    for key, vaule in iter_obj_dict:
        updated_dict = {}
        for data in vaule:
            updated_dict.update(data)
        final_dict = {your_key: updated_dict[your_key] for your_key in required_keys}
        yield final_dict  # THIS  will  dict with same required_keys


def get_cases_under_review(relos_index, from_date_obj, es_conn):
    """Returns the List of case_ids which are under review from the last 24 hours."""
    q = Q(
        "bool",
        must=[
            Q("term", latest_review_status__keyword="review"),
            Q('range', latest_review_start_time={"gte": from_date_obj})
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_index) \
        .doc_type(k_models.Relos) \
        .query(q) \
        .source(["case_id"])

    cases_under_review = []
    for res in s.scan():
        cases_under_review.append(res.case_id)

    return cases_under_review


def generate_predictions_auto_report_kermit(config, hospital_codes, ann_index, relos_index, event_candidates_by_group,
                                            note_types, es_conn, from_date=None, to_date=None, to_be_indexed="no"):
    curr_date = datetime.datetime.now()

    # Convert the from and to date into datetime format if present, else use current_serv_date and 24 hours prior as
    # prev service_date
    if not to_date:
        to_date = curr_date
    if not from_date:
        from_date = to_date - datetime.timedelta(hours=24)

    dict_generator = get_ann_contents_genrater(hospital_codes, relos_index, note_types, event_candidates_by_group, ann_index, es_conn, from_date, to_date)
    updated_dict_list = kermit_eval.evaluate(dict_generator,
                                             kermit_w2v_path=config.kermit3_w2v_path,
                                             lookup_path=config.kermit3_lookup_path,
                                             model_path=config.kermit3_model_path,
                                             sim_threshold=config.kermit3_sim_threshold,
                                             prob_threshold=config.kermit3_prob_threshold,
                                             max_green=config.kermit3_max_green)

    # if to_be_indexed then index kermit
    if to_be_indexed.lower() == "yes":
        prediction_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        index_name = ann_index
        ann_type = "info"
        update_actions = []
        # Get the list of cases under review
        cases_under_review = get_cases_under_review(relos_index, from_date, es_conn)

        for dict_row in updated_dict_list:
            body = dict()

            if dict_row['case_id'] in cases_under_review:
                print("The case {} is not indexed as it's under review. ".format(dict_row['case_id']))
                continue

            body['ann_id'] = str(dict_row['ann_id'])
            body['prediction_value'] = float(dict_row['prob'])
            body['prediction_rating'] = str(dict_row['green'])
            body['prediction_time'] = prediction_time

            if not body['ann_id']:
                continue

            doc = dict()
            doc['kermit_probability'] = "{0:.2f}".format(body['prediction_value'])
            doc['ActiveLearning_Entropy'] = sp.stats.entropy(
                [body['prediction_value'], (1 - body['prediction_value'])],
                base=2)
            doc['kermit_label'] = 'green' if body['prediction_rating'] == "True" else 'yellow'
            doc['kermit_date'] = curr_date.strftime("%Y-%m-%d %H:%M:%S")
            doc['similarity_group'] = int(dict_row['sim_grp'])

            if dict_row['last_modified_by'] in ['', 'pieces']:
                # Modify only the cases where  lastModifiedBy is not by user.
                doc['user_response_type'] = "relos_relavent" if body['prediction_rating'] == "True" else \
                    "relos_not_relavent"
                doc['last_modified_by'] = "pieces"
                doc['last_modified_date'] = prediction_time

            update_actions.append({
                    "_index": index_name,
                    "_op_type": 'update',
                    "_type": ann_type,
                    "_id": body['ann_id'],
                    "_source": {"doc": doc}
                })
        # Index the snippets from kermit predictions
        success, failure = helpers.bulk(es_conn, update_actions, raise_on_error=False)
        print("Successful: ", success)
        print("Failed: ", failure)


def update_relos_relevancy(es_conn, ann_index, x_hour=24):
    """This is to update the documents' user_response_type field from relos_relevant to relos_non_relevant once the
    snippet's corresponding note is older than a given threshold. This is required to not show the snippets(marked by
    annotators) from the older notes."""

    xhours_date = datetime.datetime.now() - datetime.timedelta(hours=x_hour)
    q = Q(
        "bool",
        must=[
            Q("terms", user_response_type="relos_relavent"),
            Q('range', note_date={"lte": xhours_date.strftime("%Y-%m-%d %H:%M:%S")})
        ])

    s = Search(using=es_conn) \
        .index(ann_index) \
        .doc_type(k_models.Ann) \
        .query(q) \
        .source([])

    ann_list = ({
        "_index": ann_index,
        "_op_type": 'update',
        "_type": k_models.Ann,
        "_id": res.case_id,
        "_source": {"doc": {
            "kermit_label": "yellow",
            "user_response_type": "relos_not_relavent",
            "last_modified_by": "pieces"
        }
        }
    } for res in s.scan())

    success, failure = helpers.bulk(es_conn, ann_list, stats_only=True, raise_on_error=False)

    print("Successful: ", success)
    print("Failed: ", failure)

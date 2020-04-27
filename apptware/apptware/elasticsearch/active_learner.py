#!/usr/bin/python

"""This program computes whether a case is to be sent to audit or work list along with storing the
model evaluation metrics into the corresponding index.
The cases are processed from kermit output and this would need to be run after the mainIndexer
is done indexing into relos index.
The threshold to decide whether to mark them as audit/work list is configurable."""

import imp
import sys
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import os
import datetime
from application.resources.elasticsearch import global_index_utils as gb_utils
from application.resources.elasticsearch import elastic_search_generator as esg
import scipy.stats as sp_stats



def get_case_last_decision_list(es, config, from_date_obj, to_date_obj):
    """Returns the cases which are not discharged. The entropy is then re-calculated and updated for the cases in
    this list."""

    case_id_list = []

    all_non_discharge_search_params = {
        'es_object': es,
        'search_index': config.relos_index,
        'scroll_time': '10m',
        'query_body': {
            "query": {
                "bool": {
                    "must_not": [{
                        "exists": {
                            "field": "date_of_discharge"
                        }
                    },
                        #Ignoring the cases which have been marked dismissed by auto_dismisser
                        {
                            "term": {
                                "latest_review_status": 'dismiss'
                            }
                        }],
                    "must": [{
                        "terms": {
                            "hospital": config.hospital_codes
                        }
                    },
                        {
                            "range": {
                                "service_date": {
                                    "gte": datetime.datetime.strftime(from_date_obj, "%Y-%m-%d %H:%M:%S"),
                                    "lte": datetime.datetime.strftime(to_date_obj, "%Y-%m-%d %H:%M:%S")
                                }
                            }
                        }],
                }
            },
            "_source": []
        },
        'page_size': 50,
        'doc_type': config.relos_index_type,
        'timeout': 60,
        'upto_count': -1
    }

    for res in esg.es_search_generator(**all_non_discharge_search_params):
        case_id_list.append(res["_id"])

    relos_df = pd.DataFrame()
    relos_df['case_id'] = case_id_list
    relos_df['review_action_time'] = pd.NaT

    relos_ann_query = {
        "query": {
            "bool": {
                "must": [
                    {

                        "term": {
                            "review_action": "submit"
                        }

                    },
                    {
                        "range": {
                            "review_action_time": {
                                "gte": datetime.datetime.strftime(from_date_obj, "%Y-%m-%d %H:%M:%S"),
                                "lte": datetime.datetime.strftime(to_date_obj, "%Y-%m-%d %H:%M:%S")
                            }
                        }
                    }]
            }
        },
        "_source": ['case_id', 'review_action_time']
    }

    search_params = {
        'es_object': es,
        'search_index': config.relos_ann_index,
        'scroll_time': '10m',
        'query_body': relos_ann_query,
        'page_size': 50,
        'doc_type': config.relos_ann_index_type,
        'timeout': 60,
        'upto_count': -1
    }

    submit_cases_dicts = []
    for res in esg.es_search_generator(**search_params):
        submit_cases_dicts.append(res['_source'])

    submit_cases_df = pd.DataFrame(submit_cases_dicts)

    # If not reviewed in last 24 hours
    if len(submit_cases_df) == 0:
        return relos_df
    if 'review_action_time' not in submit_cases_df.columns:
        submit_cases_df['review_action_time'] = pd.NaT
    submit_cases_df['review_action_time'] = pd.to_datetime(submit_cases_df['review_action_time'])

    res_df = pd.merge(submit_cases_df, relos_df, on=['case_id'], how='outer')\
        .drop('review_action_time_y', axis=1)\
        .rename(columns={'review_action_time_x': 'review_action_time'})

    res_df = res_df.groupby('case_id').max().reset_index()
    res_df['review_action_time'] = pd.to_datetime(res_df['review_action_time'])

    return res_df


def compute_case_consideration_time(case_decision_time_df, from_date_obj):
    """Computes the time from which each case's snippets have to be considered. This is done by comparing the
    last_decision_time in relos index for each case and the x hour limit."""
    case_decision_time_df['decision_x_hour_date'] = from_date_obj

    # Find the max date between the decision_x_hour_date and last submit/dismiss date
    case_decision_time_df['sum_entropy_from_date'] = case_decision_time_df[
        ['review_action_time', 'decision_x_hour_date']].max(axis=1)

    return case_decision_time_df


def generate_snippet_df(case_decision_time_df, ann_index, ann_doc_type, es, primary_note_types, config):
    """Queries the ann index for snippets with specific case_id, from primary note_types, with label green and
    note_date greater than service_date."""
    snippet_dicts = []
    event_candidates_by_group = gb_utils.get_ann_candidates(config.global_es_address, config.event_candidate_groups)
    for index, val in case_decision_time_df[['case_id', 'sum_entropy_from_date']].iterrows():
        # Query the ann index for snippets of primary note types and label green and greater than given date
        ann_query = {
            "query": {
                "bool": {
                    "must": [{
                        "term": {
                            "case_id": val['case_id']
                        }
                        },
                        {
                            "terms": {
                                "label": event_candidates_by_group
                            }
                        },
                        {

                            "terms": {
                                "note_type": primary_note_types
                            }

                        },
                        {
                            "range": {
                                "note_date": {
                                    "gte":  datetime.datetime.strftime(val['sum_entropy_from_date'], "%Y-%m-%d %H:%M:%S")
                                }
                            }
                        }]
                }
            },
            "_source": ["case_id", "ann_id", "kermit_probability", "similarity_group", "kermit_label"]
        }

        search_params = {
            'es_object': es,
            'search_index': ann_index,
            'scroll_time': '10m',
            'query_body': ann_query,
            'page_size': 50,
            'doc_type': ann_doc_type,
            'timeout': 60,
            'upto_count': -1
        }
        is_empty = True
        for res in esg.es_search_generator(**search_params):
            if is_empty:
                is_empty = False
            snippet_dicts.append(res['_source'])
        if is_empty:
            snippet_dicts.append({"case_id": val['case_id']})
    kermit_df = pd.DataFrame(snippet_dicts)
    kermit_df['GreenTag'] = kermit_df['kermit_label'].apply(lambda x: 1 if x == 'green' else 0)
    kermit_df.fillna({'kermit_probability': 0.0, 'similarity_group': 0}, inplace=True)
    return kermit_df


def calculate_case_entropy(kermit_df):
    """Filters the kermit_df based on similarity groups."""

    if 'similarity_group' in kermit_df.columns:
        # This is to get the representative snippet from each similarity group
        kermit_df = kermit_df.loc[kermit_df.reset_index().groupby(['case_id', 'similarity_group'])['kermit_probability'].idxmax()]
        # Drop the Similarity group
        kermit_df.drop('similarity_group', axis=1, inplace=True)

    kermit_df = kermit_df.reset_index().drop('index', axis=1)

    kermit_df['entropy'] = kermit_df['kermit_probability'].apply(
        lambda x: sp_stats.entropy([float(x), (1 - float(x))], base=2))
    kermit_df['GreenTag'] = kermit_df['GreenTag'].astype(bool)
    res_df = kermit_df.groupby(['case_id']).sum()
    res_df.reset_index(inplace=True)

    return res_df


def calculate_audit_work_list(case_entropy_df, threshold):
    """Identifies the cases to send to either audit or work list.
    Input: case_entropy_df as a dataframe, threshold.
    Output: Dataframe with columns case_id and result columns i.e (audit/work list)"""
    case_entropy_df['work_list'] = case_entropy_df['entropy'].apply(lambda x: x > threshold)
    case_entropy_df['audit_list'] = case_entropy_df['entropy'].apply(lambda x: x <= threshold)
    return case_entropy_df


def gen_action_audit_work_list(x, index_name, doc_type):
    """Used against each row of dataframe to generate the corresponding action."""
    action = {
        "_index": index_name,
        "_op_type": 'update',
        "_type": doc_type,
        "_id": x['case_id'],
        "_source": {"doc": {
            "latest_decision": "audit" if x['audit_list'] else "no decision",
            "latest_decision_maker": "pieces",
            "latest_review_status": "audit" if x['audit_list'] else "no decision",
            "case_entropy": x['entropy'] if x['entropy'] != 0 else []
        }
        }
    }
    return action


def get_cases_under_review(config, from_date_obj):
    """Returns the list of case_ids which are under review from the last 24 hours."""
    # get list of cases under review
    under_review_query = {
        "query": {
            "bool": {
                "must": [
                    {

                        "term": {
                            "latest_review_status": "review"
                        }

                    }
                    ,
                    {
                        "range": {
                            "latest_review_start_time": {
                                "gte": datetime.datetime.strftime(from_date_obj, "%Y-%m-%d %H:%M:%S")
                            }
                        }
                    }
                ]
            }
        }
        , "_source": ['case_id']
    }

    search_params = {
        'es_object': es,
        'search_index': config.relos_index,
        'scroll_time': '10m',
        'query_body': under_review_query,
        'page_size': 50,
        'doc_type': config.relos_index_type,
        'timeout': 60,
        'upto_count': -1
    }

    cases_under_review = []
    for res in esg.es_search_generator(**search_params):
        cases_under_review.append(res['_source']['case_id'])
    return cases_under_review


def generate_action_list(df, index_name, doc_type, function_):
    """Generate the index action list for the processed kermit dataframe and return it.
    Input: Processed DataFrame with audit/work list values.
    Output: action list/generator for updating the es index."""
    df['action'] = df.apply(lambda x: function_(x, index_name, doc_type), axis=1)
    return list(df['action'])


def gen_action_model_eval_case_entropy(x, index_name, doc_type):
    """Used against each row of dataframe to generate the corresponding action."""
    action = {
        "_index": index_name,
        "_op_type": 'index',
        "_type": doc_type,
        "_source": {
            "case_id": x['case_id'],
            "use_case": "relos",
            "model_type": "active_learner",
            "value_type": "case_entropy",
            "value": x['entropy'],
            "current_service_date": x['service_date'],
            "previous_service_date": x['prev_service_date'],
            "add_date": x['add_date'],
            "model_version": x['model_version']
        }
    }
    return action


def gen_action_model_eval_case_green_snippet_count(x, index_name, doc_type):
    """Used against each row of dataframe to generate the corresponding action."""
    action = {
        "_index": index_name,
        "_op_type": 'index',
        "_type": doc_type,
        "_source": {
            "case_id": x['case_id'],
            "use_case": "relos",
            "model_type": "kermit_greentag",
            "value_type": "green_snippet_count",
            "value": x['GreenTag'],
            "current_service_date": x['service_date'],
            "previous_service_date": x['prev_service_date'],
            "add_date": x['add_date'],
            "model_version": x['model_version']
        }
    }
    return action


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print ("Usage: python active_learner.py <config_file_path>")

    config_file_path = sys.argv[1]

    # Load config
    config = imp.load_source('config', config_file_path)

    threshold = float(config.active_learner_threshold)

    # get primary note types
    primary_note_types = gb_utils.get_interested_note_type(config.global_es_address, config.configuration_index,
                                                           config.configuration_index_type)

    # add_date, to_date and from_date
    to_date_obj = datetime.datetime.now()
    from_date_obj = to_date_obj - datetime.timedelta(hours=24)
    add_date = to_date_obj.strftime("%Y-%m-%d %H:%M:%S")

    es = Elasticsearch([config.es_address], timeout=120, max_retries=5, retry_on_timeout=True)

    case_decision_time_df = get_case_last_decision_list(es, config, from_date_obj, to_date_obj)

    case_rqd_time_df = compute_case_consideration_time(case_decision_time_df, from_date_obj)

    kermit_df = generate_snippet_df(case_rqd_time_df, config.ann_index, config.ann_index_type, es, primary_note_types, config)

    case_entropy_df = calculate_case_entropy(kermit_df)

    # Put into audit or work list based on entropy and threshold
    audit_work_df = calculate_audit_work_list(case_entropy_df, threshold)

    # Write the decision to file
    curr_date = to_date_obj.strftime("%Y%m%d%H%M%S")
    # Compute curr_date here similar to kermit_file
    audit_work_df.to_csv(os.path.join(config.active_learner_log_folder, "case_entropy_" + curr_date + ".csv"),
                         index=False, delimiter="\t")

    # Get the list of cases under review
    cases_under_review = get_cases_under_review(config, from_date_obj)

    # Generate the action list for audit or worklist -
    # using this approach as a workaround rather than the apply approach used above because of errors
    actions_audit_work = []
    for index, val in audit_work_df.iterrows():
        if val['case_id'] in cases_under_review:
            print ("{} is currently under review so not updating the entropy.".format(val['case_id']))
            continue
        actions_audit_work.append(gen_action_audit_work_list(val, config.relos_index, config.relos_index_type))

    # Index the audit or work list decision from active learner
    print ("(The number of active learner documents indexed into relos index , documents failed) are ")
    print (helpers.bulk(es, actions_audit_work, raise_on_error=False))

    # Index the entropy values into model_evaluation_log

    # Add required columns to case_entropy
    case_entropy_df['service_date'] = to_date_obj.strftime("%Y-%m-%d %H:%M:%S")
    case_entropy_df['prev_service_date'] = from_date_obj.strftime("%Y-%m-%d %H:%M:%S")
    case_entropy_df['add_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    case_entropy_df['model_version'] = config.active_learner_model_version

    # Index the case entropy
    actions_case_entropy = generate_action_list(case_entropy_df, config.model_evaluation_index,
                                                config.model_evaluation_doc_type,
                                                gen_action_model_eval_case_entropy)
    actions_case_green_snippet_count = generate_action_list(case_entropy_df, config.model_evaluation_index,
                                                            config.model_evaluation_doc_type,
                                                            gen_action_model_eval_case_green_snippet_count)

    print("(The number of active learner documents indexed into model_evaluation_log, documents failed) are ")
    print (helpers.bulk(es, actions_case_entropy, raise_on_error=False))
    print(helpers.bulk(es, actions_case_green_snippet_count, raise_on_error=False))

"""
This is the wrapper around the prediction file from Michael.
we get the required data, get the evaluation of snippets and index it.
Snippets older than 24 hours are marked non-green in the next step.
The cases which are under review are not indexed in the run.
"""

import sys
import datetime as dt
import imp
from elasticsearch import Elasticsearch, helpers
from application.resources.piecestech import get_nlp_ann_contents_from_es as get_nlp_ann
from application.resources.piecestech import elastic_search_generator as esg
from application.resources.piecestech import kermit_model_eval as kermit_eval
from time import localtime, strftime
import scipy as sp


def generate_predictions_auto_report_kermit(config, metric_output_file_path, from_date=None, to_date=None,
                                            to_be_indexed="no"):
    """Run the auto-report kermit."""

    curr_date = dt.datetime.now()

    # Convert the from and to date into datetime format if present, else use current_serv_date and 24 hours prior as
    # prev service_date
    if to_date:
        to_date = dt.datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")
    else:
        to_date = curr_date
    if from_date:
        from_date = dt.datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
    else:
        from_date = to_date - dt.timedelta(hours=24)

    # get the required NLP_ann
    nlp_ann_df = get_nlp_ann.get_ann_contents(config, from_date, to_date)

    kermit_pred_df = kermit_eval.evaluate(nlp_ann_df,
                                          kermit_w2v_path=config.kermit3_w2v_path,
                                          lookup_path=config.kermit3_lookup_path,
                                          model_path=config.kermit3_model_path,
                                          sim_threshold=config.kermit3_sim_threshold,
                                          prob_threshold=config.kermit3_prob_threshold,
                                          max_green=config.kermit3_max_green)

    kermit_pred_df.rename(columns={'green': 'GreenTag',
                                   'prob': 'Probability',
                                   'txt.note_date': 'NoteDate'}, inplace=True)
    final_df = kermit_pred_df[['ann_id', 'GreenTag', 'Probability', 'txt.note_type', 'ann.note_text', 'sim_grp',
                               'LastModifiedBy', 'ann.case_id']]

    # if to_be_indexed then index kermit
    if to_be_indexed.lower() == "yes":
        es = Elasticsearch([config.es_address], timeout=120, max_retries=5, retry_on_timeout=True)
        prediction_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        index_name = config.ann_index
        ann_type = "info"

        update_actions = []
        # Get the list of cases under review
        cases_under_review = get_cases_under_review(config, from_date, es)

        for index, row in kermit_pred_df.iterrows():
            body = dict()

            if row['ann.case_id'] in cases_under_review:
                print ("The case {} is not indexed as it's under review. ".format(row['ann.case_id']))
                continue

            body['ann_id'] = str(row['ann_id'])
            body['prediction_value'] = float(row['Probability'])
            body['prediction_rating'] = str(row['GreenTag'])
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
            doc['similarity_group'] = int(row['sim_grp'])

            if row['LastModifiedBy'] in ['', 'pieces']:
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
        print ("(The number of documents indexed into ann index , documents failed) are ")
        print (helpers.bulk(es, update_actions, raise_on_error=False))

    metric_df = final_df
    metric_df.to_csv(metric_output_file_path, sep="\t", index=False)
    return final_df


def get_cases_under_review(config, from_date_obj, es):
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
                                "gte": dt.datetime.strftime(from_date_obj, "%Y-%m-%d %H:%M:%S")
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


def update_relos_relevancy(config, x_hour=24):
    """This is to update the documents' user_response_type field from relos_relevant to relos_non_relevant once the
    snippet's corresponding note is older than a given threshold. This is required to not show the snippets(marked by
    annotators) from the older notes."""

    xhours_date = dt.datetime.now() - dt.timedelta(hours=x_hour)

    es = Elasticsearch([config.es_address], timeout=120, max_retries=5, retry_on_timeout=True)

    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "note_date": {
                                "lte": xhours_date.strftime("%Y-%m-%d %H:%M:%S")
                            }
                        }
                    },
                    {
                        "term": {
                            "user_response_type": "relos_relavent"
                        }
                    }
                ]
            }
        }, "_source": []
    }

    search_params = {
        'es_object': es,
        'search_index': config.ann_index,
        'query_body': query,
        'scroll_time': '10m',
        'page_size': 1000,
        'doc_type': config.ann_index_type,
        'timeout': 60,
        'upto_count': -1
    }

    ann_list = ({
        "_index": config.ann_index,
        "_op_type": 'update',
        "_type": config.ann_index_type,
        "_id": hit['_id'],
        "_source": {"doc": {
            "kermit_label": "yellow",
            "user_response_type": "relos_not_relavent",
            "last_modified_by": "pieces"
        }}} for hit in esg.es_search_generator(**search_params))

    print (helpers.bulk(es, ann_list))


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print ("Usage: python kermit.py <config_file_path> <metric_output_file_path> <to_index> " \
              "<from_date in '%Y-%m-%d %H:%M:%S'> <to_date in '%Y-%m-%d %H:%M:%S'>")

    config_file_path = sys.argv[1]
    metric_output_file_path = sys.argv[2]
    to_be_indexed = sys.argv[3]
    from_date = sys.argv[4]
    to_date = sys.argv[5]

    config = imp.load_source('config', config_file_path)

    start = dt.datetime.now()

    kermit_df = generate_predictions_auto_report_kermit(config, metric_output_file_path, to_be_indexed=to_be_indexed,
                                                        from_date=from_date, to_date=to_date)

    # Letting it run with default value of 24 hours
    update_relos_relevancy(config)

    end = dt.datetime.now()

    print ("kermit2 Run time: ", end - start)

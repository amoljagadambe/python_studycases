"""File which processes the relos and relos_ann indexes"""
import click
import datetime
from datetime import timedelta
import logging

from elasticsearch import helpers

from active_learner.ai_engine_exception import AiEngineException
from active_learner import es
from active_learner import utils as al_utils
from commands import configuration


# TODO: Ask
es_tracer = logging.getLogger('elasticsearch')
es_tracer.setLevel(logging.CRITICAL) # or desired level


logging.basicConfig(
    format="ECS Active Learner :: %(asctime)s :: %(levelname)s :: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run(start_time: str, end_time: str, secret_name: str, parameter_name: str, is_local: bool):
    logging.log(logging.INFO, "Active Learner Started.")
    logging.log(
        logging.INFO,
        "The secret_name, parameter_name, start_time, end_time, and is_local flag provided are {}, {}, {}, {}, {} ".format(
            secret_name,
            parameter_name,
            start_time,
            end_time,
            is_local
        ))
    config = configuration.get(secret_name, parameter_name, is_local)

    to_date_obj = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
    from_date_obj = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)

    es_conn = es.connect_es(
        host=config.es_info["host"],
        port=config.es_info["port"],
        from_cloud=(False if is_local else True)
    )

    case_decision_time_iter = al_utils.get_case_last_decision_iter(
        es_conn, config.hospital_codes, config.relos_index, config.relos_ann_index, from_date_obj, to_date_obj)

    # Get the list of cases under review
    cases_under_review = al_utils.get_cases_under_review(
        config.relos_index, from_date_obj, es_conn)

    cases_to_be_indexed = filter(
        lambda item: item.case_id not in cases_under_review, case_decision_time_iter)

    actions = []
    for case_info in cases_to_be_indexed:
        snippet_info_iter = al_utils.get_snippet_info_for_case_info_iter(
            case_info, from_date_obj, es_conn, config.ann_index, config.primary_note_types, config.event_candidates
        )
        rep_snippet_iter = al_utils.get_representative_snippet_for_each_similarity_group_iter(
            snippet_info_iter)

        _case_id = case_info.case_id
        _entropy = 0
        for rep_snippet in rep_snippet_iter:
            _entropy += rep_snippet.entropy

        to_audit = _entropy <= config.active_learner_threshold

        actions.append({
            "_index": config.relos_index,
            "_op_type": 'update',
            "_id": _case_id,
            "_source": {
                "doc": {
                    "latest_decision": "audit" if to_audit else "no decision",
                    "latest_decision_maker": "pieces",
                    "latest_review_status": "audit" if to_audit else "no decision",
                    "case_entropy": _entropy or []
                }
            }
        })

    print("ACTIONS TO BE TAKEN: ", len(actions))

    success, failure = helpers.bulk(es_conn, actions, stats_only=True, raise_on_error=False)

    print("Successful: ", success)
    print("Failed: ", failure)



@click.command()
@click.option("-s", "--start-time", "start", help="Start time", required=False)
@click.option("-e", "--end-time", "end", help="End time", required=False)
@click.option("-x", "--secret", "secret", help="Secret name (Optional)", default=None)
@click.option("-p", "--parameter", "parameter", help="Parameter name (Optional)", default=None)
@click.option('--is-local', is_flag=True, help="Local execution (default:False)")
def batch_run(start, end, secret, parameter, is_local):
    click.echo("Running batch...")
    run(start, end, secret, parameter, is_local)


if __name__ == "__main__":
    batch_run()

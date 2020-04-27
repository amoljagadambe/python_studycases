import click
import datetime
from datetime import timedelta
import logging

from elasticsearch import helpers

from case_activity_status_update.ai_engine_exception import AiEngineException
from case_activity_status_update import es
from case_activity_status_update import utils as case_utils
from commands import configuration

es_tracer = logging.getLogger('elasticsearch')
es_tracer.setLevel(logging.CRITICAL)  # or desired level

logging.basicConfig(
    format="ECS Active Learner :: %(asctime)s :: %(levelname)s :: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run(secret_name: str, parameter_name: str, is_local: bool):
    logging.log(logging.INFO, "Case Activity status update Started.")
    logging.log(
        logging.INFO,
        "The secret_name, parameter_name, and is_local flag provided are {}, {}, {} ".format(
            secret_name,
            parameter_name,
            is_local
        ))
    config = configuration.get(secret_name, parameter_name, is_local)

    # to_date_obj = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
    # from_date_obj = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)

    es_conn = es.connect_es(
        host=config.es_info["host"],
        port=config.es_info["port"],
        from_cloud=(False if is_local else True)
    )
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    actions = []
    actions = case_utils.update_active_dormant_status(es, config.relos_index, config.patient_dormant_day,
                                                      config.note_dormant_day, TIME_FORMAT, config.note_index)
    actions = case_utils.update_discharged_status(es, config.relos_index, TIME_FORMAT, actions)

    print("ACTIONS TO BE TAKEN: ", len(actions))

    success, failure = helpers.bulk(es_conn, actions, stats_only=True, raise_on_error=False)

    print("Successful: ", success)
    print("Failed: ", failure)


@click.command()
@click.option("-x", "--secret", "secret", help="Secret name (Optional)", default=None)
@click.option("-p", "--parameter", "parameter", help="Parameter name (Optional)", default=None)
@click.option('--is-local', is_flag=True, help="Local execution (default:False)")
def batch_run(secret, parameter, is_local):
    click.echo("Running batch...")
    run(secret, parameter, is_local)


if __name__ == "__main__":
    batch_run()

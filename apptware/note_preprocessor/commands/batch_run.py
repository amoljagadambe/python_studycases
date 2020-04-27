"""File which processes the notes against Unitex, main level program."""
import click
from datetime import datetime, timedelta
import logging
from collections import namedtuple

from note_preprocessor.ai_engine_exception import AiEngineException
from note_preprocessor import nlp
from note_preprocessor import es
from note_preprocessor.retrieve_secret import get_secret
import note_preprocessor.db_connection_util as db

import load_env


logging.basicConfig(
    format="ECS Note Preprocessor :: %(asctime)s :: %(levelname)s :: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
Config = namedtuple("Config", ["mysql_info", "es_info", "org_id", "note_index"])


def run(start_time: str, end_time: str, secret_name: str, is_local: bool):
    logging.log(logging.INFO, "Note Pre-Processing and Indexing Started.")
    logging.log(
        logging.INFO,
        "The secret_name, start_time, end_time, and is_local flag provided are ",
        secret_name,
        start_time,
        end_time,
        is_local
    )
    if secret_name:
        config = get_config_from_secrets_manager(secret_name)
    else:
        config = get_config_from_environment(is_local)
    note_data = get_note_data(start_time, end_time, config)
    processed_data = process(note_data)
    index(processed_data, config, is_local)


def get_config_from_secrets_manager(secret_name: str) -> Config:
    secret = get_secret(secret_name)
    logging.info("Retrieved secret successfully")
    try:
        config = Config(
            mysql_info=secret["mysql_info"],
            es_info=secret["es_info"],
            note_index=secret["es_info"]["txt_index"],
            org_id=secret["org_id"],
        )
        return config
    except AttributeError:
        logging.log(logging.CRITICAL, "Config not present in secrets")
        raise AiEngineException


def get_config_from_environment(is_local: bool):
    mysql_info, es_info, org_id = load_env.load_from_file() if is_local else load_env.load_from_environment()
    config = Config(
        mysql_info=mysql_info,
        es_info=es_info,
        note_index=es_info["txt_index"],
        org_id=org_id,
    )
    return config


def get_note_data(start_time, end_time, config: Config):
    # Query details
    query_start_time = (
        datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") - timedelta(minutes=3)
    ).strftime("%Y-%m-%d %H:%M:%S")
    query_end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    # Connect to MySQL and get the notes
    note_data = db.get_data(
        config.mysql_info, config.org_id, query_start_time, query_end_time
    )
    logging.log(logging.INFO, "Connection to MySQL Successful.")
    return note_data


def process(note_data):
    # Pre-Process notes
    preprocessed_note_generator = nlp.preprocess_notes(note_data)
    logging.log(logging.INFO, "Started pre processing the notes.")
    return preprocessed_note_generator


def index(preprocessed_note_generator, config: Config, is_local: bool):
    # Connect to ES
    es_conn = es.connect_es(
        host=config.es_info["host"],
        port=config.es_info["port"],
        from_cloud=(False if is_local else True)
    )
    logging.log(logging.INFO, "Connection to ES Successful.")

    # Index the Notes
    es.index_notes(es_conn, preprocessed_note_generator, config.note_index)
    logging.log(logging.INFO, "Note Pre Processing and Indexing complete.")


@click.command()
@click.option("-s", "--start-time", "start", help="Start time", required=True)
@click.option("-e", "--end-time", "end", help="End time", required=True)
@click.option("-x", "--secret", "secret", help="Secret name (Optional)", default=None)
@click.option('--is-local', is_flag=True, help="Local execution (default:False)")
def batch_run(start, end, secret, is_local):
    click.echo("Running batch...")
    run(start, end, secret, is_local)


if __name__ == "__main__":
    batch_run()

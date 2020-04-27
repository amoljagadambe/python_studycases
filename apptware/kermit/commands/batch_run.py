import logging
import click
import datetime
from kermit import es_connect as es
from kermit import utils as k_utils
from commands import configuration


def run(start_time: str, end_time: str, secret_name: str, parameter_name: str, is_local: bool, indexed="no"):
    logging.log(logging.INFO, "Active Learner Started.")
    logging.log(
        logging.INFO,
        "The secret_name, parameter_name, start_time, end_time, indexed and is_local flag provided are {}, {}, {}, "
        "{}, {} ".format(
            secret_name,
            parameter_name,
            start_time,
            end_time,
            indexed,
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

    k_utils.generate_predictions_auto_report_kermit(config, config.hospital_codes, config.ann_index, config.relos_index,
                                                    config.event_candidates_by_group, config.note_types,
                                                    es_conn, to_be_indexed=indexed,
                                                    from_date=from_date_obj, to_date=to_date_obj)

    # Letting it run with default value of 24 hours
    k_utils.update_relos_relevancy(es_conn, config.ann_index)


@click.command()
@click.option("-s", "--start-time", "start", help="Start time", required=True)
@click.option("-e", "--end-time", "end", help="End time", required=True)
@click.option("-x", "--secret", "secret", help="Secret name (Optional)", default=None)
@click.option("-p", "--parameter", "parameter", help="Parameter name (Optional)", default=None)
@click.option("-i", "--is-indexed", "indexed", help="yes/no", required=True)
@click.option('--is-local', is_flag=True, help="Local execution (default:True)")
def batch_run(start, end, secret, parameter, indexed, is_local):
    click.echo("Running batch...")
    run(start, end, secret, parameter, indexed, is_local)


if __name__ == "__main__":
    batch_run()

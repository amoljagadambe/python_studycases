import logging
from collections import namedtuple
from dataclasses import dataclass

import load_env

# from commands.retrieve_secret import get as get_from_secrets_manager
from case_activity_status_update.ai_engine_exception import AiEngineException


@dataclass
class Config:
    es_info: dict
    relos_index: str
    note_index: str
    patient_dormant_day: int
    note_dormant_day: int


def get(secret_name: str, parameter_name: str, is_local: bool) -> Config:
    if is_local:
        return _get_config_from_environment(is_local)

    if not (secret_name and parameter_name):
        logging.log(logging.CRITICAL, "secret_name and parameter_name are required for non local execution")
        raise AiEngineException

    return _get_config_from_secrets_manager(secret_name, parameter_name)


def _get_config_from_secrets_manager(secret_name: str, parameter_name: str) -> Config:
    secret, parameter = get_from_secrets_manager(secret_name, parameter_name)
    logging.info("Retrieved secret and parameter successfully")
    try:
        config = Config(
            es_info=secret["es_info"],
            relos_index=secret["es_info"]["relos_index"],
            note_index=secret["es_info"]["note_index"],
            patient_dormant_day=parameter["patient_dormant_day"],
            note_dormant_day=parameter["note_dormant_day"]
        )
        return config
    except AttributeError:
        logging.log(logging.CRITICAL, "Config not present in secrets")
        raise AiEngineException


def _get_config_from_environment(is_local: bool) -> Config:
    es_info, parameters = load_env.load_from_file() if is_local else load_env.load_from_environment()
    config = Config(
        es_info=es_info,
        relos_index=es_info["relos_index"],
        note_index=es_info["note_index"],
        patient_dormant_day=parameters['patient_dormant_day'],
        note_dormant_day=parameters['note_dormant_day']
    )
    return config

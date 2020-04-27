import logging
from collections import namedtuple
from dataclasses import dataclass

import load_env

from commands.retrieve_secret import get as get_from_secrets_manager
from active_learner.ai_engine_exception import AiEngineException


@dataclass
class Config:
    es_info: dict
    ann_index: str
    relos_index: str
    relos_ann_index: str
    active_learner_threshold: float
    primary_note_types: list
    hospital_codes: list
    event_candidates: list


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
            ann_index=secret["es_info"]["ann_index"],
            relos_index=secret["es_info"]["relos_index"],
            relos_ann_index=secret["es_info"]["relos_ann_index"],
            active_learner_threshold=parameter["active_learner_threshold"],
            primary_note_types=parameter["primary_note_types"],
            hospital_codes=parameter["hospital_codes"],
            event_candidates=parameter["event_candidates"]
        )
        return config
    except AttributeError:
        logging.log(logging.CRITICAL, "Config not present in secrets")
        raise AiEngineException


def _get_config_from_environment(is_local: bool) -> Config:
    es_info, parameters = load_env.load_from_file() if is_local else load_env.load_from_environment()
    config = Config(
        es_info=es_info,
        ann_index=es_info["ann_index"],
        relos_index=es_info["relos_index"],
        relos_ann_index=es_info["relos_ann_index"],
        active_learner_threshold=parameters["active_learner_threshold"],
        primary_note_types=parameters["primary_note_types"],
        hospital_codes=parameters["hospital_codes"],
        event_candidates=parameters["event_candidates"]
    )
    return config

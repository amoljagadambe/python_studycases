import logging
from dataclasses import dataclass
import load_env

from commands.retrieve_secret import get as get_from_secrets_manager
from kermit.ai_engine_exception import AiEngineException


@dataclass
class Config:
    es_info: dict
    ann_index: str
    relos_index: str
    hospital_codes: list
    note_types: list
    event_candidates_by_group: list
    kermit3_w2v_path: str
    kermit3_lookup_path: str
    kermit3_model_path: str
    kermit3_sim_threshold:float
    kermit3_prob_threshold:float
    kermit3_max_green:float


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
            hospital_codes=parameter["hospital_codes"],
            note_types=parameter["note_types"],
            event_candidates_by_group=parameter["event_candidates_by_group"],
            kermit3_w2v_path=parameter["kermit3_w2v_path"],
            kermit3_lookup_path=parameter["kermit3_lookup_path"],
            kermit3_model_path=parameter["kermit3_model_path"],
            kermit3_sim_threshold=parameter["kermit3_sim_threshold"],
            kermit3_prob_threshold=parameter["kermit3_prob_threshold"],
            kermit3_max_green=parameter["kermit3_max_green"]
        )
        return config
    except AttributeError:
        logging.log(logging.CRITICAL, "Config not present in secrets")
        raise AiEngineException


def _get_config_from_environment(is_local: bool) -> Config:
    #parameters: object
    es_info, parameters = load_env.load_from_file(None) if is_local else load_env.load_from_environment()
    config = Config(
        es_info=es_info,
        ann_index=es_info["ann_index"],
        relos_index=es_info["relos_index"],
        hospital_codes=parameters["hospital_codes"],
        note_types=parameters["note_types"],
        event_candidates_by_group=parameters["event_candidates_by_group"],
        kermit3_w2v_path=parameters["kermit3_w2v_path"],
        kermit3_lookup_path=parameters["kermit3_lookup_path"],
        kermit3_model_path=parameters["kermit3_model_path"],
        kermit3_sim_threshold=parameters["kermit3_sim_threshold"],
        kermit3_prob_threshold=parameters["kermit3_prob_threshold"],
        kermit3_max_green=parameters["kermit3_max_green"]
    )
    return config

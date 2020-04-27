import logging
from environs import Env
from pathlib import Path

from active_learner.ai_engine_exception import AiEngineException


logger = logging.getLogger(__name__)

# For production, specify the file, which may be mounted to the pod
PATH_TO_ENVIRONMENT_FILE = "./.env"
env = Env()


def _parse_config_from_env(env_obj: Env):
    return env_obj.dict("es_info"), {
        "active_learner_threshold": env_obj.float("active_learner_threshold"),
        "primary_note_types": env_obj.list("primary_note_types"),
        "hospital_codes": env_obj.list("hospital_codes"),
        "event_candidates": env_obj.list("event_candidates")
    }
    # return env_obj.dict("es_info"), env_obj.dict("parameters")
    return env_obj.dict("es_info")

def load_from_file(env_file_path = None):
    env_path = env_file_path or Path(PATH_TO_ENVIRONMENT_FILE)
    try:
        env.read_env(path=env_path, override=True)
    except IOError:
        logging.log(logging.ERROR, "No environment file found")
        raise AiEngineException
    return _parse_config_from_env(env_obj=env)


def load_from_environment():
    env.read_env()
    return _parse_config_from_env(env_obj=env)

import logging
from environs import Env
from pathlib import Path
import os
logger = logging.getLogger(__name__)

# For production, specify the file, which may be mounted to the pod
BASE_DIR = os.path.abspath('./.env')

PATH_TO_ENVIRONMENT_FILE = "./.env"
env = Env()


def _parse_config_from_env(env_obj: Env):
    return env_obj.dict("es_info"), {
        "kermit3_w2v_path":env_obj.str("kermit3_w2v_path"),
        "kermit3_lookup_path": env_obj.str("kermit3_lookup_path"),
        "kermit3_model_path": env_obj.str("kermit3_model_path"),
        "kermit3_sim_threshold": env_obj.float("kermit3_sim_threshold"),
        "kermit3_prob_threshold":env_obj.float("kermit3_prob_threshold"),
        "kermit3_max_green":env_obj.float("kermit3_max_green"),
        "note_types": env_obj.list("note_types"),
        "hospital_codes": env_obj.list("hospital_codes"),
        "event_candidates_by_group": env_obj.list("event_candidates_by_group")
    }

    return env_obj.dict("es_info"), env_obj.dict("parameters")
    # return env_obj.dict("es_info")


def load_from_file(env_file_path=None):
    env_path = env_file_path or Path(PATH_TO_ENVIRONMENT_FILE)
    #env_path = env_file_path or 'E:\Projects\kermit\.env'
    try:
        env.read_env(path=env_path, override=True)
    except IOError:
        logging.log(logging.ERROR, "No environment file found")
        raise Exception("File not Found")
    return _parse_config_from_env(env_obj=env)


def load_from_environment():
    env.read_env()
    return _parse_config_from_env(env_obj=env)


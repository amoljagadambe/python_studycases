import logging
from environs import Env
from pathlib import Path

from note_preprocessor.ai_engine_exception import AiEngineException

logging.basicConfig(
    format="ECS Note Preprocessor :: %(asctime)s :: %(levelname)s :: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# For production, specify the file, which may be mounted to the pod
PATH_TO_ENVIRONMENT_FILE = "./.env"
env = Env()

def load_from_file(env_file_path = None):
    env_path = env_file_path or Path(PATH_TO_ENVIRONMENT_FILE)
    # This overrides environment variables for the application
    # To not override, use override=False
    try:
        env.read_env(path=env_path, override=True)
    except IOError:
        logging.log(logging.ERROR, "No environment file found")
        raise AiEngineException
    return env.dict("mysql_info"), env.dict("es_info"), env("org_id")


def load_from_environment():
    env.read_env()
    return env.dict("mysql_info"), env.dict("es_info"), env("org_id")

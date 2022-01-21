"""
config for server
"""
import os

from starlette.config import Config

app_path = os.path.dirname(os.path.realpath(__file__))
env = os.environ.get('ENV')
env_file_mapping = {
    'dev': os.path.join(app_path, '.env'),
    'prod': os.path.join(app_path, '.env.prod'),
}
env_path = os.path.join(app_path, env_file_mapping.get(env, '.env'))
config = Config(env_path)
DEBUG = env == 'dev'

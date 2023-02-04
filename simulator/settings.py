import os
from pydantic import BaseSettings


class Environment(BaseSettings):
    RESOURCES_DIR: str

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


ENV = Environment()
SCENARIO_DIR = os.path.join(ENV.RESOURCES_DIR, "scenarios")

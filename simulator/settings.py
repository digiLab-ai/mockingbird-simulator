from pydantic import BaseSettings
import datetime
import os


class Environment(BaseSettings):
    RESOURCES_DIR: str

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


ENV = Environment()
SCENARIO_DIR = os.path.join(ENV.RESOURCES_DIR, "scenarios")

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # Format for datetime strings in input files.
TIME_STEP_DELTA = datetime.timedelta(
    milliseconds=125
)  # Steps will always be this amount of time. Longer steps will be broken down into multiple steps of this duration.

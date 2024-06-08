import os
from pydantic import SecretStr

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PYRE_ENDPOINT: str = "http://localhost:8000"
    PYRE_POLLING_INTERVAL: int = 600
    PYRE_DB_URL: str = "localhost:5432/pyre"
    PYRE_DB_USER: SecretStr = SecretStr("")
    PYRE_DB_PASSWORD: SecretStr = SecretStr("")


config = Config()

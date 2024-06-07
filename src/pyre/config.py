import os
from typing import Optional
from pydantic import SecretStr

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PYRE_ORDERS_FILE: str = os.path.expanduser("~/.pyre/orders.yaml")
    PYRE_POLLING_INTERVAL: int = 600
    PYRE_DB_URL: str = "localhost:5432/pyre"
    PYRE_DB_USER: Optional[SecretStr] = None
    PYRE_DB_PASSWORD: Optional[SecretStr] = None


config = Config()

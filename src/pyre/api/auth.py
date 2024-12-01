from typing import List
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from pyre.config import Config
from pyre.exceptions import PyreException


API_KEY_HEADER = APIKeyHeader(name="X-API-Key")


def is_api_key_valid(api_key: str):
    if len(api_key) < 16:
        return False
    return True


def check_api_key(config: Config):
    if config.PYRE_AUTH_DISABLED:
        return

    api_key = config.PYRE_API_KEY.get_secret_value()
    if not api_key or not is_api_key_valid(api_key):
        raise PyreException("PYRE_API_KEY is either not set or invalid")


def authorizer_factory(config: Config):
    def is_authorized(api_key: str = Security(API_KEY_HEADER)):
        if not api_key or api_key != config.PYRE_API_KEY.get_secret_value():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key"
            )

    return is_authorized


def get_security_dependencies(config: Config) -> List[Depends]:
    if config.PYRE_AUTH_DISABLED:
        return []
    return [Depends(authorizer_factory(config=config))]

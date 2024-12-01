from contextlib import asynccontextmanager
from fastapi import FastAPI

from pyre.api.v1.router import router as v1_router
from pyre.api.auth import check_api_key, get_security_dependencies
from pyre.config import Config, config


def create_api(config: Config) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        check_api_key(config)
        yield

    api = FastAPI(lifespan=lifespan, dependencies=get_security_dependencies(config))
    api.include_router(v1_router)
    return api


api = create_api(config=config)

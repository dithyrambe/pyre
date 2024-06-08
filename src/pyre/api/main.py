from fastapi import FastAPI

from pyre.api.v1.router import router as v1_router


api = FastAPI()
api.include_router(v1_router)


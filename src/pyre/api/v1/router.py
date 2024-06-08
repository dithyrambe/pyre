from fastapi import APIRouter

from pyre.api.v1.endpoints.orders import router as order_router

router = APIRouter(prefix="/v1")

router.include_router(order_router)




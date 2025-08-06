from fastapi import APIRouter

from pyre.api.v1.endpoints.orders import router as order_router
from pyre.api.v1.endpoints.worth import router as worth_router

router = APIRouter(prefix="/v1")

router.include_router(order_router)
router.include_router(worth_router)

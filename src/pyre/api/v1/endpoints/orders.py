from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from pyre.api.v1.models import Order
from pyre.db import crud
from pyre.db.engine import get_db


router = APIRouter(prefix="/orders")


@router.get("/", response_model=List[Order])
def get_orders(
    ticker: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    db: Session = Depends(get_db),
):
    orders = crud.get_orders(
        db=db, ticker=ticker, start_datetime=start_datetime, end_datetime=end_datetime
    )
    return orders


@router.get("/{id}", response_model=Order)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = crud.get_order_by_id(db=db, id=id)
    return order


@router.post("/", response_model=Order)
def upsert_order(order: Order, db: Session = Depends(get_db)):
    upserted = crud.upsert_order(db=db, order=order.model_dump())
    return upserted


@router.post("/bulk")
def upsert_orders(orders: List[Order], db: Session = Depends(get_db)):
    upserted = crud.bulk_upsert_order(db=db, orders=[o.model_dump() for o in orders])
    return upserted


@router.delete("/{id}")
def delete_order_by_id(id: int, db: Session = Depends(get_db)):
    crud.delete_order_by_id(db=db, id=id)

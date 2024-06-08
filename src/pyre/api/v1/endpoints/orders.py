from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from pyre.db import crud
from pyre.db.engine import get_db
from pyre.api.v1.models import Order

router = APIRouter(prefix="/orders")


@router.get("/", response_model=List[Order])
def get_orders(db: Session = Depends(get_db)):
    orders = crud.get_orders(db=db)
    return orders
    

@router.get("/{id}", response_model=Order)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    order = crud.get_order_by_id(id=id, db=db)
    return order


@router.post("/", response_model=Order)
def upsert_order(order: Order, db: Session = Depends(get_db)):
    upserted = crud.upsert_order(order=order.model_dump(), db=db)
    return upserted


@router.delete("/{id}")
def delete_order_by_id(id: int, db: Session = Depends(get_db)):
    crud.delete_order_by_id(id=id, db=db)


from typing import Dict, List, Optional
import pendulum
from sqlalchemy.orm import Session

from pyre.db.schemas import Order


def get_orders(
    db: Session,
    ticker: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
):
    query = db.query(Order)
    if ticker:
        query = query.filter(Order.ticker == ticker)
    if start_datetime:
        query = query.filter(Order.datetime >= pendulum.parse(start_datetime))
    if end_datetime:
        query = query.filter(Order.datetime < pendulum.parse(end_datetime))
    return query.all()


def get_order_by_id(db: Session, id: int):
    return db.query(Order).filter(Order.id == id).first()


def upsert_order(db: Session, order: Dict):
    order = Order(**order)
    delete_order_by_id(id=order.id, db=db)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def bulk_upsert_order(db: Session, orders: List[Dict]):
    orders = [Order(**data) for data in orders]
    for order in orders:
        db.query(Order).filter(Order.id == order.id).delete()
        db.add(order)
    db.commit()


def delete_order_by_id(db: Session, id: int):
    db.query(Order).filter(Order.id == id).delete()
    db.commit()

from typing import Dict, List
from sqlalchemy.orm import Session

from pyre.db.schemas import Order


def get_orders(db: Session):
    return db.query(Order).all()
    

def get_order_by_id(id: int, db: Session):
    return db.query(Order).filter(Order.id == id).first()


def upsert_order(order: Dict, db: Session):
    order = Order(**order)
    delete_order_by_id(id=order.id, db=db)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def bulk_upsert_order(orders: List[Dict], db: Session):
    orders = [Order(**data) for data in orders]
    for order in orders:
        db.query(Order).filter(
            Order.id == order.id
        ).delete()
        db.add(order)
    db.commit()


def delete_order_by_id(id: int, db: Session):
    db.query(Order).filter(
        Order.id == id
    ).delete()
    db.commit()


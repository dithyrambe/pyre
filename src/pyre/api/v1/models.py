from datetime import datetime

from pydantic import BaseModel


class Order(BaseModel):
    """
    Order data model
    """

    id: int
    datetime: datetime
    ticker: str
    price: float
    quantity: float
    fees: float

    class Config:
        from_attributes = True


class Worth(BaseModel):
    """
    Worth data model
    """

    worth: float

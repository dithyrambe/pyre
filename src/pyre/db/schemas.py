from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, Column, DateTime, Double, String


Base = declarative_base()


class StockData(Base):
    __tablename__ = "stock_data"

    datetime = Column(DateTime, primary_key=True)
    ticker = Column(String, primary_key=True)
    open = Column(Double, nullable=True)
    high = Column(Double, nullable=True)
    low = Column(Double, nullable=True)
    close = Column(Double, nullable=True)
    volume = Column(Integer, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, index=True)
    ticker = Column(String, index=True)
    quantity = Column(Double)
    price = Column(Double)
    fees = Column(Double)

from typing import Optional

from sqlalchemy import Engine, create_engine as _create_engine
from sqlalchemy.orm import Session

from pyre.db.schemas import Base
from pyre.config import config


def create_engine() -> Engine:
    _db_url = config.PYRE_DB_URL
    _db_user = config.PYRE_DB_USER.get_secret_value()
    _db_parssword = config.PYRE_DB_PASSWORD.get_secret_value()

    engine = _create_engine(f"postgresql://{_db_user}:{_db_parssword}@{_db_url}")
    Base.metadata.create_all(bind=engine)
    return engine


def get_db():
    engine = create_engine()
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
    

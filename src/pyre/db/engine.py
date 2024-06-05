import os
from typing import Optional

from sqlalchemy import Engine, create_engine as _create_engine
from pyre.exceptions import PyreException

from pyre.db.schemas import Base


def create_engine(db_url: Optional[str] = None, db_user: Optional[str] = None, db_password: Optional[str] = None) -> Engine:
    _db_url = db_url or os.getenv("PYRE_DB_URL")
    _db_user = db_user or os.getenv("PYRE_DB_USER")
    _db_parssword = db_password or os.getenv("PYRE_DB_PASSWORD")
    if _db_url is None:
        raise PyreException("db url (or env var PYRE_DB_HOST) must be set.")

    engine = _create_engine(f"postgresql://{_db_user}:{_db_parssword}@{_db_url}")
    Base.metadata.create_all(bind=engine)
    return engine


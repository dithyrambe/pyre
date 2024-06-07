from typing import Optional

from sqlalchemy import Engine, create_engine as _create_engine

from pyre.db.schemas import Base
from pyre.config import config


def create_engine(db_url: Optional[str] = None, db_user: Optional[str] = None, db_password: Optional[str] = None) -> Engine:
    _db_url = db_url or config.PYRE_DB_URL
    _db_user = db_user or config.PYRE_DB_USER.get_secret_value()
    _db_parssword = db_password or config.PYRE_DB_PASSWORD.get_secret_value()

    engine = _create_engine(f"postgresql://{_db_user}:{_db_parssword}@{_db_url}")
    Base.metadata.create_all(bind=engine)
    return engine


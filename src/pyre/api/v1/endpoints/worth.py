from typing import Optional

from fastapi import APIRouter, Depends
import pendulum
from sqlalchemy import Connection


from pyre.api.v1.models import Worth
from pyre.db.analysis import get_worth
from pyre.db.engine import get_conn


router = APIRouter(prefix="/worth")


@router.get("/", response_model=Worth)
def get(
    on: Optional[str] = None,
    conn: Connection = Depends(get_conn),
):
    if on:
        on = pendulum.parse(on).to_date_string()
    worth = get_worth(conn=conn, on=on)
    return Worth(worth=worth)

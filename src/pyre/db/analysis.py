from sqlalchemy import Connection, text


def get_worth(conn: Connection, on: str | None = None) -> float:
    query = """
    WITH
    positions AS (
        SELECT ticker, SUM(quantity) AS quantity
        FROM orders
        WHERE (:on IS NULL OR datetime <= :on)
        GROUP BY ticker
        HAVING SUM(quantity) > 0
    ),
    last_close AS (
        SELECT s.ticker, s.close
        FROM stock_data s
        INNER JOIN (
            SELECT ticker, MAX(datetime) AS max_datetime
            FROM stock_data
            WHERE close IS NOT NULL
            AND (:on IS NULL OR datetime <= :on)
            GROUP BY ticker
        ) sub 
        ON s.ticker = sub.ticker
        AND s.datetime = sub.max_datetime
    )
    SELECT SUM(quantity * close) AS worth
    FROM positions p
    INNER JOIN last_close c
    ON p.ticker = c.ticker
    """

    result = conn.execute(text(query), parameters={"on": on}).fetchone()
    return result[0] or 0.0

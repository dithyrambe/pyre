import pendulum
from pydantic import SecretStr
from sqlalchemy.orm import Session

from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient
import pytest

from pyre.config import config
from pyre.db.engine import create_engine
from pyre.db.schemas import Order


postgres = PostgresContainer("postgres:16-alpine")


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)

    config.PYRE_DB_URL = f"{postgres.get_container_host_ip()}:{postgres.get_exposed_port(postgres.port)}"
    config.PYRE_DB_USER = SecretStr(postgres.username)
    config.PYRE_DB_PASSWORD = SecretStr(postgres.password)
    with Session(create_engine()) as db:
        order = Order(id=1, datetime=pendulum.now(), ticker="ABC", price=10.0, quantity=2, fees=0.1)
        db.add(order)
        db.commit()


@pytest.fixture(scope="function", autouse=True)
def reset_data():
    with Session(create_engine()) as db:
        db.query(Order).delete()
        order = Order(id=1, datetime=pendulum.now(), ticker="ABC", price=10.0, quantity=2, fees=0.1)
        db.add(order)
        db.commit()


@pytest.fixture()
def client():
    from pyre.api.main import api
    return TestClient(api)


def test_get_orders(client: TestClient):
    response = client.get("/v1/orders")
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == 1


def test_get_order_by_id(client: TestClient):
    response = client.get("/v1/orders/1")
    order = response.json()
    assert order["id"] == 1


def test_post_order(client: TestClient):
    order_data = {
        "id": 2,
        "datetime": "2024-06-08T00:00:00",
        "ticker": "ABC",
        "price": 10.0,
        "quantity": 2.0,
        "fees": 0.1,
    }
    response = client.post(
        "/v1/orders/",
        json=order_data
    )
    orders_response = client.get("/v1/orders")
    assert response.json() == order_data 
    assert len(orders_response.json()) == 2


def test_update_order(client: TestClient):
    order_data = {
        "id": 1,
        "datetime": "2024-06-08T00:00:00",
        "ticker": "DEF",
        "price": 10.0,
        "quantity": 2.0,
        "fees": 0.1,
    }
    _ = client.post(
        "/v1/orders/",
        json=order_data
    )
    orders_response = client.get("/v1/orders")
    orders = orders_response.json()
    assert len(orders) == 1
    assert orders[0] == order_data


def test_delete_order(client: TestClient):
    _ = client.delete("/v1/orders/1")
    response = client.get("/v1/orders")
    assert len(response.json()) == 0


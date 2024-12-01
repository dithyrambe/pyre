from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from pydantic import SecretStr
import pytest

from pyre.api.main import create_api
from pyre.config import Config


@pytest.mark.parametrize(
    argnames=("config", "client_key", "expected_code"),
    argvalues=[
        (Config(PYRE_AUTH_DISABLED=True), "", status.HTTP_200_OK),
        (
            Config(PYRE_AUTH_DISABLED=False, PYRE_API_KEY=SecretStr("ThisIsAValidSecretKey")),
            "",
            status.HTTP_403_FORBIDDEN,
        ),
        (
            Config(PYRE_AUTH_DISABLED=False, PYRE_API_KEY=SecretStr("ThisIsAValidSecretKey")),
            "ThisIsAValidSecretKey",
            status.HTTP_200_OK,
        ),
        (
            Config(PYRE_AUTH_DISABLED=False, PYRE_API_KEY=SecretStr("ThisIsAValidSecretKey")),
            "NotMatching",
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
@patch("pyre.db.engine.create_engine")
@patch("pyre.db.engine.Session")
def test_auth_toggle(
    session: MagicMock, engine: MagicMock, config: Config, client_key: str, expected_code: int
):
    api = create_api(config)
    client = TestClient(api)

    r = client.get("/v1/orders", headers={"X-API-Key": client_key})
    assert r.status_code == expected_code

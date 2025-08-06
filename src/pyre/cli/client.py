from httpx import Client

from pyre.config import config


def get_client(resource: str | None = None) -> Client:
    base_url = f"{config.PYRE_ENDPOINT}/v1"
    if resource:
        base_url = "/".join([base_url.rstrip("/"), resource.rstrip("/")])
    return Client(
        base_url=base_url,
        headers={"X-API-Key": config.PYRE_API_KEY.get_secret_value()},
    )

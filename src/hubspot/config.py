import os
from dedalus_mcp.auth import Connection, SecretKeys

_BASE_URL = "https://api.hubapi.com"

hubspot = Connection(
    name="JiayuWang-hubspot-mcp",
    secrets=SecretKeys(token="HUBSPOT_ACCESS_TOKEN"),
    base_url=_BASE_URL,
    auth_header_format="Bearer {api_key}",
)

__all__ = ["hubspot"]
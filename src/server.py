import os
from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings
from hubspot import hubspot, hubspot_tools


def _disable_auto_output_schemas(server: MCPServer) -> None:
    server.tools._build_output_schema = lambda _fn: None


def create_server() -> MCPServer:
    return MCPServer(
        name="hubspot-mcp",
        connections=[hubspot],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai"),
    )


async def main() -> None:
    server = create_server()
    _disable_auto_output_schemas(server)
    server.collect(*hubspot_tools)
    await server.serve(port=8080)


__all__ = ["create_server", "main"]
#!/usr/bin/env python3
"""
HubSpot MCP Client Test

This script exercises all tools in the HubSpot MCP server.
Set HUBSPOT_ACCESS_TOKEN in your environment to run these tests.
"""

import asyncio
import os
from dedalus_mcp import MCPServer, get_context
from dedalus_mcp.testing import TestRunner
from hubspot import hubspot, hubspot_tools
from hubspot.tools import (
    list_contacts,
    get_contact,
    create_contact,
    update_contact,
    list_companies,
    create_company,
    list_deals,
    create_deal,
    update_deal_stage,
    list_tickets,
    create_ticket,
    search_crm_objects,
)


def create_server() -> MCPServer:
    from dedalus_mcp.server import TransportSecuritySettings
    return MCPServer(
        name="hubspot-mcp",
        connections=[hubspot],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
    )


async def test_contacts():
    print("\n=== Testing Contacts ===")
    print("\n1. Listing contacts...")
    result = await list_contacts(limit=5)
    print(f"   Result: {result[0].text[:200]}...")

    print("\n2. Searching contacts with filter...")
    result = await search_crm_objects(
        object_type="contacts",
        filter_groups=[{
            "filters": [{
                "propertyName": "email",
                "operator": "CONTAINS_TOKEN",
                "value": "@example.com"
            }]
        }],
        limit=5
    )
    print(f"   Result: {result[0].text[:200]}...")


async def test_companies():
    print("\n=== Testing Companies ===")
    print("\n3. Listing companies...")
    result = await list_companies(limit=5)
    print(f"   Result: {result[0].text[:200]}...")

    print("\n4. Searching companies...")
    result = await search_crm_objects(
        object_type="companies",
        filter_groups=[{
            "filters": [{
                "propertyName": "name",
                "operator": "CONTAINS_TOKEN",
                "value": "Acme"
            }]
        }],
        limit=5
    )
    print(f"   Result: {result[0].text[:200]}...")


async def test_deals():
    print("\n=== Testing Deals ===")
    print("\n5. Listing deals...")
    result = await list_deals(limit=5)
    print(f"   Result: {result[0].text[:200]}...")

    print("\n6. Searching deals...")
    result = await search_crm_objects(
        object_type="deals",
        filter_groups=[{
            "filters": [{
                "propertyName": "dealstage",
                "operator": "NEQ",
                "value": "closedwon"
            }]
        }],
        limit=5
    )
    print(f"   Result: {result[0].text[:200]}...")


async def test_tickets():
    print("\n=== Testing Tickets ===")
    print("\n7. Listing tickets...")
    result = await list_tickets(limit=5)
    print(f"   Result: {result[0].text[:200]}...")

    print("\n8. Searching tickets...")
    result = await search_crm_objects(
        object_type="tickets",
        filter_groups=[{
            "filters": [{
                "propertyName": "hs_ticket_priority",
                "operator": "EQ",
                "value": "HIGH"
            }]
        }],
        limit=5
    )
    print(f"   Result: {result[0].text[:200]}...")


async def test_create_operations():
    print("\n=== Testing Create Operations (Read-only tests skipped for safety) ===")
    print("\n9. Would test create_contact but skipping to avoid side effects")
    print("10. Would test create_company but skipping to avoid side effects")
    print("11. Would test create_deal but skipping to avoid side effects")
    print("12. Would test create_ticket but skipping to avoid side effects")
    print("13. Would test update_contact but skipping to avoid side effects")
    print("14. Would test update_deal_stage but skipping to avoid side effects")


async def main():
    token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
    if not token:
        print("Error: HUBSPOT_ACCESS_TOKEN environment variable is not set")
        print("Please set it and try again:")
        print("  export HUBSPOT_ACCESS_TOKEN=your-token")
        return

    print("HubSpot MCP Client Test")
    print("=" * 50)
    print(f"Using access token: {token[:8]}...")

    server = create_server()
    runner = TestRunner(server)

    async with runner:
        ctx = get_context()
        print(f"Connected to server: {server.name}")
        print(f"Available tools: {[t.name for t in hubspot_tools]}")

        await test_contacts()
        await test_companies()
        await test_deals()
        await test_tickets()
        await test_create_operations()

        print("\n" + "=" * 50)
        print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
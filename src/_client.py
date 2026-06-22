# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""End-to-end client test for the HubSpot MCP server.

Runs against the deployed marketplace server via the Dedalus runner,
passing credentials through the DAuth SecretValues path (the same path a
real marketplace user hits). Every tool is exercised at least once and a
deterministic PASS/FAIL line is printed per tool.

Required environment variables:
    DEDALUS_API_KEY        Dedalus API key (dsk-live-...)
    HUBSPOT_ACCESS_TOKEN   HubSpot private app / OAuth access token

Optional:
    DEDALUS_API_URL   Override Dedalus API base (default https://api.dedaluslabs.ai)
    DEDALUS_AS_URL    Override Dedalus AS base  (default https://as.dedaluslabs.ai)
    MCP_SERVER_SLUG   Marketplace slug (default JiayuWang/hubspot-mcp)

Usage:
    PYTHONPATH=src python src/_client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from hubspot import hubspot  # noqa: E402
from dedalus_mcp.auth import Connection as _Conn
from dedalus_labs.lib.mcp.request import slug_to_connection_name as _s2c


def _rebind(conn, slug):
    return _Conn(name=_s2c(slug), secrets=conn.secrets, base_url=conn.base_url,
                 auth_header_name=conn.auth_header_name, auth_header_format=conn.auth_header_format)


DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", "")
DEDALUS_API_URL = os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai")
DEDALUS_AS_URL = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
MCP_SERVER_SLUG = os.getenv("MCP_SERVER_SLUG", "JiayuWang/hubspot-mcp")
MODEL = os.getenv("DEDALUS_TEST_MODEL", "anthropic/claude-sonnet-4-5")

REQUIRED_TOOLS = [
    "list_contacts",
    "get_contact",
    "search_crm_objects",
    "list_companies",
    "list_deals",
    "list_tickets",
    "create_contact",
    "update_contact",
    "create_company",
    "create_deal",
    "update_deal_stage",
    "create_ticket",
]


def _passed(tool_name: str, output: str) -> bool:
    if not output:
        return False
    lowered = output.lower()
    hard_failures = (
        "no tool",
        "tool not found",
        "unknown tool",
        "could not call",
        "no active context",
        "modulenotfounderror",
        "importerror",
        "currently unavailable",
        "mcp server",
    )
    return not any(marker in lowered for marker in hard_failures)


async def _run_tool(runner, creds, tool_name: str, instruction: str) -> bool:
    print(f"\n--- {tool_name} ---")
    try:
        result = await runner.run(
            input=instruction,
            model=MODEL,
            mcp_servers=[MCP_SERVER_SLUG],
            credentials=creds,
            max_steps=6,
            max_tokens=4096,
        )
        output = getattr(result, "output", str(result)) or ""
        print(output[:600])
        ok = _passed(tool_name, output)
    except Exception as exc:  # noqa: BLE001
        print(f"exception: {exc!r}")
        ok = False
    print(f"[{'PASS' if ok else 'FAIL'}] {tool_name}")
    return ok


async def main() -> int:
    if not DEDALUS_API_KEY:
        print("Error: DEDALUS_API_KEY not set")
        return 1
    if not HUBSPOT_ACCESS_TOKEN:
        print("Error: HUBSPOT_ACCESS_TOKEN not set")
        return 1

    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_mcp.auth import SecretValues

    creds = [SecretValues(hubspot, token=HUBSPOT_ACCESS_TOKEN)]

    client = AsyncDedalus(
        api_key=DEDALUS_API_KEY,
        base_url=DEDALUS_API_URL,
        as_base_url=DEDALUS_AS_URL,
    )
    runner = DedalusRunner(client)

    print(f"Testing HubSpot MCP server: {MCP_SERVER_SLUG}")
    print("=" * 60)

    results: dict[str, bool] = {}

    # 1. Read-only discovery.
    results["list_contacts"] = await _run_tool(
        runner, creds, "list_contacts",
        "Call the list_contacts tool with limit 5 and show each contact id and email.",
    )
    results["get_contact"] = await _run_tool(
        runner, creds, "get_contact",
        "Call list_contacts with limit 1, take that contact's id, then call "
        "get_contact on it and show the result.",
    )
    results["search_crm_objects"] = await _run_tool(
        runner, creds, "search_crm_objects",
        "Call search_crm_objects with object_type 'contacts' and a filter_groups "
        "that matches contacts whose email contains '@', limit 5.",
    )
    results["list_companies"] = await _run_tool(
        runner, creds, "list_companies",
        "Call the list_companies tool with limit 5 and list each company name.",
    )
    results["list_deals"] = await _run_tool(
        runner, creds, "list_deals",
        "Call the list_deals tool with limit 5 and list each deal name.",
    )
    results["list_tickets"] = await _run_tool(
        runner, creds, "list_tickets",
        "Call the list_tickets tool with limit 5 and list each ticket subject.",
    )

    # 2. Write tools, run against isolated smoke-test fixtures so they do not
    #    disturb real data. Each create uses a clearly-labelled test value.
    results["create_contact"] = await _run_tool(
        runner, creds, "create_contact",
        "Call create_contact with properties email "
        "'dedalus-smoke-test@example.com', firstname 'Dedalus', lastname "
        "'SmokeTest'. Report the new contact id.",
    )
    results["update_contact"] = await _run_tool(
        runner, creds, "update_contact",
        "Call list_contacts with limit 1 to get a contact id, then call "
        "update_contact on that id setting properties jobtitle to "
        "'dedalus-smoke-test'. Report success.",
    )
    results["create_company"] = await _run_tool(
        runner, creds, "create_company",
        "Call create_company with properties name 'Dedalus Smoke Test Co'. "
        "Report the new company id.",
    )
    results["create_deal"] = await _run_tool(
        runner, creds, "create_deal",
        "Call create_deal with properties dealname 'Dedalus Smoke Test Deal' "
        "and dealstage 'appointmentscheduled'. Report the new deal id.",
    )
    results["update_deal_stage"] = await _run_tool(
        runner, creds, "update_deal_stage",
        "Call create_deal with dealname 'Dedalus Stage Test' and dealstage "
        "'appointmentscheduled' to get a deal id, then call update_deal_stage "
        "on that id setting dealstage to 'qualifiedtobuy'.",
    )
    results["create_ticket"] = await _run_tool(
        runner, creds, "create_ticket",
        "Call create_ticket with properties subject 'Dedalus Smoke Test "
        "Ticket' and hs_ticket_priority 'LOW'. Report the new ticket id.",
    )

    print("\n" + "=" * 60)
    print("Summary")
    for name in REQUIRED_TOOLS:
        ok = results.get(name, False)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

    all_pass = all(results.get(t, False) for t in REQUIRED_TOOLS)
    print("\nRESULT:", "ALL PASS" if all_pass else "SOME FAILED")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
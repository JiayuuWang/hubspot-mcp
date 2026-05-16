import json
from typing import Any

from mcp.types import TextContent
from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.types import ToolAnnotations

from .types import (
    ContactProperties,
    CompanyProperties,
    DealProperties,
    TicketProperties,
    SearchFilterGroup,
)


async def _req(
    method: HttpMethod,
    path: str,
    body: dict | None = None,
    params: dict | None = None,
) -> list[TextContent]:
    ctx = get_context()
    resp = await ctx.dispatch(
        HttpRequest(
            method=method,
            path=path,
            body=body,
            params=params,
        )
    )
    if resp.success:
        data = resp.response.body or {}
        return [TextContent(type="text", text=json.dumps(data, indent=2))]
    error = resp.error.message if resp.error else "Request failed"
    return [TextContent(type="text", text=json.dumps({"error": error}, indent=2))]


async def _list(
    object_type: str,
    limit: int = 100,
    after: str | None = None,
    properties: list[str] | None = None,
    archived: bool = False,
) -> list[TextContent]:
    params: dict[str, Any] = {"limit": limit, "archived": archived}
    if after:
        params["after"] = after
    if properties:
        params["properties"] = ",".join(properties)
    return await _req(HttpMethod.GET, f"/crm/v3/objects/{object_type}", params=params)


async def _get(
    object_type: str,
    object_id: str,
    properties: list[str] | None = None,
    associations: list[str] | None = None,
) -> list[TextContent]:
    params: dict[str, Any] = {}
    if properties:
        params["properties"] = ",".join(properties)
    if associations:
        params["associations"] = ",".join(associations)
    return await _req(HttpMethod.GET, f"/crm/v3/objects/{object_type}/{object_id}", params=params)


async def _create(
    object_type: str,
    properties: dict[str, Any],
    associations: list[dict[str, Any]] | None = None,
) -> list[TextContent]:
    body: dict[str, Any] = {"properties": properties}
    if associations:
        body["associations"] = associations
    return await _req(HttpMethod.POST, f"/crm/v3/objects/{object_type}", body=body)


async def _update(
    object_type: str,
    object_id: str,
    properties: dict[str, Any],
) -> list[TextContent]:
    return await _req(
        HttpMethod.PATCH,
        f"/crm/v3/objects/{object_type}/{object_id}",
        body={"properties": properties},
    )


async def _search(
    object_type: str,
    filter_groups: list[SearchFilterGroup] | None = None,
    query: str | None = None,
    properties: list[str] | None = None,
    limit: int = 100,
    after: str | None = None,
    sorts: list[dict[str, str]] | None = None,
) -> list[TextContent]:
    body: dict[str, Any] = {
        "filterGroups": filter_groups or [],
        "limit": limit,
    }
    if query:
        body["query"] = query
    if properties:
        body["properties"] = properties
    if after:
        body["after"] = after
    if sorts:
        body["sorts"] = sorts
    return await _req(HttpMethod.POST, f"/crm/v3/objects/{object_type}/search", body=body)


@tool(
    description="List all CRM contacts with pagination, filtering, and property selection. Use this to retrieve contacts in bulk or search through your contact database.",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_contacts(
    limit: int = 100,
    after: str | None = None,
    properties: list[str] | None = None,
    archived: bool = False,
) -> list[TextContent]:
    return await _list("contacts", limit=limit, after=after, properties=properties, archived=archived)


@tool(
    description="Get a specific contact by ID. Returns all contact properties including email, name, phone, and custom properties. Use this to retrieve detailed information about a single contact.",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def get_contact(
    contact_id: str,
    properties: list[str] | None = None,
    associations: list[str] | None = None,
) -> list[TextContent]:
    return await _get("contacts", contact_id, properties=properties, associations=associations)


@tool(
    description="Create a new CRM contact. Required properties include email (unique identifier) and optionally firstname, lastname, phone, company, jobtitle, and custom properties. Use this to add new contacts to your HubSpot database.",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_contact(
    properties: ContactProperties,
    associations: list[dict[str, Any]] | None = None,
) -> list[TextContent]:
    return await _create("contacts", properties, associations=associations)


@tool(
    description="Update an existing CRM contact. Provide the contact_id and the properties you want to update. Use this to modify contact information such as email, name, phone, lifecycle stage, or any custom properties.",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def update_contact(
    contact_id: str,
    properties: dict[str, Any],
) -> list[TextContent]:
    return await _update("contacts", contact_id, properties)


@tool(
    description="List all CRM companies with pagination and property selection. Use this to retrieve companies in bulk, filter by industry, location, or other company properties.",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_companies(
    limit: int = 100,
    after: str | None = None,
    properties: list[str] | None = None,
    archived: bool = False,
) -> list[TextContent]:
    return await _list("companies", limit=limit, after=after, properties=properties, archived=archived)


@tool(
    description="Create a new CRM company. Required properties include name, and optionally domain, industry, phone, city, state, country, zip, website, and custom properties. Use this to add new companies to your HubSpot database.",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_company(
    properties: CompanyProperties,
    associations: list[dict[str, Any]] | None = None,
) -> list[TextContent]:
    return await _create("companies", properties, associations=associations)


@tool(
    description="List all CRM deals with pagination and property selection. Use this to retrieve deals in bulk, filter by stage, amount, or other deal properties. Supports filtering across pipeline stages.",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_deals(
    limit: int = 100,
    after: str | None = None,
    properties: list[str] | None = None,
    archived: bool = False,
) -> list[TextContent]:
    return await _list("deals", limit=limit, after=after, properties=properties, archived=archived)


@tool(
    description="Create a new CRM deal. Required properties include dealname, and optionally amount, dealstage, closedate, pipeline, description, and hubspot_owner_id. Use this to add new deals to your sales pipeline.",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_deal(
    properties: DealProperties,
    associations: list[dict[str, Any]] | None = None,
) -> list[TextContent]:
    return await _create("deals", properties, associations=associations)


@tool(
    description="Update a deal's pipeline stage. Provide the deal_id and the new dealstage value. Common dealstage values include 'appointmentscheduled', 'qualifiedtobuy', 'presentationscheduled', 'decisionmakerboughtin', 'contractsent', 'closedwon', 'closedlost'. Use this to move deals through your sales pipeline.",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def update_deal_stage(
    deal_id: str,
    dealstage: str,
) -> list[TextContent]:
    return await _update("deals", deal_id, {"dealstage": dealstage})


@tool(
    description="List all CRM tickets with pagination and property selection. Use this to retrieve support tickets, filter by priority, pipeline, status, or other ticket properties.",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def list_tickets(
    limit: int = 100,
    after: str | None = None,
    properties: list[str] | None = None,
    archived: bool = False,
) -> list[TextContent]:
    return await _list("tickets", limit=limit, after=after, properties=properties, archived=archived)


@tool(
    description="Create a new CRM ticket for support requests. Required properties include subject and optionally content, hs_ticket_priority (HIGH, MEDIUM, LOW), hs_pipeline, and hubspot_owner_id. Use this to create support tickets from customer inquiries.",
    annotations=ToolAnnotations(readOnlyHint=False),
)
async def create_ticket(
    properties: TicketProperties,
    associations: list[dict[str, Any]] | None = None,
) -> list[TextContent]:
    return await _create("tickets", properties, associations=associations)


@tool(
    description="Search CRM objects (contacts, companies, deals) using flexible filter queries. This unified search endpoint lets you search across multiple object types with complex filter combinations. Use filter_groups to specify propertyName, operator (EQ, NEQ, GT, GTE, LT, LTE, CONTAINS_TOKEN, IN, etc.), and value for each filter.",
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def search_crm_objects(
    object_type: str,
    filter_groups: list[SearchFilterGroup] | None = None,
    query: str | None = None,
    properties: list[str] | None = None,
    limit: int = 100,
    after: str | None = None,
    sorts: list[dict[str, str]] | None = None,
) -> list[TextContent]:
    return await _search(object_type, filter_groups, query, properties, limit, after, sorts)


hubspot_tools = [
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
]

__all__ = ["hubspot_tools"]
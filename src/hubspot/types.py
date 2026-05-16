from typing import Any, TypedDict


class ContactProperties(TypedDict, total=False):
    email: str
    firstname: str
    lastname: str
    phone: str
    mobilephone: str
    company: str
    jobtitle: str
    lifecyclestage: str
    leadstatus: str
    address: str
    city: str
    state: str
    zip: str
    country: str
    website: str


class CompanyProperties(TypedDict, total=False):
    name: str
    domain: str
    website: str
    description: str
    industry: str
    numberofemployees: int
    annualrevenue: float
    city: str
    state: str
    country: str
    phone: str
    address: str
    address2: str
    zip: str
    type: str
    lifecyclestage: str


class DealProperties(TypedDict, total=False):
    dealname: str
    amount: float
    dealstage: str
    closedate: str
    pipeline: str
    description: str
    hubspot_owner_id: str


class TicketProperties(TypedDict, total=False):
    subject: str
    content: str
    hs_ticket_priority: str
    hs_pipeline: str
    hubspot_owner_id: str


class SearchFilter(TypedDict):
    propertyName: str
    operator: str
    value: Any


class SearchFilterGroup(TypedDict):
    filters: list[SearchFilter]


class ListResult(TypedDict):
    results: list[dict[str, Any]]
    paging: dict[str, Any] | None
    total: int | None


class GetResult(TypedDict):
    id: str
    properties: dict[str, Any]
    createdAt: str
    updatedAt: str
    archived: bool


class CreateResult(TypedDict):
    id: str
    properties: dict[str, Any]
    createdAt: str
    updatedAt: str


class UpdateResult(TypedDict):
    id: str
    properties: dict[str, Any]
    updatedAt: str


class SearchResult(TypedDict):
    results: list[dict[str, Any]]
    paging: dict[str, Any] | None
    total: int | None
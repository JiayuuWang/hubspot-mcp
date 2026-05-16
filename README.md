# HubSpot MCP Server

A Type 4 OAuth MCP server for HubSpot CRM API, enabling AI assistants to interact with HubSpot contacts, companies, deals, and tickets.

## Features

- **Contacts**: List, get, create, and update CRM contacts
- **Companies**: List and create CRM companies  
- **Deals**: List, create, and update deal stages
- **Tickets**: List and create support tickets
- **Search**: Unified CRM object search across contacts, companies, and deals

## Setup

### 1. Create a HubSpot OAuth App

1. Go to [developers.hubspot.com](https://developers.hubspot.com) and create an app
2. Set the redirect URL to your Dedalus deployment URL
3. Configure the following scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.companies.read`
   - `crm.objects.companies.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
   - `tickets`

### 2. Environment Variables

Configure these environment variables:

```bash
OAUTH_ENABLED=true
OAUTH_AUTHORIZE_URL=https://app.hubspot.com/oauth/authorize
OAUTH_TOKEN_URL=https://api.hubapi.com/oauth/v1/token
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
OAUTH_SCOPES_AVAILABLE=crm.objects.contacts.read,crm.objects.contacts.write,crm.objects.companies.read,crm.objects.companies.write,crm.objects.deals.read,crm.objects.deals.write,tickets
OAUTH_BASE_URL=https://api.hubapi.com

DEDALUS_API_KEY=dsk-live-...
DEDALUS_AS_URL=https://as.dedaluslabs.ai
```

## Tools

### Contacts

- **list_contacts**: List all contacts with pagination and filtering
- **get_contact**: Get a specific contact by ID
- **create_contact**: Create a new contact with properties
- **update_contact**: Update an existing contact

### Companies

- **list_companies**: List all companies with pagination
- **create_company**: Create a new company

### Deals

- **list_deals**: List all deals with pagination
- **create_deal**: Create a new deal
- **update_deal_stage**: Update a deal's pipeline stage

### Tickets

- **list_tickets**: List all tickets with pagination
- **create_ticket**: Create a new support ticket

### Search

- **search_crm_objects**: Unified search across contacts, companies, and deals

## Usage

```python
from dedalus_mcp import runner

result = await runner.run(
    input="Find all contacts at Acme Corp",
    mcp_servers=["dedalus-labs/hubspot-mcp"],
)
```

## API Reference

This server uses the [HubSpot CRM API v3](https://developers.hubspot.com/docs/reference/api/crm/objects).

## License

MIT
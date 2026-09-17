# AegisOps — Salesforce Integration (Optional, Disabled by Default)

Salesforce is an **optional** adapter. It is **disabled by default** and the
base MVP performs **no real Salesforce writes** and sends **no customer
communications**. Locally, a `FakeSalesforceIntegration` returns synthetic
external IDs/URLs so the workflow and UI can be demonstrated safely.

## Adapters

- `SalesforceIntegration` — the interface (`sync_customer_impact(incident)`).
- `FakeSalesforceIntegration` — default; offline; deterministic synthetic
  references pointing at a non-routable `.invalid` host. No network calls.
- `SalesforceRestIntegration` — a disabled skeleton. Constructing it without
  `SALESFORCE_ENABLED=true` plus instance URL and credentials raises
  `SalesforceNotConfigured`. It performs no writes in the MVP.

Selection happens in `app/shared/container.py:get_salesforce_integration()`,
driven by configuration.

## Conceptual flow

1. An incident is confirmed and its remediation approved.
2. An operator **manually** starts a customer-impact sync (never automatic).
3. The adapter would create/update, in Salesforce:
   - a Service Incident representation,
   - a Customer Impact record,
   - a support Case.
4. The UI shows returned external IDs and URLs where available.
5. No customer emails are sent automatically.
6. No mass communications are automated.

Every sync attempt records `salesforce_sync_requested` and then
`salesforce_sync_completed` or `salesforce_sync_failed` in the append-only
audit trail.

## Suggested object model

| AegisOps concept | Salesforce object (suggested) |
|---|---|
| Incident | Service Incident (custom object) or Case |
| Customer impact | Customer Impact (custom object) linked to the incident |
| Support ticket | Case |

## External Services / OpenAPI approach

The AegisOps backend exposes an OpenAPI schema (`/openapi.json`). In a real
integration, Salesforce **External Services** can register that schema and
invoke the Azure-hosted API from Flow, keeping the AI/approval logic in
AegisOps while Salesforce orchestrates business process.

## Required permissions and least privilege

- Use a dedicated integration user / connected app with the **minimum** object
  and field permissions needed to create the three records above.
- Do not grant broad admin scopes. Prefer field-level security and permission
  sets scoped to the specific objects.
- Store credentials in a secret manager (Azure Key Vault), never in source.

## Why manual human approval is required

Customer-impact records can drive customer-facing processes. Requiring a manual
operator action (after remediation approval) prevents automated or erroneous
external records and communications.

## Switching from fake to real

1. Provision a Salesforce connected app and integration user.
2. Set `SALESFORCE_ENABLED=true` and provide `SALESFORCE_INSTANCE_URL`,
   `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET` via the environment /
   Key Vault (never committed).
3. Implement the REST calls in `SalesforceRestIntegration.sync_customer_impact`.
4. Test in a Salesforce sandbox before any production org.

## Known limitations

- The fake adapter's IDs/URLs are synthetic and non-routable.
- The REST skeleton is intentionally unimplemented in the MVP.
- This integration is a portfolio demonstration, not a production connector.

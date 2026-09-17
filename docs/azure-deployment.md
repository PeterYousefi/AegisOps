# AegisOps — Azure Deployment (Design-Only)

This document describes how AegisOps **would** be deployed to Azure. It is
design-only: **nothing is provisioned or deployed** from this repository until
explicitly approved. The Bicep templates under `infra/` are placeholders with
no real Azure identifiers or secrets.

## Prerequisites

- An Azure subscription and a resource group.
- Azure CLI (`az`) with the Bicep tooling, authenticated (`az login`).
- Docker for building and pushing container images.
- Permission to create the resources below.

## Architecture mapping

| Component | Azure service |
|---|---|
| Frontend service | Azure Container Apps |
| Backend service | Azure Container Apps |
| Container images | Azure Container Registry (ACR) |
| Database | Azure Database for PostgreSQL Flexible Server |
| Runbooks / artifacts | Azure Blob Storage |
| Secrets | Azure Key Vault |
| Identity | Microsoft Entra ID + user-assigned managed identity |
| Observability | Azure Monitor + Application Insights + Log Analytics |
| CI/CD | GitHub Actions |
| Infrastructure-as-code | Bicep (`infra/`) |

## Required environment variables (placeholders)

Provide these at deploy time via the environment or Key Vault — never commit
real values:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `AI_PROVIDER` (`mock` or `azure`); if `azure`: `AZURE_OPENAI_ENDPOINT`,
  `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_API_KEY`
- `SALESFORCE_ENABLED` (default `false`); if `true`: `SALESFORCE_INSTANCE_URL`,
  `SALESFORCE_CLIENT_ID`, `SALESFORCE_CLIENT_SECRET`
- `APPLICATIONINSIGHTS_CONNECTION_STRING` (for telemetry)

## Container build / push (placeholders)

```bash
az acr login --name <PLACEHOLDER_ACR_NAME>
docker build -t <PLACEHOLDER_ACR_LOGIN_SERVER>/aegisops-backend:latest ./backend
docker build -t <PLACEHOLDER_ACR_LOGIN_SERVER>/aegisops-frontend:latest ./frontend
docker push <PLACEHOLDER_ACR_LOGIN_SERVER>/aegisops-backend:latest
docker push <PLACEHOLDER_ACR_LOGIN_SERVER>/aegisops-frontend:latest
```

## Bicep deployment commands (placeholders — do not run until approved)

```bash
# Validate / preview only:
az deployment group what-if \
  --resource-group <PLACEHOLDER_RG> \
  --template-file infra/main.bicep \
  --parameters @infra/main.parameters.example.json

# Deploy (ONLY after explicit approval):
# az deployment group create \
#   --resource-group <PLACEHOLDER_RG> \
#   --template-file infra/main.bicep \
#   --parameters @infra/main.parameters.example.json \
#   --parameters postgresAdminPassword=<PROVIDE_SECURELY>
```

## Managed identity and Key Vault guidance

- Use a **user-assigned managed identity** granted the Key Vault "Secrets User"
  role (already modeled in `infra/modules/keyvault.bicep`).
- Store the DB password and any provider keys in Key Vault; the Container Apps
  read them at runtime via the managed identity. No secrets in app config or
  source.

## Database and storage setup

- PostgreSQL Flexible Server (v16) with a private/allow-listed access model.
- Run Alembic migrations against the provisioned database before first use.
- Blob Storage container `runbooks` for runbook/artifact storage.

## Application Insights

- Workspace-based Application Insights linked to Log Analytics.
- Set `APPLICATIONINSIGHTS_CONNECTION_STRING`; the backend is
  OpenTelemetry-ready for traces/metrics/logs.

## GitHub Actions configuration

- CI (`.github/workflows/ci.yml`) runs backend tests, frontend
  lint/typecheck/build, and Docker image build validation on every PR.
- A **disabled** `azure-deploy` job (`if: ${{ false }}`, manual-only intent) is
  a placeholder. Enabling it later would use OIDC federated credentials
  (`AZURE_CLIENT_ID`/`AZURE_TENANT_ID`/`AZURE_SUBSCRIPTION_ID` as repo secrets)
  — no long-lived credentials.

## Cost-awareness and teardown

- Use the smallest viable SKUs (Burstable PostgreSQL, Basic ACR, minimal
  Container Apps replicas) for a demo.
- Tear down when done: `az group delete --name <PLACEHOLDER_RG> --yes`.

## Reminder

Cloud deployment is **not performed** until explicitly approved. This document
and the Bicep templates are design artifacts only.

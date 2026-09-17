// AegisOps — Azure infrastructure (PLACEHOLDER templates).
//
// NOT DEPLOYED. These templates describe the intended production topology for
// portfolio/design purposes. They contain NO real Azure identifiers, secrets,
// subscription IDs, or tenant IDs. Deployment is performed only after explicit
// approval (Milestone 9). Values are parameterized; see
// main.parameters.example.json for placeholder inputs.

targetScope = 'resourceGroup'

@description('Short name prefix for resources, e.g. "aegisops".')
param namePrefix string = 'aegisops'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Container image for the backend (from ACR).')
param backendImage string = 'PLACEHOLDER_BACKEND_IMAGE'

@description('Container image for the frontend (from ACR).')
param frontendImage string = 'PLACEHOLDER_FRONTEND_IMAGE'

@description('PostgreSQL administrator login (provide at deploy time).')
param postgresAdminLogin string = 'PLACEHOLDER_ADMIN_LOGIN'

@description('PostgreSQL administrator password (provide securely at deploy time).')
@secure()
param postgresAdminPassword string

// ---------------------------------------------------------------------------
// Observability
// ---------------------------------------------------------------------------
module logAnalytics './modules/loganalytics.bicep' = {
  name: 'logAnalytics'
  params: {
    name: '${namePrefix}-logs'
    location: location
  }
}

module appInsights './modules/appinsights.bicep' = {
  name: 'appInsights'
  params: {
    name: '${namePrefix}-appi'
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
  }
}

// ---------------------------------------------------------------------------
// Identity, secrets, registry, storage
// ---------------------------------------------------------------------------
module identity './modules/identity.bicep' = {
  name: 'identity'
  params: {
    name: '${namePrefix}-identity'
    location: location
  }
}

module keyVault './modules/keyvault.bicep' = {
  name: 'keyVault'
  params: {
    name: '${namePrefix}-kv'
    location: location
    principalId: identity.outputs.principalId
  }
}

module acr './modules/acr.bicep' = {
  name: 'acr'
  params: {
    name: '${namePrefix}acr'
    location: location
  }
}

module storage './modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: '${namePrefix}stor'
    location: location
    blobContainerName: 'runbooks'
  }
}

// ---------------------------------------------------------------------------
// Database
// ---------------------------------------------------------------------------
module postgres './modules/postgres.bicep' = {
  name: 'postgres'
  params: {
    name: '${namePrefix}-pg'
    location: location
    adminLogin: postgresAdminLogin
    adminPassword: postgresAdminPassword
  }
}

// ---------------------------------------------------------------------------
// Container Apps environment + services
// ---------------------------------------------------------------------------
module containerAppsEnv './modules/containerapps-env.bicep' = {
  name: 'containerAppsEnv'
  params: {
    name: '${namePrefix}-cae'
    location: location
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
  }
}

module backendApp './modules/containerapp.bicep' = {
  name: 'backendApp'
  params: {
    name: '${namePrefix}-backend'
    location: location
    environmentId: containerAppsEnv.outputs.environmentId
    image: backendImage
    targetPort: 8000
    userAssignedIdentityId: identity.outputs.identityId
  }
}

module frontendApp './modules/containerapp.bicep' = {
  name: 'frontendApp'
  params: {
    name: '${namePrefix}-frontend'
    location: location
    environmentId: containerAppsEnv.outputs.environmentId
    image: frontendImage
    targetPort: 3000
    userAssignedIdentityId: identity.outputs.identityId
  }
}

output backendFqdn string = backendApp.outputs.fqdn
output frontendFqdn string = frontendApp.outputs.fqdn

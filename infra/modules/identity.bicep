// User-assigned managed identity (placeholder).
// Production auth strategy: managed identity + Microsoft Entra ID; no secrets
// stored in app config. This identity is granted access to Key Vault and ACR.
param name string
param location string

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
}

output identityId string = identity.id
output principalId string = identity.properties.principalId
output clientId string = identity.properties.clientId

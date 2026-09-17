// Container Apps managed environment (placeholder).
param name string
param location string
param logAnalyticsWorkspaceId string

// Reference the existing Log Analytics workspace to derive its customerId.
resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: last(split(logAnalyticsWorkspaceId, '/'))
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: name
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
      }
    }
  }
}

output environmentId string = env.id

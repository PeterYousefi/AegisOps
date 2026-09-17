// Azure Database for PostgreSQL Flexible Server (placeholder).
// The admin password is passed securely at deploy time; in production it is
// sourced from Key Vault, never committed.
param name string
param location string
param adminLogin string
@secure()
param adminPassword string

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: name
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: adminLogin
    administratorLoginPassword: adminPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
    }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01-preview' = {
  parent: postgres
  name: 'aegisops'
}

output serverName string = postgres.name

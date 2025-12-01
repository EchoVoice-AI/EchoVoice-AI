param location string = resourceGroup().location
param acsServiceName string
param tags object = {}

// Create Azure Communication Service resource
resource communicationService 'Microsoft.Communication/communicationServices@2023-04-01' = {
  name: acsServiceName
  location: 'global'
  tags: tags
  properties: {
    dataLocation: location
  }
}

// Output connection string for environment configuration
output connectionString string = 'endpoint=https://${acsServiceName}.communication.azure.com/;accesskey=${communicationService.listKeys().primaryKey}'
output resourceId string = communicationService.id
output serviceHost string = '${acsServiceName}.communication.azure.com'

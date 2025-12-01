param location string = resourceGroup().location
param acsServiceName string
param senderEmailAddress string
param keyVaultName string
param tags object = {}

// Reference existing ACS service
resource communicationService 'Microsoft.Communication/communicationServices@2023-04-01' existing = {
  name: acsServiceName
}

// Reference existing Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}

// Store ACS connection string in Key Vault secret
resource acsConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'AzureCommunicationServiceConnectionString'
  properties: {
    value: 'endpoint=https://${acsServiceName}.communication.azure.com/;accesskey=${communicationService.listKeys().primaryKey}'
  }
}

// Store sender email in Key Vault secret
resource senderEmailSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'AzureCommunicationServiceFromEmail'
  properties: {
    value: senderEmailAddress
  }
}

// Store use ACS email flag in Key Vault secret
resource useAcsEmailSecret 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'UseAcsEmail'
  properties: {
    value: 'true'
  }
}

output connectionStringSecretName string = acsConnectionStringSecret.name
output senderEmailSecretName string = senderEmailSecret.name
output useAcsEmailSecretName string = useAcsEmailSecret.name

targetScope = 'subscription'

param resourceGroupName string
param location string = 'eastus'
param acsServiceName string = 'echvoice-acs-${uniqueString(resourceGroup().id)}'
param senderEmailAddress string = 'noreply@echvoice.com'
param keyVaultName string = 'echvoice-kv-${uniqueString(resourceGroup().id)}'
param tags object = {
  project: 'EchoVoice-AI'
  environment: 'production'
}

// Create or reference resource group
resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

// Deploy ACS service
module acsService 'acs-email.bicep' = {
  scope: rg
  name: 'acsServiceDeployment'
  params: {
    location: location
    acsServiceName: acsServiceName
    tags: tags
  }
}

// Deploy Key Vault (if not existing, you'd use a separate template)
// This assumes Key Vault is already created. For full automation, create a separate keyvault.bicep

// Configure ACS email secrets in Key Vault
module acsConfig 'acs-email-config.bicep' = {
  scope: rg
  name: 'acsConfigDeployment'
  params: {
    location: location
    acsServiceName: acsServiceName
    senderEmailAddress: senderEmailAddress
    keyVaultName: keyVaultName
    tags: tags
  }
}

output acsResourceId string = acsService.outputs.resourceId
output acsServiceHost string = acsService.outputs.serviceHost
output connectionStringSecretName string = acsConfig.outputs.connectionStringSecretName
output senderEmailSecretName string = acsConfig.outputs.senderEmailSecretName
output useAcsEmailSecretName string = acsConfig.outputs.useAcsEmailSecretName

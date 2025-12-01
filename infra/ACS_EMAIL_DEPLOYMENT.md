# Azure Communication Services Email Deployment Guide

This Bicep template deploys Azure Communication Services (ACS) for email delivery in EchoVoice-AI.

## Files Overview

- **acs-email.bicep**: Creates the Azure Communication Service resource
- **acs-email-config.bicep**: Stores ACS credentials in Key Vault secrets
- **main-acs.bicep**: Orchestrates the deployment of both services

## Prerequisites

1. **Azure CLI** installed and logged in
2. **Resource Group** already created (or modify the deployment script)
3. **Key Vault** already created in the same resource group
4. **Verified sender email domain** in ACS (required for production)

## Deployment

### Option 1: Using Azure CLI

```bash
# Set variables
RESOURCE_GROUP="echvoice-rg"
LOCATION="eastus"
ACS_SERVICE_NAME="echvoice-acs"
SENDER_EMAIL="noreply@echvoice.com"
KEY_VAULT_NAME="echvoice-kv"

# Deploy
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/main-acs.bicep \
  --parameters \
    location="$LOCATION" \
    acsServiceName="$ACS_SERVICE_NAME" \
    senderEmailAddress="$SENDER_EMAIL" \
    keyVaultName="$KEY_VAULT_NAME"
```

### Option 2: Using PowerShell

```powershell
$resourceGroup = "echvoice-rg"
$location = "eastus"
$acsServiceName = "echvoice-acs"
$senderEmail = "noreply@echvoice.com"
$keyVaultName = "echvoice-kv"

New-AzResourceGroupDeployment `
  -ResourceGroupName $resourceGroup `
  -TemplateFile "infra/main-acs.bicep" `
  -location $location `
  -acsServiceName $acsServiceName `
  -senderEmailAddress $senderEmail `
  -keyVaultName $keyVaultName
```

## Configuration

After deployment, the following secrets are stored in Key Vault:

- **AzureCommunicationServiceConnectionString**: Used in `AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING` env var
- **AzureCommunicationServiceFromEmail**: Used in `AZURE_COMMUNICATION_SERVICE_FROM_EMAIL` env var
- **UseAcsEmail**: Set to `"true"` to enable ACS email delivery

### Retrieve Secrets for Local Development

```bash
# Get connection string
az keyvault secret show \
  --vault-name echvoice-kv \
  --name AzureCommunicationServiceConnectionString \
  --query value -o tsv

# Get sender email
az keyvault secret show \
  --vault-name echvoice-kv \
  --name AzureCommunicationServiceFromEmail \
  --query value -o tsv
```

### Set Environment Variables

For local development or deployment:

```bash
export AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING="<value-from-keyvault>"
export AZURE_COMMUNICATION_SERVICE_FROM_EMAIL="noreply@echvoice.com"
export USE_ACS_EMAIL="true"
```

Or in `.env` file:

```env
AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING=<your-connection-string>
AZURE_COMMUNICATION_SERVICE_FROM_EMAIL=noreply@echvoice.com
USE_ACS_EMAIL=true
```

## Email Domain Verification

For production email sending, you must verify your sender domain in ACS:

1. Go to Azure Portal → Communication Services → echvoice-acs
2. Select **Email** → **Domains**
3. Click **Connect a domain** or **Try a free Azure subdomain**
4. Follow DNS verification steps

**For testing**, you can use the pre-configured `DoNotReply@<your-acs-service>.notification.azure.com` address.

## Integration with FastAPI

The delivery node in `backend/app/graph/langgraph_flow.py` automatically:

1. Checks if `USE_ACS_EMAIL=true`
2. Uses ACS EmailClient to send emails
3. Falls back to mock service if ACS is unavailable or misconfigured

## Cost Considerations

- Azure Communication Services charges per email sent
- Free tier: 100 emails/month
- Production tier: Usage-based pricing
- See [ACS pricing](https://azure.microsoft.com/en-us/pricing/details/communication-services/) for details

## Troubleshooting

### Issue: "Sender email not verified"
**Solution**: Verify your sender domain in ACS or use a pre-configured test email address.

### Issue: "Connection string invalid"
**Solution**: Confirm the connection string in Key Vault and that ACS resource exists in the same region.

### Issue: Emails not sending
**Solution**: Check ACS Email logs in Azure Portal or enable debug logging in the delivery node.

## References

- [Azure Communication Services Email SDK](https://learn.microsoft.com/en-us/python/api/azure-communication-email/)
- [Bicep documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Azure Communication Services pricing](https://azure.microsoft.com/en-us/pricing/details/communication-services/)

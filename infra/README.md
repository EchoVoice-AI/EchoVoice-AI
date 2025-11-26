# Infra: Azure deployment for EchoVoice-AI

This folder contains a minimal Bicep-based scaffold to provision the Azure
resources used by the EchoVoice-AI RAG components (Storage, Cognitive Search,
Function App, Key Vault, Application Insights).

This is a starting point — adjust SKUs, names and settings before running in
production. The deployment is split into small modules to make incremental
changes easier.

Quick start (requires Azure CLI and Bicep):

PowerShell (Windows):

```powershell
# login and select subscription
az login
az account set --subscription <YOUR_SUBSCRIPTION_ID>

# create resource group (replace location as needed)
az group create -n echovoice-rg -l eastus

# deploy with params in this folder
cd infra
./deploy.ps1 -rg echovoice-rg -location eastus -env dev
```

Bash (Linux / macOS):

```bash
az login
az account set --subscription <YOUR_SUBSCRIPTION_ID>
az group create -n echovoice-rg -l eastus
cd infra
./deploy.sh echovoice-rg eastus dev
```

After deployment:

- The deployment outputs will include resource names and connection strings.
- Run `infra/scripts/create-search-index.py` (update env vars in the script or
  pass values via environment) to create the Search Index and optional indexer.

Notes

- This scaffold is intended for development and demonstration. For production
  use you should add RBAC, private endpoints, Key Vault access policies, and
  integrate with CI/CD pipelines.

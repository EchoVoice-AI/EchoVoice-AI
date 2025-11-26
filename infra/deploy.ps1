param(
    [Parameter(Mandatory=$true)][string]$rg,
    [Parameter(Mandatory=$true)][string]$location,
    [Parameter(Mandatory=$true)][string]$env
)

# Simple wrapper to deploy main.bicep
$main = Join-Path $PSScriptRoot 'main.bicep'
if (-not (Test-Path $main)) {
    Write-Error "main.bicep not found in infra folder"
    exit 1
}

Write-Host "Deploying infra to resource group $rg in $location (env=$env)"
az deployment group create --resource-group $rg --template-file $main --parameters environment=$env location=$location

Write-Host "Deployment finished. Check outputs with az deployment group show."
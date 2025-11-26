#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <resource-group> <location> <env>"
  exit 2
fi
RG=$1
LOCATION=$2
ENV=$3

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN="$SCRIPT_DIR/main.bicep"

if [ ! -f "$MAIN" ]; then
  echo "main.bicep not found in infra folder"
  exit 1
fi

echo "Deploying infra to resource group $RG in $LOCATION (env=$ENV)"
az deployment group create --resource-group "$RG" --template-file "$MAIN" --parameters environment="$ENV" location="$LOCATION"

echo "Deployment finished."

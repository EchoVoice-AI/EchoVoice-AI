import os

from services.load_azd_env import load_azd_env

# WEBSITE_HOSTNAME is always set by App Service, RUNNING_IN_PRODUCTION is set in main.bicep
RUNNING_ON_AZURE = os.getenv("WEBSITE_HOSTNAME") is not None or os.getenv("RUNNING_IN_PRODUCTION") is not None

if not RUNNING_ON_AZURE:
    load_azd_env()

# Use FastAPI app as the single entrypoint for this repository's backend.
# If the import fails, surface the error so the developer can fix the migration.
from api.main import app  # type: ignore

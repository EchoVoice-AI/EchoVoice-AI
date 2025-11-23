from __future__ import annotations

import json
from typing import Any, Dict, Optional

from services.delivery import send_email_mock


class DeliveryAgent:
    """Simple delivery agent with pluggable provider hooks.

    By default uses `send_email_mock` for development. Replace or extend
    the provider logic when integrating with real providers (SendGrid,
    Microsoft Graph, or Service Bus triggering another service).
    """

    def __init__(self, provider: Optional[str] = None, hooks: Optional[Dict[str, Any]] = None):
        self.provider = provider
        self.hooks = hooks or {}

    def deliver(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """Deliver a message. Returns a provider-like result dict."""
        # Development fallback
        if not self.provider:
            return send_email_mock(to_email, subject, body)

        # Placeholder for actual provider implementations
        # e.g., if self.provider == 'sendgrid': call SendGrid SDK using hooks
        return {"status": "unsupported_provider", "provider": self.provider}


class AzureDeliveryAdapter:
    """Stubs for Azure integrations (Application Insights, Service Bus).

    Replace prints with SDK calls when preparing for deployment.
    """

    @staticmethod
    def log_delivery_event(event: Dict[str, Any], instrumentation_key: Optional[str] = None) -> bool:
        if instrumentation_key is None:
            print(f"[AppInsights] Delivery event: {json.dumps(event)}")
            return True
        # TODO: real AppInsights SDK call
        return True

    @staticmethod
    def publish_to_service_bus(event: Dict[str, Any], connection_string: Optional[str] = None) -> bool:
        if connection_string is None:
            print(f"[ServiceBus] Publish event: {json.dumps(event)}")
            return True
        # TODO: real Service Bus SDK publish
        return True

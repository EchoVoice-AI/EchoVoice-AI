from typing import Optional
import os

try:
    from azure.communication.email import EmailClient, EmailContent, EmailAddress, EmailMessage
except ImportError:
    EmailClient = None


def send_email_acs(
    to_email: str,
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    connection_string: Optional[str] = None,
):
    """
    Send an email using Azure Communication Services EmailClient.
    Requires AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING and AZURE_COMMUNICATION_SERVICE_FROM_EMAIL in env or as args.
    """
    if EmailClient is None:
        raise ImportError("azure-communication-email is not installed. Run 'pip install azure-communication-email'.")

    connection_string = connection_string or os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
    from_email = from_email or os.getenv("AZURE_COMMUNICATION_SERVICE_FROM_EMAIL")
    if not connection_string or not from_email:
        raise ValueError("Missing Azure Communication Services connection string or from email.")

    client = EmailClient.from_connection_string(connection_string)
    content = EmailContent(subject=subject, plain_text=body)
    recipient = EmailAddress(email=to_email)
    message = EmailMessage(
        sender=from_email,
        content=content,
        recipients=[recipient],
    )
    poller = client.send(message)
    result = poller.result()
    return {"status": result.status, "message_id": result.id, "to": to_email}

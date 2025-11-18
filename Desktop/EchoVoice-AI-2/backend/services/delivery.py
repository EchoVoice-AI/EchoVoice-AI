def send_email_mock(to_email: str, subject: str, body: str):
    # Simulated delivery for development/testing
    print(f"[delivery] Sending email to {to_email} — subject: {subject}\n{body}\n---")
    return {"status": "sent", "to": to_email}

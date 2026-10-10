
import requests
from datetime import datetime, timedelta, timezone
from graph_auth import result

WEBHOOK_URL = "https://unfocused-zoning-plaster.ngrok-free.dev/webhook"

access_token = result["access_token"]

expiration = (
    datetime.now(timezone.utc) + timedelta(hours=1)
).isoformat().replace("+00:00", "Z")

payload = {
    "changeType": "created",
    "notificationUrl": WEBHOOK_URL,
    "resource": "me/mailFolders('Inbox')/messages",
    "expirationDateTime": expiration,
    "clientState": "meeting-scheduler-test"
}

response = requests.post(
    "https://graph.microsoft.com/v1.0/subscriptions",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=30
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.json())
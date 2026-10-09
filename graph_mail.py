import requests

def get_latest_email(access_token):

    url = (
        "https://graph.microsoft.com/v1.0/me/messages"
        "?$top=20"
        "&$orderby=receivedDateTime desc"
        "&$select=subject,from,toRecipients,bodyPreview,receivedDateTime"
    )

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code != 200:
        print("Failed to read email:", response.status_code)
        return None

    messages = response.json().get("value", [])

    meeting_keywords = [
        "meeting", "schedule", "connect",
        "discuss", "availability", "minutes"
    ]

    for message in messages:
        subject = message.get("subject") or ""
        body = message.get("bodyPreview") or ""
        text = f"{subject} {body}".lower()

        if subject.lower().startswith("meeting scheduled"):
            continue

        if "scheduled automatically by the ai meeting scheduler agent" in text:
            continue

        if not any(word in text for word in meeting_keywords):
            continue

        sender = (
            message.get("from", {})
            .get("emailAddress", {})
            .get("address", "")
        )

        recipients = message.get("toRecipients", [])
        recipient = (
            recipients[0].get("emailAddress", {}).get("address", "")
            if recipients else ""
        )

        return {
            "id": message["id"],
            "from": sender,
            "to": recipient,
            "subject": subject,
            "body": body
        }

    print("No likely meeting-request email found.")
    return None


def send_confirmation_email(access_token, recipient, subject, body):

    email = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient
                    }
                }
            ]
        }
    }

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=email
    )

    print("\nEMAIL STATUS:", response.status_code)

    if response.status_code == 202:
        print("CONFIRMATION EMAIL SENT SUCCESSFULLY")
        return True

    print("FAILED TO SEND CONFIRMATION EMAIL")
    print(response.text)

    return False
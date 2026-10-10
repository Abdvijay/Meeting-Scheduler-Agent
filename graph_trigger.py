
from flask import Flask, request
import subprocess
import sys
import os

app = Flask(__name__)

CLIENT_STATE = "meeting-scheduler-test"

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

processed_ids = set()


@app.route("/webhook", methods=["POST"])
def webhook():
    validation_token = request.args.get("validationToken")

    if validation_token:
        return validation_token, 200, {
            "Content-Type": "text/plain"
        }

    notification = request.get_json(silent=True) or {}

    for item in notification.get("value", []):
        if item.get("clientState") != CLIENT_STATE:
            print("Rejected notification: clientState mismatch.")
            continue

        message_id = item.get("resourceData", {}).get("id")

        if not message_id:
            print("Notification has no message ID.")
            continue

        if message_id in processed_ids:
            print("Duplicate notification ignored:", message_id)
            continue

        processed_ids.add(message_id)

        print("\nNew email notification received.")
        print("Message ID:", message_id)
        print("Starting meeting scheduler...")

        try:
            subprocess.Popen(
                [PYTHON, os.path.join(PROJECT_DIR, "main.py"), message_id],
                cwd=PROJECT_DIR
            )
        except Exception as error:
            processed_ids.discard(message_id)
            print("Failed to start scheduler:", error)

    return "", 202


if __name__ == "__main__":
    print("Starting Microsoft Graph webhook...")
    app.run(host="0.0.0.0", port=5000)
from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():

    # Microsoft Graph sends this when
    # validating our notification endpoint.
    validation_token = request.args.get(
        "validationToken"
    )

    if validation_token:

        return validation_token, 200, {
            "Content-Type": "text/plain"
        }

    # Normal Graph notification
    notification = request.get_json(
        silent=True
    )

    print("\n================================")
    print("MICROSOFT GRAPH NOTIFICATION")
    print("================================")

    print(notification)

    return "", 202


if __name__ == "__main__":

    print("Starting Microsoft Graph webhook...")

    app.run(
        host="0.0.0.0",
        port=5000
    )
from mock_email import get_mock_email


def check_for_new_email():

    print("\nEMAIL TRIGGER")
    print("-------------")

    print("Checking for new email...")

    email = get_mock_email()

    if not email:

        print("No new email found.")

        return None

    print("New email detected!")

    print(
        "From:",
        email["from"]
    )

    print(
        "Subject:",
        email["subject"]
    )

    return email
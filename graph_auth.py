import msal

CLIENT_ID = "538a741b-a8a5-4f67-95de-c312b1efe318"

AUTHORITY = "https://login.microsoftonline.com/consumers/"


SCOPES = [
    "Calendars.ReadWrite",
    "Calendars.Read.Shared",
    "Calendars.ReadWrite.Shared",
    "Mail.Read",
    "Mail.Send"
]


app = msal.PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY
)

accounts = app.get_accounts()

if accounts:
    result = app.acquire_token_silent(
        SCOPES,
        account=accounts[0]
    )
else:
    result = app.acquire_token_interactive(
        scopes=SCOPES
    )

if "access_token" in result:
    print("Microsoft Graph authentication successful!")
    print("Token acquired successfully.")
else:
    print("Authentication failed.")
    print(result.get("error"))
    print(result.get("error_description"))
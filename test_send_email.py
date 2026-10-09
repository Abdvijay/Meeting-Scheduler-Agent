from graph_auth import result
from graph_mail import send_confirmation_email


if "access_token" not in result:
    print("Authentication failed.")
    exit()


success = send_confirmation_email(
    result["access_token"],
    "vijay.amadis@outlook.com",
    "AI Meeting Scheduler - Email Test",
    """
Hi Vijay,

This is a test email from the AI Meeting Scheduler Agent.

The email sending functionality is being tested separately.

Thanks,
AI Meeting Scheduler Agent
"""
)


if success:
    print("\nEMAIL TEST PASSED")
else:
    print("\nEMAIL TEST FAILED")
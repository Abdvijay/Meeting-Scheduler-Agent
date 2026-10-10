from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys
from agent import understand_email
from scheduler import find_common_slots, create_meeting_event
from graph_auth import result
from graph_mail import (
    get_latest_email,
    get_email_by_id,
    send_confirmation_email
)
from graph_calendar import (
    get_calendar_events,
    get_shared_calendar_events,
    convert_graph_events_to_scheduler_format,
    create_calendar_event,
)
from confirmation import generate_confirmation


# ==================================================
# CONFIGURATION
# ==================================================

VIJAY_EMAIL = "vijay.amadis@outlook.com"
DEMO_EMAIL = "vijay.demo@outlook.com"

IST = ZoneInfo("Asia/Kolkata")

PARTICIPANT_TEAMS = {
    VIJAY_EMAIL: "Chennai",
    DEMO_EMAIL: "Chennai",
}


# ==================================================
# 1. CHECK AUTHENTICATION
# ==================================================

print("\nAI MEETING SCHEDULER AGENT")
print("==========================")

if not result or "access_token" not in result:
    print("Microsoft Graph authentication failed.")
    raise SystemExit(1)

access_token = result["access_token"]


# ==================================================
# 2. READ THE INCOMING EMAIL
# ==================================================

print("\nREADING OUTLOOK EMAIL")
print("---------------------")

if len(sys.argv) > 1:
    message_id = sys.argv[1]
    email = get_email_by_id(access_token, message_id)
else:
    email = get_latest_email(access_token)

if not email:
    print("No meeting-request email found.")
    raise SystemExit(0)

print("From:", email["from"])
print("To:", email["to"])
print("Subject:", email["subject"])


# ==================================================
# 3. UNDERSTAND THE EMAIL USING QWEN
# ==================================================

print("\nUNDERSTANDING EMAIL")

try:
    understood = understand_email(email)
except Exception as error:
    print("AI email analysis failed:", error)
    raise SystemExit(1)

print(understood)

if not understood.get("is_meeting_request", False):
    print("This email is not a meeting request.")
    raise SystemExit(0)


# ==================================================
# 4. VALIDATE PARTICIPANTS
# ==================================================

sender = email["from"].strip().lower()
recipient = email["to"].strip().lower()

if not sender or not recipient or sender == recipient:
    print("Invalid sender or recipient.")
    raise SystemExit(1)

participants = list(dict.fromkeys([sender, recipient]))

if any(person not in PARTICIPANT_TEAMS for person in participants):
    print("Unsupported participant:", participants)
    print("Configure both email accounts before proceeding.")
    raise SystemExit(1)

participant_teams = {
    person: PARTICIPANT_TEAMS[person]
    for person in participants
}

duration = understood.get("duration_minutes", 30)
purpose = understood.get("purpose", "").strip()

if not isinstance(duration, int) or duration <= 0:
    print("Invalid meeting duration.")
    raise SystemExit(1)

if not purpose:
    purpose = email["subject"] or "Meeting"

print("\nPARTICIPANTS:", participants)
print("PURPOSE:", purpose)
print("DURATION:", duration, "minutes")


# ==================================================
# 5. CALCULATE NEXT WEEK'S DATE RANGE
# ==================================================

today = datetime.now(IST).date()

next_monday = today + timedelta(days=7 - today.weekday())
next_saturday = next_monday + timedelta(days=5)

start_datetime = (
    datetime.combine(next_monday, datetime.min.time(), tzinfo=IST)
    .astimezone(ZoneInfo("UTC"))
    .strftime("%Y-%m-%dT%H:%M:%SZ")
)

end_datetime = (
    datetime.combine(next_saturday, datetime.min.time(), tzinfo=IST)
    .astimezone(ZoneInfo("UTC"))
    .strftime("%Y-%m-%dT%H:%M:%SZ")
)

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
]


# ==================================================
# 6. READ BOTH REAL OUTLOOK CALENDARS
# ==================================================

print("\nREADING VIJAY'S CALENDAR")

vijay_events = get_calendar_events(
    access_token,
    start_datetime,
    end_datetime,
)

if vijay_events is None:
    print("Could not read Vijay's calendar. Stopping.")
    raise SystemExit(1)

print("\nREADING THE SHARED DEMO CALENDAR")

demo_events = get_shared_calendar_events(
    access_token,
    DEMO_EMAIL,
    start_datetime,
    end_datetime,
)

if demo_events is None:
    print("Could not read the demo calendar. Stopping.")
    print("No meeting will be created.")
    raise SystemExit(1)

calendar_events = {
    VIJAY_EMAIL: convert_graph_events_to_scheduler_format(
        vijay_events
    ),
    DEMO_EMAIL: convert_graph_events_to_scheduler_format(
        demo_events
    ),
}

print("Both calendars were retrieved.")


# ==================================================
# 7. FIND A COMMON AVAILABLE SLOT
# ==================================================

print("\nFINDING COMMON AVAILABILITY")

common_slots = find_common_slots(
    participants,
    participant_teams,
    days,
    duration,
    calendar_events,
)

if not common_slots:
    print("No common meeting slot found.")
    raise SystemExit(0)

print("\nAVAILABLE SLOTS")

for slot in common_slots:
    print(slot)

selected_slot = common_slots[0]

print("\nSELECTED SLOT")
print(selected_slot)


# ==================================================
# 8. PREPARE THE MEETING
# ==================================================

meeting_event = create_meeting_event(
    participants,
    selected_slot,
    purpose,
)

print("\nMEETING DETAILS")
print("Subject:", meeting_event["subject"])
print("Date:", meeting_event["date"])
print("Day:", meeting_event["day"])
print("Time:", meeting_event["start"], "-", meeting_event["end"])
print("Participants:", meeting_event["participants"])


# ==================================================
# 9. CREATE THE REAL OUTLOOK EVENT
# ==================================================

start_time = (
    f'{meeting_event["date"]}T'
    f'{meeting_event["start"]}:00'
)

end_time = (
    f'{meeting_event["date"]}T'
    f'{meeting_event["end"]}:00'
)

print("\nCREATING OUTLOOK MEETING")

try:
    event_response = create_calendar_event(
        access_token,
        meeting_event["subject"],
        start_time,
        end_time,
        participants,
    )
except Exception as error:
    print("Event creation failed:", error)
    raise SystemExit(1)

if event_response is None or event_response.status_code not in (200, 201):
    print("Outlook did not confirm event creation.")

    if event_response is not None:
        print("HTTP status:", event_response.status_code)
        print("Response:", event_response.text)

    raise SystemExit(1)

created_event = event_response.json()

print("Outlook event created.")
print("Event ID:", created_event.get("id"))


# ==================================================
# 10. SEND CONFIRMATION EMAILS
# ==================================================

confirmation = generate_confirmation(
    meeting_event,
    duration,
)

print("\nSENDING CONFIRMATION EMAILS")

for participant in participants:
    try:
        sent = send_confirmation_email(
            access_token,
            participant,
            confirmation["subject"],
            confirmation["body"],
        )

        if sent:
            print("Confirmation sent to:", participant)
        else:
            print("Confirmation failed for:", participant)

    except Exception as error:
        print(f"Could not send to {participant}: {error}")


# ==================================================
# FINAL SUMMARY
# ==================================================

print("\n" + "=" * 40)
print("MEETING SCHEDULER SUMMARY")
print("=" * 40)
print("Subject:", meeting_event["subject"])
print("Date:", meeting_event["date"])
print("Time:", meeting_event["start"], "-", meeting_event["end"], "IST")
print("Duration:", duration, "minutes")
print("Participants:", participants)
print("Outlook event ID:", created_event.get("id"))
print("=" * 40)
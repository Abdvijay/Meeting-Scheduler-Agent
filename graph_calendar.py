import requests
from datetime import datetime
from zoneinfo import ZoneInfo

def get_calendar_events(
    access_token,
    start_datetime,
    end_datetime
):

    url = (
        "https://graph.microsoft.com/v1.0/me/calendarView"
        f"?startDateTime={start_datetime}"
        f"&endDateTime={end_datetime}"
        "&$select=subject,start,end"
        "&$orderby=start/dateTime"
    )

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    print(
        "CALENDAR READ STATUS:",
        response.status_code
    )

    if response.status_code != 200:

        print("FAILED TO READ CALENDAR")
        print(response.text)

        return None

    events = response.json().get(
        "value",
        []
    )

    return events


def convert_graph_events_to_scheduler_format(events):

    calendar_events = {}
    ist_timezone = ZoneInfo("Asia/Kolkata")

    timezone_mapping = {
        "UTC": "UTC",
        "India Standard Time": "Asia/Kolkata",
        "GMT Standard Time": "Europe/London",
        "Eastern Standard Time": "America/New_York",
    }

    for event in events:

        start = event.get("start", {})
        end = event.get("end", {})

        start_value = start.get("dateTime")
        end_value = end.get("dateTime")

        if not start_value or not end_value:
            continue

        start_zone = timezone_mapping.get(
            start.get("timeZone", "UTC"), "UTC"
        )
        end_zone = timezone_mapping.get(
            end.get("timeZone", "UTC"), "UTC"
        )

        start_dt = datetime.fromisoformat(
            start_value
        ).replace(tzinfo=ZoneInfo(start_zone))

        end_dt = datetime.fromisoformat(
            end_value
        ).replace(tzinfo=ZoneInfo(end_zone))

        # Convert both event times to Chennai time.
        start_dt = start_dt.astimezone(ist_timezone)
        end_dt = end_dt.astimezone(ist_timezone)

        day_name = start_dt.strftime("%A")

        calendar_events.setdefault(day_name, []).append(
            (
                start_dt.strftime("%H:%M"),
                end_dt.strftime("%H:%M"),
            )
        )

    return calendar_events


def build_calendar_event_payload(
    subject,
    start_time,
    end_time,
    attendees
):

    payload = {
        "subject": subject,

        "body": {
            "contentType": "Text",
            "content": (
                "Meeting scheduled automatically "
                "by the AI Meeting Scheduler Agent."
            )
        },

        "start": {
            "dateTime": start_time,
            "timeZone": "India Standard Time"
        },

        "end": {
            "dateTime": end_time,
            "timeZone": "India Standard Time"
        },

        "attendees": [
            {
                "emailAddress": {
                    "address": email
                },
                "type": "required"
            }
            for email in attendees
        ]
    }

    return payload


def create_calendar_event(
    access_token,
    subject,
    start_time,
    end_time,
    attendees
):

    payload = build_calendar_event_payload(
        subject,
        start_time,
        end_time,
        attendees
    )

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/calendar/events",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print(
        "STATUS:",
        response.status_code
    )

    print("RESPONSE:")

    print(
        response.json()
    )

    return response


def get_shared_calendar_events(
    access_token,
    owner_email,
    start_datetime,
    end_datetime
):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Find the shared calendar belonging to the requested owner.
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/calendars",
        headers=headers,
        params={
            "$select": "id,name,owner,canEdit"
        }
    )

    print("SHARED CALENDAR LIST STATUS:", response.status_code)

    if response.status_code != 200:
        print("Failed to list calendars:", response.text)
        return None

    calendars = response.json().get("value", [])
    target_email = owner_email.strip().lower()

    shared_calendar = next(
        (
            calendar
            for calendar in calendars
            if calendar.get("owner", {})
            .get("address", "")
            .lower() == target_email
        ),
        None
    )

    if not shared_calendar:
        print("Shared calendar not found:", owner_email)
        return None

    if not shared_calendar.get("canEdit", False):
        print("Calendar is shared, but edit permission is not available.")

    calendar_id = shared_calendar["id"]

    # Read events from that specific shared calendar.
    events_response = requests.get(
        f"https://graph.microsoft.com/v1.0/me/calendars/{calendar_id}/calendarView",
        headers=headers,
        params={
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "$select": "subject,start,end",
            "$orderby": "start/dateTime"
        }
    )

    print("SHARED CALENDAR READ STATUS:", events_response.status_code)

    if events_response.status_code != 200:
        print("Failed to read shared calendar:", events_response.text)
        return None

    return events_response.json().get("value", [])
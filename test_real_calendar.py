from graph_auth import result
from graph_calendar import get_calendar_events


if "access_token" not in result:

    print("Microsoft Graph authentication failed.")
    exit()


events = get_calendar_events(
    result["access_token"],
    "2026-10-12T00:00:00",
    "2026-10-17T00:00:00"
)


print("\nREAL OUTLOOK CALENDAR EVENTS")
print("-----------------------------")


if not events:

    print("No calendar events found.")

else:

    for event in events:

        print("\nSubject:", event.get("subject"))

        print(
            "Start:",
            event.get("start", {}).get("dateTime")
        )

        print(
            "End:",
            event.get("end", {}).get("dateTime")
        )
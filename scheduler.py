from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# --------------------------------------------------
# Working hours in each team's LOCAL timezone
# --------------------------------------------------

WORKING_HOURS = {
    "Chennai": [
        ("09:00", "13:00"),
        ("14:30", "18:00")
    ],
    "London": [
        ("09:00", "13:00"),
        ("14:30", "18:00")
    ]
}


# --------------------------------------------------
# Team timezones
# --------------------------------------------------

TEAM_TIMEZONES = {
    "Chennai": "Asia/Kolkata",
    "London": "Europe/London"
}


# --------------------------------------------------
# Get Monday-Friday of NEXT WEEK
# --------------------------------------------------

def get_next_week_dates():

    today = datetime.now().date()

    # Monday of next week
    next_monday = today + timedelta(
        days=(7 - today.weekday())
    )

    next_week_dates = {}

    for offset in range(5):

        date = next_monday + timedelta(
            days=offset
        )

        day_name = date.strftime("%A")

        next_week_dates[day_name] = date

    return next_week_dates


# --------------------------------------------------
# Convert team local time to IST
# --------------------------------------------------

def convert_to_ist(team, time_string, date):

    local_timezone = ZoneInfo(
        TEAM_TIMEZONES[team]
    )

    ist_timezone = ZoneInfo(
        "Asia/Kolkata"
    )

    local_datetime = datetime.strptime(
        f"{date} {time_string}",
        "%Y-%m-%d %H:%M"
    )

    local_datetime = local_datetime.replace(
        tzinfo=local_timezone
    )

    ist_datetime = local_datetime.astimezone(
        ist_timezone
    )

    return (
        ist_datetime.hour * 60
        + ist_datetime.minute
    )


# --------------------------------------------------
# Convert HH:MM to minutes
# --------------------------------------------------

def time_to_minutes(time_string):

    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


# --------------------------------------------------
# Convert minutes to HH:MM
# --------------------------------------------------

def minutes_to_time(total_minutes):

    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60

    return f"{hours:02d}:{minutes:02d}"


# --------------------------------------------------
# Check calendar availability
# --------------------------------------------------

def is_time_available(
    email,
    day,
    start_time,
    end_time,
    calendar_events
):

    start = time_to_minutes(start_time)
    end = time_to_minutes(end_time)

    events = calendar_events.get(
        email,
        {}
    ).get(
        day,
        []
    )

    for event_start, event_end in events:

        busy_start = time_to_minutes(
            event_start
        )

        busy_end = time_to_minutes(
            event_end
        )

        # Check whether the meeting overlaps
        # with an existing calendar event.
        if start < busy_end and end > busy_start:
            return False

    return True


# --------------------------------------------------
# Check whether time is inside team working hours
# --------------------------------------------------

def is_within_working_hours(
    team,
    date,
    start_time,
    end_time
):

    start_minutes = time_to_minutes(
        start_time
    )

    end_minutes = time_to_minutes(
        end_time
    )

    for work_start, work_end in WORKING_HOURS[team]:

        work_start_ist = convert_to_ist(
            team,
            work_start,
            date
        )

        work_end_ist = convert_to_ist(
            team,
            work_end,
            date
        )

        if (
            start_minutes >= work_start_ist
            and end_minutes <= work_end_ist
        ):
            return True

    return False


# --------------------------------------------------
# Find common available slots
# --------------------------------------------------

def find_common_slots(
    participants,
    participant_teams,
    days,
    duration_minutes,
    calendar_events
):

    common_slots = []

    # Get the ACTUAL dates for next week
    next_week_dates = get_next_week_dates()

    print("\nNEXT WEEK BEING CHECKED")
    print("----------------")

    for day in days:

        if day in next_week_dates:

            print(
                day,
                "->",
                next_week_dates[day]
            )


    # Check every day: Monday-Friday
    for day in days:

        if day not in next_week_dates:
            continue

        actual_date = next_week_dates[day]

        date_string = str(actual_date)

        # Check every 30-minute slot
        for hour in range(24):

            for minute in [0, 30]:

                start_minutes = (
                    hour * 60 + minute
                )

                end_minutes = (
                    start_minutes
                    + duration_minutes
                )

                if end_minutes > 24 * 60:
                    continue

                start_time = minutes_to_time(
                    start_minutes
                )

                end_time = minutes_to_time(
                    end_minutes
                )

                all_available = True

                # Check EVERY participant
                for participant in participants:

                    team = participant_teams.get(
                        participant
                    )

                    if not team:
                        all_available = False
                        break

                    # 1. Check calendar
                    if not is_time_available(
                        participant,
                        day,
                        start_time,
                        end_time,
                        calendar_events
                    ):
                        all_available = False
                        break

                    # 2. Check working hours
                    if not is_within_working_hours(
                        team,
                        date_string,
                        start_time,
                        end_time
                    ):
                        all_available = False
                        break

                # If EVERYONE is available
                if all_available:

                    common_slots.append(
                        {
                            "day": day,
                            "date": date_string,
                            "start": start_time,
                            "end": end_time
                        }
                    )

    return common_slots


# --------------------------------------------------
# Create meeting object
# --------------------------------------------------

def create_meeting_event(
    participants,
    selected_slot,
    subject
):

    return {
        "subject": subject,
        "day": selected_slot["day"],
        "date": selected_slot["date"],
        "start": selected_slot["start"],
        "end": selected_slot["end"],
        "participants": participants
    }
def generate_confirmation(
    meeting_event,
    duration_minutes
):

    subject = (
        f"Meeting Scheduled - "
        f"{meeting_event['subject']}"
    )

    body = f"""
Hi,

The meeting has been scheduled successfully.

Meeting: {meeting_event["subject"]}
Date: {meeting_event["date"]}
Day: {meeting_event["day"]}
Time: {meeting_event["start"]} - {meeting_event["end"]} IST
Duration: {duration_minutes} minutes

Participants:
{chr(10).join(meeting_event["participants"])}

The meeting was scheduled automatically by
the AI Meeting Scheduler Agent.

Thanks,
AI Meeting Scheduler Agent
"""

    return {
        "subject": subject,
        "body": body
    }
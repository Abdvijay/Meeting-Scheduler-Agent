from ollama import chat
import json
import re


def understand_email(email):
    prompt = f"""
You are an AI meeting scheduling assistant.

Analyze the email and return these fields:
- is_meeting_request: boolean
- duration_minutes: integer
- date_range: string
- purpose: string

Rules:
1. A meeting request asks to arrange or schedule a meeting.
2. If no duration is specified, use 30 minutes.
3. If no date range is specified, use "not specified".
4. Use a short description of the meeting as the purpose.
5. For a non-meeting email, return false, 0, "", "".
6. Return valid JSON only.

Email:
From: {email["from"]}
To: {email["to"]}
Subject: {email["subject"]}
Body:
{email["body"]}
"""

    response = chat(
        model="qwen3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    content = response.message.content

    content = re.sub(
        r"<think>.*?</think>",
        "",
        content,
        flags=re.DOTALL
    ).strip()

    result = json.loads(content)

    # Trust the actual email headers, not AI-generated addresses.
    result["sender"] = email["from"].strip().lower()
    result["recipient"] = email["to"].strip().lower()

    return result
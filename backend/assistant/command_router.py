import datetime
from assistant.ai_engine import ask_ai
from assistant.mongo import db

def save_to_db(user_text, response_text):
    db.conversations.insert_one({
        "user_input": user_text,
        "response": response_text,
        "timestamp": datetime.datetime.utcnow()
    })

def route_command(text: str) -> str:
    text_lower = text.lower()

    # TIME / DATE
    if "time" in text_lower or "date" in text_lower:
        now = datetime.datetime.now()
        response = now.strftime(
            "Today is %A, %d %B %Y and the time is %I:%M %p."
        )

    # GREETING
    elif "hello" in text_lower or "hi" in text_lower:
        response = "Hello I am ThingOne. How can I help you?"

    # FALLBACK → AI
    else:
        response = ask_ai(text)

    save_to_db(text, response)
    return response

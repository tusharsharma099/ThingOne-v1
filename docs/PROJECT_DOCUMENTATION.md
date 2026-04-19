# ThingOne AI — Project Documentation

## Project Overview

ThingOne AI is a web-based voice-first assistant built with Django (backend), MongoDB (chat storage), and an LLM-driven AI engine. The app supports voice and text interactions, JWT authentication, per-user chat histories stored in MongoDB, and a web UI for login, signup, and chat.

## Tech Stack

- **Backend:** Python, Django 6.x
- **AI Client:** OpenAI-style client (configured in `assistant/ai_engine.py`)
- **Database:** MongoDB (primary) with an in-memory fallback in `assistant/mongo.py` for development
- **Auth:** JWT via `djangorestframework_simplejwt`
- **Frontend:** HTML/CSS/JS templates under `assistant/templates/assistant`

## Repo Layout (key files)

- [backend/manage.py](backend/manage.py)
- [backend/backend/settings.py](backend/backend/settings.py)
- [backend/.env](backend/.env)
- [backend/assistant/__init__.py](backend/assistant/__init__.py)
- [backend/assistant/views.py](backend/assistant/views.py)
- [backend/assistant/ai_engine.py](backend/assistant/ai_engine.py)
- [backend/assistant/mongo.py](backend/assistant/mongo.py)
- [backend/assistant/urls.py](backend/assistant/urls.py)
- [backend/assistant/command_router.py](backend/assistant/command_router.py)
- [backend/requirements.txt](backend/requirements.txt)
- [docs/vision.md](docs/vision.md)

## High-level Architecture

- HTTP requests are handled by Django. The project's root URL config (in `backend/backend/urls.py`) includes the `assistant` app's URLs.
- The `assistant` app provides both HTML page views (home, login, signup) and JSON API endpoints (JWT login, ask API, chat management).
- Chat history and application-level stats live in MongoDB (`assistant/mongo.py`). If MongoDB is unavailable, an in-memory fallback is used during development.
- The AI interactions are routed through `assistant/ai_engine.py` which instantiates an `OpenAI` client and exposes `ask_ai(prompt)`.
- `assistant/command_router.py` provides simple routing logic for localized commands (time, greeting), falling back to the AI engine.

## assistant app — Components

- `views.py` — Primary HTTP and API views
  - `JWTLogin(APIView).post(...)` — Accepts `email` and `password`, authenticates via Django `User`, returns JWT `access` and `refresh` tokens.
  - Page views: `home_page`, `login_page`, `signup_page`, `logout_user`.
  - Chat APIs (JWT protected via DRF `IsAuthenticated`):
    - `POST /api/ask/` — `ask_api` (main AI chat endpoint). Body: `{"message": "...", "chat_id": "optional"}`. Returns `{"reply": "...", "chat_id": "..."}`.
    - `GET/POST /api/chats/` — `user_chats_api` (list user chats).
    - `GET /api/chat/<chat_id>/` — `chat_messages_api` (messages for a chat).
    - `POST /api/chat/<chat_id>/delete/` — `delete_chat_api`.
  - Note: Views save chat messages via helper functions imported from `assistant.mongo`.

- `ai_engine.py` — LLM client wrapper
  - Loads `OPENAI_API_KEY` from environment and initializes `OpenAI(api_key=...)`.
  - Exposes `ask_ai(prompt: str) -> str` which calls `client.chat.completions.create(...)` using model `gpt-4o-mini` and returns the assistant text.
  - Includes simple debug prints and a `__main__` test harness.

- `mongo.py` — MongoDB helpers and in-memory fallback
  - Connects to `MONGO_URI` from `backend/.env`.
  - Collections used: `chats`, `user_stats` (and command_router uses `conversations` in some flow).
  - Key helpers: `create_new_chat`, `add_message`, `get_user_chats`, `get_chat_messages`, `delete_chat`, `delete_all_user_chats`, `get_message_count`, `increment_message_count`.
  - The message limit logic is implemented here and used by `views.ask_api`.

- `command_router.py` — Lightweight input router
  - `route_command` handles simple intents (time, greeting) and delegates to `ask_ai` for fallbacks.
  - Saves routed exchanges into a `conversations` collection via `save_to_db`.

## Important Behavioral Details

- Message limits: Non-admin users are limited to 10 messages (checked in `views.ask_api` using `get_message_count`/`increment_message_count`). The admin email override is `tusharsharma0991@gmail.com` in `views.py`.
- Chat context: `ask_api` builds a prompt from the last 5 messages for context before calling `ask_ai`.
- Authentication: JWT tokens are created with DRF SimpleJWT in `JWTLogin`. DRF and SimpleJWT are enabled in `backend/backend/settings.py`.

## Environment & Secrets

Required environment variables (stored in `backend/.env` during development):

- `MONGO_URI` — MongoDB connection string.
- `OPENAI_API_KEY` — API key for the LLM provider.
- `SECRET_KEY` — Django secret key (in `backend/backend/settings.py` a default exists; replace in production).

Example `.env` (DO NOT commit real keys):

```
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.example.mongodb.net/?retryWrites=true&w=majority
OPENAI_API_KEY=sk-xxxxxx
SECRET_KEY=replace-this-for-production
DEBUG=True
```

Security note: Remove or rotate any real keys leaked in the repository. The repo currently contains `backend/.env` with a sample `OPENAI_API_KEY` and `MONGO_URI` — treat these as secrets and rotate them.

## Setup & Installation (Development)

1. Create virtual environment and activate:

```
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```
pip install -r backend/requirements.txt
```

3. Create/verify `.env` (see Environment section).

4. Run Django migrations and start the server:

```
cd backend
python manage.py migrate
python manage.py runserver
```

5. Open `http://127.0.0.1:8000/` and use the UI to signup/login.

## Running Key Functionality

- JWT login: `POST /api/jwt/login/` with JSON `{ "email": "...", "password": "..." }`.
- Ask AI: `POST /api/ask/` with headers `Authorization: Bearer <access_token>` and JSON `{ "message": "...", "chat_id": "optional" }`.

## Tests & Development Workflow

- There is a simple `assistant/tests.py` placeholder; expand with unit tests for `mongo` helpers, `ai_engine.ask_ai` (mock the LLM client), and `views` (DRF test client + JWT flows).
- Recommended test strategy:
  - Unit tests for `assistant/mongo.py` using the in-memory fallback.
  - Mock `OpenAI` client in `assistant/ai_engine.py` to assert prompt formatting.
  - Integration tests for `views.ask_api` validating the message limit logic and chat creation.

## Deployment Notes

- The project is prepared for containerized deployments. Common production steps:
  - Use an actual MongoDB Atlas cluster and set `MONGO_URI` accordingly.
  - Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
  - Use a production WSGI server such as `gunicorn backend.wsgi`.
  - Ensure secrets are injected via environment variables or a secrets manager; never commit `.env`.

## Contributing

- Fork the repo, create a feature branch, and submit a pull request with tests.
- Keep secret keys out of commits.
- Add or update `docs/PROJECT_DOCUMENTATION.md` when changing behavior, endpoints, or configuration.

## Troubleshooting

- MongoDB connection errors: Verify `MONGO_URI`, network access, and that Atlas allows your IP.
- LLM/API errors: Confirm `OPENAI_API_KEY` validity and consumption limits. Add retries if needed.
- Authentication issues: Ensure user exists in Django `auth_user` table, and that JWT tokens are created and sent with requests.

## Appendix — Quick File Map

- Pages & URLs: [backend/assistant/urls.py](backend/assistant/urls.py)
- Core APIs & Page handlers: [backend/assistant/views.py](backend/assistant/views.py)
- LLM client wrapper: [backend/assistant/ai_engine.py](backend/assistant/ai_engine.py)
- Mongo helpers & in-memory fallback: [backend/assistant/mongo.py](backend/assistant/mongo.py)
- Simple command routing: [backend/assistant/command_router.py](backend/assistant/command_router.py)
- Settings: [backend/backend/settings.py](backend/backend/settings.py)

---

If you'd like, I can now:
- Expand the API reference with request/response examples for each endpoint.
- Add a small `curl`/Postman collection and example front-end usage snippets.
- Generate unit tests for the `mongo` helpers and `ask_api` flow.

Tell me which of the above you'd like next, and I'll continue. 

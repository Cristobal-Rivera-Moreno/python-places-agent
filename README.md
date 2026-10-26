# Python Places Agent

A FastAPI backend that powers a conversational **tourist guide** ("J.A.R.V.I.S."). It uses Google Gemini with function calling: when a user asks about nearby places, the model calls a Google Maps Places tool and replies with a short, friendly, markdown-formatted list including star ratings and open/closed status.

## Features

- Chat endpoint (`POST /api/chat`) with optional conversation history.
- Gemini (`gemini-2.0-flash`) automatic function calling against the Google Maps Places Nearby Search API.
- Location-aware: the user's latitude/longitude are injected into the system prompt.
- Bilingual (English / Spanish) persona with strict rules: answers under 100 words, markdown bullets, star-icon ratings, and refusal of off-topic questions.
- Simple bearer-token check so only the companion Tourist Guide chat client can call the API.
- An alternative OpenStreetMap (Overpass) lookup tool, currently not wired into the agent.

## Tech stack

| Area | Library |
| --- | --- |
| Web framework / server | FastAPI, Uvicorn |
| LLM | `google-genai` (Gemini) |
| Places data | `googlemaps` (Google Places), `overpy` (OpenStreetMap Overpass) |
| Config | `pydantic-settings`, `python-dotenv` |
| Packaging | [uv](https://docs.astral.sh/uv/), Python 3.12+ |

## Project structure

```
.
├── main.py                        # Entry point: starts Uvicorn with the FastAPI app
├── routes/
│   └── routes.py                  # FastAPI app and the /api/chat endpoint
├── tools/
│   ├── google_places_api.py       # Gemini tool: Google Places nearby search
│   └── open_maps_api.py           # Overpass (OSM) amenity lookup (unused by the agent)
├── prompts/
│   └── tourist_guide_prompt.py    # System prompt builder (persona, rules, location)
├── dto/
│   └── models.py                  # Pydantic models: ChatRequest, ChatMessage
├── models/
│   └── settings.py                # Environment-based settings (API keys)
├── pyproject.toml                 # Dependencies and project metadata
└── uv.lock                        # Locked dependency versions
```

## How it works

1. The client sends a message, the user's coordinates, and optionally prior chat history to `POST /api/chat`.
2. The server checks the `Authorization` header.
3. A Gemini chat session is created with:
   - the system prompt from `get_tourist_guide_prompt(lat, lon)`,
   - the `get_nearby_places` tool (exposed to the model as a Python function),
   - any prior history converted to Gemini `Content` objects.
4. Gemini decides whether to call the tool. `get_nearby_places(amenity, lat, lon, radius=1000)` queries Google Places and returns up to 5 results (name, address, rating, open-now) as text.
5. Gemini composes the final answer, returned as `{"agent_response": "..."}`.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (or pip)
- A **Gemini API key** ([Google AI Studio](https://aistudio.google.com/))
- A **Google Maps Platform API key** with the Places API enabled

## Setup

```bash
# Install dependencies
uv sync

# Create the environment file
cat > .env <<'EOF'
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
EOF
```

Settings are loaded by `pydantic-settings` from `.env` (see [models/settings.py](models/settings.py)). Both variables are required; the app fails to start without them.

## Running

```bash
uv run python main.py
```

By default [main.py](main.py) binds Uvicorn to a fixed host (`10.30.0.72`) on port `8000`. Change the host to `127.0.0.1` or `0.0.0.0` to run on your own machine. Alternatively:

```bash
uv run uvicorn routes:app --reload --port 8000
```

Interactive API docs are available at `http://<host>:8000/docs`.

## API

### `POST /api/chat`

**Headers**

| Header | Value |
| --- | --- |
| `Authorization` | `Bearer <app token>` (see [routes/routes.py](routes/routes.py)) |
| `Content-Type` | `application/json` |

**Body** (see [dto/models.py](dto/models.py))

```json
{
  "userId": "user-123",
  "message": { "role": "user", "content": "What are some good pharmacies near me?" },
  "lat": 21.9167,
  "long": -102.3069,
  "chatHistory": [
    { "role": "user", "content": "Hi!" },
    { "role": "model", "content": "¡Hola! How can I help you today?" }
  ]
}
```

- `lat` / `long` default to Aguascalientes, Mexico (`21.9167, -102.3069`).
- `chatHistory` is optional. Roles follow Gemini's convention (`user` / `model`).

**Response**

```json
{ "agent_response": "**Aguascalientes**\n- **Farmacia X** ⭐⭐⭐⭐☆ ..." }
```

**Errors**

| Status | Cause |
| --- | --- |
| 401 | Missing or invalid `Authorization` header |
| 500 | Gemini / Places API failure (message in `detail`) |

**Example**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $APP_CHAT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "userId": "demo",
        "message": {"role": "user", "content": "Good coffee shops nearby?"},
        "lat": 21.9167,
        "long": -102.3069
      }'
```

## Known limitations and security notes

This project is an early prototype (v0.1.0). Before deploying it, address the following:

- **Hardcoded secrets.** [main.py](main.py) contains a hardcoded Gemini API key and [routes/routes.py](routes/routes.py) contains the hardcoded bearer token. Remove the key from `main.py` (the client there is unused), **rotate that key**, and load the bearer token from the environment.
- **`.env` is not in `.gitignore`.** Add `.env` so API keys are never committed.
- **Request validation.** The endpoint reads the raw JSON body instead of using the `ChatRequest` model, so FastAPI does not validate input. Typing the parameter as `ChatRequest` would fix this.
- **Chat history is not persisted.** Each request builds a fresh session from the `chatHistory` the client sends; the module-level `history` dict is unused.
- **Blocking calls in an async handler.** The Gemini and Google Maps calls are synchronous inside an `async def`, which blocks the event loop under load.
- **Unused code.** `tools/open_maps_api.py` is not connected to the agent and does not return its results.
- **Tool coverage.** Only Google Places nearby search is exposed, limited to 5 results within a default 1 km radius.
- **No tests** are included yet.

## License

No license specified.

# KeyRotator

A plug-and-play API key rotation mechanism for FastAPI projects, extracted from the TeachingMonsterAI project.

## Features

- **Key Pool Management**: Manage multiple API keys per provider with automatic rotation
- **Health Monitoring**: Tracks key health, rate limits, and usage statistics
- **Dashboard**: Web UI for monitoring and manually reviving keys
- **Provider Agnostic**: Works with any API provider (Gemini, OpenAI, etc.)
- **Thread-Safe**: Safe for concurrent use

## Quick Start

1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your API keys in `app.py`
4. Run: `uvicorn app:app --reload`
5. Access dashboard: http://localhost:8000/dev/pool-status/ui

## Integration into Your Project

```python
from fastapi import FastAPI
from keyrotator import KeyPool, KeyRotatorRouter

app = FastAPI()

# Create key pools for your providers
gemini_pool = KeyPool("gemini", keys=["your-gemini-key1", "your-gemini-key2"])
openai_pool = KeyPool("openai", keys=["sk-your-openai-key"])

# Include the router
app.include_router(
    KeyRotatorRouter([gemini_pool, openai_pool]),
    prefix="/dev"
)
```

## API Endpoints

- `GET /dev/pool-status` - JSON status of all pools
- `POST /dev/pool-status/revive` - Manually revive a spent/dead key
- `GET /dev/pool-status/ui` - HTML dashboard

## Key States

- **HEALTHY**: Key is working normally
- **RATE_LIMITED**: Temporarily blocked due to 429 errors
- **SPENT**: Exhausted (402) - requires manual revive
- **DEAD**: Invalid/auth error (403) - requires manual revive

## License

Extracted from TeachingMonsterAI project.
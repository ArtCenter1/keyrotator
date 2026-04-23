"""
Standalone KeyRotator Application

This is a standalone version of the KeyRotator mechanism extracted from TeachingMonsterAI.
It provides API key rotation and a dashboard for monitoring key pools.

Usage:
    1. Configure your API keys in pools below.
    2. Run with: uvicorn app:app --reload
    3. Access dashboard at: http://localhost:8000/dev/pool-status/ui

To integrate into another project:
    from keyrotator import KeyPool, KeyRotatorRouter

    # Create your pools
    gemini_pool = KeyPool("gemini", keys=["your-gemini-keys"])
    openai_pool = KeyPool("openai", keys=["your-openai-keys"])

    # Include in your FastAPI app
    app.include_router(KeyRotatorRouter([gemini_pool, openai_pool]), prefix="/dev")
"""

from fastapi import FastAPI
from keyrotator import KeyPool, KeyRotatorRouter

# Configure your API key pools here
# Replace with your actual keys
gemini_keys = ["AIzaSy..."]  # Add your Gemini API keys
openrouter_keys = ["sk-or-..."]  # Add your OpenRouter API keys

# Create key pools
gemini_pool = KeyPool("gemini", keys=gemini_keys)
openrouter_pool = KeyPool("openrouter", keys=openrouter_keys)

# Create FastAPI app
app = FastAPI(title="KeyRotator Standalone")

# Include the KeyRotator router
app.include_router(KeyRotatorRouter([gemini_pool, openrouter_pool]), prefix="/dev")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

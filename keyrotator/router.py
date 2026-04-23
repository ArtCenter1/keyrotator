from __future__ import annotations
import json
import os
import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from loguru import logger

from keyrotator.pool import KeyPool
from keyrotator.config import ConfigManager, ProviderConfig, KeyConfig
import httpx


class ReviveRequest(BaseModel):
    provider: str
    key_index: int


class AddKeyRequest(BaseModel):
    provider: str
    key: str
    alias: str = None


class UpdateProviderRequest(BaseModel):
    provider: str
    enabled: bool = None
    rate_limit_per_minute: int = None


class KeyRotatorRouter:
    """Enhanced router with configuration management."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._pools: Dict[str, KeyPool] = {}
        self._load_pools()

    def _load_pools(self):
        """Load or create key pools from configuration."""
        config = self.config_manager.load()

        for provider_name, provider_config in config.providers.items():
            if provider_config.enabled:
                keys = self.config_manager.get_keys_for_provider(provider_name)
                if keys:  # Only create pool if there are keys
                    self._pools[provider_name] = KeyPool(
                        provider=provider_name,
                        keys=keys,
                        rate_limit_quarantine_sec=60,
                        spend_cap_quarantine_sec=0,
                    )

    def get_router(self) -> APIRouter:
        """
        Get the configured APIRouter with all endpoints.
        """
        router = APIRouter(tags=["keyrotator"])

        async def _get_ngrok_url():
            """Attempt to fetch the public tunnel URL from the ngrok sidecar."""
            try:
                async with httpx.AsyncClient(timeout=0.5) as client:
                    r = await client.get("http://ngrok:4040/api/tunnels")
                    if r.status_code == 200:
                        data = r.json()
                        tunnels = data.get("tunnels", [])
                        if tunnels:
                            return tunnels[0].get("public_url")
            except Exception:
                pass
            return None

        @router.get("/dashboard", response_class=HTMLResponse)
        async def get_dashboard():
            """Serve the main dashboard."""
            config = self.config_manager.load()
            status_data = [pool.get_status() for pool in self._pools.values()]
            public_url = await _get_ngrok_url()

            status_json = json.dumps(
                {
                    "pools": status_data,
                    "public_url": public_url,
                    "providers": [
                        {
                            "name": p.name,
                            "display_name": p.display_name,
                            "description": p.description,
                            "enabled": p.enabled,
                            "key_count": len(
                                [
                                    k
                                    for k in config.keys
                                    if k.provider == p.name and k.enabled
                                ]
                            ),
                        }
                        for p in config.providers.values()
                    ],
                    "is_development": self.config_manager.is_development_mode(),
                }
            )

            html = self._render_dashboard(status_json)
            return HTMLResponse(content=html)

        @router.get("/status")
        async def get_status():
            """Get JSON status of all pools."""
            status_data = [pool.get_status() for pool in self._pools.values()]
            public_url = await _get_ngrok_url()

            return {
                "pools": status_data,
                "public_url": public_url,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "is_development": self.config_manager.is_development_mode(),
            }

        @router.post("/revive")
        async def revive_key(body: ReviveRequest):
            """Manually revive a SPENT/DEAD key."""
            pool = self._pools.get(body.provider)
            if pool is None:
                raise HTTPException(
                    status_code=404, detail=f"Provider '{body.provider}' not found"
                )

            success = pool.revive(body.key_index)
            if not success:
                raise HTTPException(
                    status_code=400, detail=f"Invalid key index {body.key_index}"
                )

            logger.info(
                f"[keyrotator] Revived {body.provider} key #{body.key_index} via dashboard"
            )
            return {
                "ok": True,
                "message": f"Key #{body.key_index} revived for {body.provider}",
            }

        @router.get("/config")
        async def get_config():
            """Get current configuration."""
            config = self.config_manager.load()
            return {
                "providers": {
                    name: {
                        "name": p.name,
                        "display_name": p.display_name,
                        "description": p.description,
                        "default_model": p.default_model,
                        "rate_limit_per_minute": p.rate_limit_per_minute,
                        "enabled": p.enabled,
                        "key_count": len(
                            [k for k in config.keys if k.provider == name and k.enabled]
                        ),
                    }
                    for name, p in config.providers.items()
                },
                "keys": [
                    {
                        "provider": k.provider,
                        "alias": k.alias,
                        "enabled": k.enabled,
                        "index": i,
                    }
                    for i, k in enumerate(config.keys)
                ],
                "is_development": self.config_manager.is_development_mode(),
            }

        @router.post("/keys")
        async def add_key(body: AddKeyRequest):
            """Add a new API key."""
            config = self.config_manager.load()

            # Validate provider exists
            if body.provider not in config.providers:
                raise HTTPException(
                    status_code=400, detail=f"Unknown provider: {body.provider}"
                )

            # Add key to config
            self.config_manager.add_key(body.provider, body.key, body.alias)

            # Reload pools to include new key
            self._load_pools()

            return {"ok": True, "message": f"Key added to {body.provider}"}

        @router.delete("/keys/{provider}/{key_index}")
        async def remove_key(provider: str, key_index: int):
            """Remove an API key."""
            success = self.config_manager.remove_key(provider, key_index)
            if not success:
                raise HTTPException(status_code=404, detail="Key not found")

            # Reload pools
            self._load_pools()

            return {"ok": True, "message": f"Key removed from {provider}"}

        @router.put("/providers/{provider}")
        async def update_provider(provider: str, body: UpdateProviderRequest):
            """Update provider configuration."""
            config = self.config_manager.load()
            if provider not in config.providers:
                raise HTTPException(
                    status_code=404, detail=f"Provider '{provider}' not found"
                )

            update_data = body.dict(exclude_unset=True)
            self.config_manager.update_provider_config(provider, **update_data)

            # Reload pools if provider was enabled/disabled
            if "enabled" in update_data:
                self._load_pools()

            return {"ok": True, "message": f"Provider {provider} updated"}

        return router

    def _render_dashboard(self, initial_json: str) -> str:
        """Read and return the dashboard HTML template with injected data."""
        import os

        template_path = os.path.join(os.path.dirname(__file__), "dashboard.html")

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()

            # Replace the placeholder with actual data
            try:
                json_data = json.dumps(initial_json)
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to serialize dashboard data: {e}")
                json_data = json.dumps({"error": "Data serialization failed"})

            return template.replace("{initial_json}", json_data)
        except FileNotFoundError:
            # Fallback to a simple dashboard if template file is missing
            return f"""<!DOCTYPE html>
<html>
<head><title>KeyRotator Dashboard</title></head>
<body>
<h1>KeyRotator Dashboard</h1>
<p>Dashboard template not found. Please check installation.</p>
<pre>{json.dumps(initial_json, indent=2)}</pre>
</body>
</html>"""

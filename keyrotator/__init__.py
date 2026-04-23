"""
KeyRotator — Professional API Key Management Dashboard

A plug-and-play API key rotation system for development environments.
Manage multiple API keys across providers with automatic rotation, health monitoring,
and a comprehensive mission control dashboard.

Features:
- Dynamic key management via web dashboard
- Automatic rotation and failover
- Real-time health monitoring and analytics
- Provider-agnostic architecture
- Configuration persistence
- Development-mode detection

Usage:
    from keyrotator import KeyRotatorApp

    # Create and run the dashboard
    app = KeyRotatorApp()
    app.run()

    # Or integrate into existing FastAPI app
    from keyrotator import KeyRotatorRouter, ConfigManager

    config = ConfigManager()
    app.include_router(KeyRotatorRouter(config), prefix="/keyrotator")
"""

from keyrotator.pool import KeyPool, KeyEntry, KeyState, AllKeysExhaustedError
from keyrotator.router import KeyRotatorRouter
from keyrotator.config import ConfigManager, KeyRotatorConfig, ProviderConfig, KeyConfig
from keyrotator.app import KeyRotatorApp

__all__ = [
    "KeyPool",
    "KeyEntry",
    "KeyState",
    "AllKeysExhaustedError",
    "KeyRotatorRouter",
    "ConfigManager",
    "KeyRotatorConfig",
    "ProviderConfig",
    "KeyConfig",
    "KeyRotatorApp",
]

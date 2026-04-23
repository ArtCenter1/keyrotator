"""
Configuration management for KeyRotator
Handles API key storage, provider configuration, and persistence.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import base64


@dataclass
class ProviderConfig:
    """Configuration for an API provider."""

    name: str
    display_name: str
    description: str
    default_model: str
    rate_limit_per_minute: int = 15
    base_url: Optional[str] = None
    api_version: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class KeyConfig:
    """Configuration for an API key."""

    provider: str
    key: str
    alias: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KeyRotatorConfig:
    """Main configuration for KeyRotator."""

    version: str = "1.0.0"
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    keys: List[KeyConfig] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Initialize default providers if empty
        if not self.providers:
            self._init_default_providers()

    def add_provider(self, provider_config: ProviderConfig):
        """Add or update a provider configuration."""
        self.providers[provider_config.name] = provider_config

    def remove_provider(self, provider_name: str):
        """Remove a provider configuration."""
        if provider_name in self.providers:
            del self.providers[provider_name]
            # Also remove associated keys
            self.keys = [k for k in self.keys if k.provider != provider_name]

    def _init_default_providers(self):
        """Initialize default provider configurations."""
        self.providers = {
            "gemini": ProviderConfig(
                name="gemini",
                display_name="Google Gemini",
                description="Google's Gemini AI models with free tier",
                default_model="gemini-1.5-flash",
                rate_limit_per_minute=15,
                base_url="https://generativelanguage.googleapis.com",
            ),
            "openrouter": ProviderConfig(
                name="openrouter",
                display_name="OpenRouter",
                description="Unified API for multiple AI providers",
                default_model="openai/gpt-3.5-turbo",
                rate_limit_per_minute=50,
                base_url="https://openrouter.ai/api/v1",
            ),
            "kilo": ProviderConfig(
                name="kilo",
                display_name="Kilo AI",
                description="Kilo's AI models",
                default_model="kilo-model",
                rate_limit_per_minute=30,
            ),
            "kimi": ProviderConfig(
                name="kimi",
                display_name="Kimi AI",
                description="Moonshot AI's Kimi models",
                default_model="kimi-model",
                rate_limit_per_minute=30,
            ),
            "nvidia-nim": ProviderConfig(
                name="nvidia-nim",
                display_name="NVIDIA NIM",
                description="NVIDIA's NIM inference microservices",
                default_model="nvidia-nim-model",
                rate_limit_per_minute=60,
            ),
        }


class ConfigManager:
    """Manages KeyRotator configuration persistence."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or self._get_default_config_path())
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[KeyRotatorConfig] = None

    def _get_default_config_path(self) -> str:
        """Get default config file path."""
        # Check for project-specific config first
        project_config = Path(".keyrotator/config.json")
        if project_config.exists():
            return str(project_config)

        # Fall back to user config
        user_config = Path.home() / ".keyrotator" / "config.json"
        return str(user_config)

    def load(self) -> KeyRotatorConfig:
        """Load configuration from file."""
        if self._config is not None:
            return self._config

        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                self._config = KeyRotatorConfig(**data)
            except Exception as e:
                print(f"Warning: Failed to load config {self.config_path}: {e}")
                self._config = KeyRotatorConfig()
        else:
            self._config = KeyRotatorConfig()

        return self._config

    def save(self) -> None:
        """Save configuration to file."""
        if self._config is None:
            return

        # Convert to dict for JSON serialization
        data = {
            "version": self._config.version,
            "providers": {
                name: {
                    "name": p.name,
                    "display_name": p.display_name,
                    "description": p.description,
                    "default_model": p.default_model,
                    "rate_limit_per_minute": p.rate_limit_per_minute,
                    "base_url": p.base_url,
                    "api_version": p.api_version,
                    "headers": p.headers,
                    "enabled": p.enabled,
                }
                for name, p in self._config.providers.items()
            },
            "keys": [
                {
                    "provider": k.provider,
                    "key": self._encrypt_key(k.key),
                    "alias": k.alias,
                    "enabled": k.enabled,
                    "metadata": k.metadata,
                }
                for k in self._config.keys
            ],
            "settings": self._config.settings,
        }

        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def _encrypt_key(self, key: str) -> str:
        """
        Simple obfuscation for API keys (NOT true encryption).

        SECURITY WARNING:
        This provides minimal protection against casual inspection only.
        Keys are obfuscated using XOR with a fixed key and should NEVER be
        considered secure. This is designed for development environments only.

        For production use, implement proper encryption using libraries like
        `cryptography` with user-provided keys or secure key management systems.

        The obfuscation prevents accidental exposure in logs or casual file viewing,
        but determined attackers can easily reverse this.
        """
        # In production, use proper encryption with user-provided keys
        # This is just to avoid plain text storage in development
        key_bytes = key.encode()
        # Simple XOR with a fixed key for obfuscation
        xor_key = b"keyrotator_salt_2024"
        encrypted = bytes(
            a ^ b
            for a, b in zip(key_bytes, xor_key * (len(key_bytes) // len(xor_key) + 1))
        )
        return base64.b64encode(encrypted).decode()

    def _decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt obfuscated API key."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_key)
            xor_key = b"keyrotator_salt_2024"
            decrypted = bytes(
                a ^ b
                for a, b in zip(
                    encrypted_bytes,
                    xor_key * (len(encrypted_bytes) // len(xor_key) + 1),
                )
            )
            return decrypted.decode()
        except:
            # If decryption fails, assume it's already plain text (backwards compatibility)
            return encrypted_key

    def add_key(self, provider: str, key: str, alias: Optional[str] = None) -> None:
        """Add a new API key."""
        config = self.load()

        # Check if key already exists
        for existing in config.keys:
            if existing.key == key and existing.provider == provider:
                return  # Already exists

        key_config = KeyConfig(
            provider=provider,
            key=key,
            alias=alias
            or f"Key #{len([k for k in config.keys if k.provider == provider]) + 1}",
        )
        config.keys.append(key_config)
        self.save()

    def remove_key(self, provider: str, key_index: int) -> bool:
        """Remove an API key by index."""
        config = self.load()
        keys_for_provider = [k for k in config.keys if k.provider == provider]

        if 0 <= key_index < len(keys_for_provider):
            # Find the actual index in the main list
            actual_index = config.keys.index(keys_for_provider[key_index])
            config.keys.pop(actual_index)
            self.save()
            return True
        return False

    def get_keys_for_provider(self, provider: str) -> List[str]:
        """Get decrypted keys for a provider."""
        config = self.load()
        keys = [k for k in config.keys if k.provider == provider and k.enabled]
        return [self._decrypt_key(k.key) for k in keys]

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get provider configuration."""
        config = self.load()
        return config.providers.get(provider)

    def update_provider_config(self, provider: str, **kwargs) -> None:
        """Update provider configuration."""
        config = self.load()
        if provider in config.providers:
            for key, value in kwargs.items():
                if hasattr(config.providers[provider], key):
                    setattr(config.providers[provider], key, value)
            self.save()

    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development").lower() in [
            "dev",
            "development",
            "local",
        ]

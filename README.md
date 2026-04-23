# KeyRotator — Mission Control

![KeyRotator](https://img.shields.io/badge/KeyRotator-Mission%20Control-blue?style=for-the-badge&logo=rocket)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Professional API Key Management Dashboard for Development Environments**

KeyRotator is a plug-and-play API key rotation system designed for development and testing environments. It provides a comprehensive mission control dashboard to manage multiple API keys across different providers, with automatic rotation, health monitoring, and real-time analytics.

## 📸 Mission Control Dashboard

![KeyRotator Mission Control Dashboard](https://via.placeholder.com/800x600/0f1419/8b5cf6?text=KeyRotator+Mission+Control+Dashboard)
*Screenshot of the KeyRotator Mission Control dashboard showing real-time key monitoring, provider status, and management interface*

## ✨ Features

### 🔑 **Smart Key Management**
- **Multi-Provider Support**: Gemini, OpenRouter, Kilo, Kimi, NVIDIA NIM, and custom providers
- **Automatic Rotation**: Seamless failover between keys when rate limits or quotas are hit
- **Health Monitoring**: Real-time tracking of key status, usage patterns, and performance metrics
- **Configuration Persistence**: Secure storage of API keys with encryption

### 🎛️ **Mission Control Dashboard**
- **Real-Time Monitoring**: Live status updates and health indicators
- **Interactive Management**: Add, remove, and revive API keys through the web interface
- **Provider Controls**: Enable/disable providers and adjust rate limits
- **Activity Logs**: Historical tracking of key usage and failures
- **Responsive Design**: Works on desktop and mobile devices

### 🛡️ **Developer Experience**
- **Development Mode Detection**: Automatically detects when running in development
- **Thread-Safe Operations**: Safe for concurrent API calls
- **Easy Integration**: Minimal code changes required for existing FastAPI projects
- **Extensible Architecture**: Add support for new providers easily

## 🚀 Quick Start

### Standalone Dashboard

1. **Clone and Install**
   ```bash
   git clone https://github.com/yourusername/keyrotator.git
   cd keyrotator
   pip install -r requirements.txt
   ```

2. **Run Mission Control**
   ```bash
   python app.py
   ```

3. **Access Dashboard**
   - Open: http://localhost:8000/api/dashboard
   - API Docs: http://localhost:8000/docs

4. **Add Your Keys**
   - Use the dashboard to add API keys for your preferred providers
   - Keys are encrypted and stored locally

## 📦 Integration into Fresh Projects

### Option 1: Full KeyRotator Integration

For projects that need complete key management:

```python
from fastapi import FastAPI
from keyrotator import KeyRotatorApp

# Create the KeyRotator app
app = KeyRotatorApp()

# Your app will have KeyRotator endpoints at /api/*
# Dashboard: /api/dashboard
# API: /api/status, /api/keys, etc.
```

### Option 2: Router Integration

For existing FastAPI projects:

```python
from fastapi import FastAPI
from keyrotator import ConfigManager, KeyRotatorRouter

app = FastAPI(title="My Awesome App")

# Initialize KeyRotator config
config_manager = ConfigManager()

# Add KeyRotator router
keyrotator_router = KeyRotatorRouter(config_manager)
app.include_router(keyrotator_router, prefix="/keyrotator")

# Your existing routes...
@app.get("/")
async def root():
    return {"message": "My App with KeyRotator"}

# Access dashboard at: /keyrotator/dashboard
```

### Option 3: Programmatic Key Usage

For direct key rotation in your code:

```python
from keyrotator import ConfigManager, KeyPool

# Get keys for a provider
config = ConfigManager()
gemini_keys = config.get_keys_for_provider("gemini")

# Create a pool
pool = KeyPool("gemini", keys=gemini_keys)

# Use in your API calls
async def call_gemini_api(prompt: str):
    entry = pool.get_key()
    if not entry:
        raise Exception("No healthy Gemini keys available")

    try:
        # Your API call here with entry.key
        response = await call_external_api(entry.key, prompt)
        pool.report_success(entry)
        return response
    except Exception as e:
        pool.report_error(entry, 429, str(e))  # Or appropriate error code
        raise
```

## 🎯 Supported Providers

KeyRotator comes pre-configured for popular AI providers:

| Provider | Display Name | Default Rate Limit | Description |
|----------|-------------|-------------------|-------------|
| `gemini` | Google Gemini | 15 req/min | Google's Gemini AI models |
| `openrouter` | OpenRouter | 50 req/min | Unified API for multiple providers |
| `kilo` | Kilo AI | 30 req/min | Kilo's AI models |
| `kimi` | Kimi AI | 30 req/min | Moonshot AI's Kimi models |
| `nvidia-nim` | NVIDIA NIM | 60 req/min | NVIDIA's inference microservices |

### Adding Custom Providers

```python
from keyrotator import ConfigManager, ProviderConfig

config = ConfigManager()

# Add a custom provider
custom_provider = ProviderConfig(
    name="my-custom-api",
    display_name="My Custom API",
    description="My custom AI service",
    default_model="my-model-v1",
    rate_limit_per_minute=100,
    base_url="https://api.mycustom.ai/v1"
)

config._config.providers["my-custom-api"] = custom_provider
config.save()
```

## 🔧 Configuration

### Environment Variables

```bash
# Force development mode
ENVIRONMENT=development

# Custom config location
KEYROTATOR_CONFIG_PATH=/path/to/config.json
```

### Configuration File

Keys are stored in `~/.keyrotator/config.json` (or project `.keyrotator/config.json`):

```json
{
  "version": "1.0.0",
  "providers": {
    "gemini": {
      "name": "gemini",
      "display_name": "Google Gemini",
      "enabled": true,
      "rate_limit_per_minute": 15
    }
  },
  "keys": [
    {
      "provider": "gemini",
      "key": "encrypted_key_data",
      "alias": "Free Tier Key #1",
      "enabled": true
    }
  ]
}
```

## 📊 Dashboard Features

### Real-Time Monitoring
- **Health Status**: Visual indicators for key health and provider status
- **Usage Metrics**: Requests per minute, success/failure rates
- **Rate Limiting**: Current usage vs limits with progress bars
- **Activity Logs**: Recent key usage and error history

### Key Management
- **Add Keys**: Securely add new API keys with aliases
- **Revive Keys**: Manually reset spent or dead keys
- **Delete Keys**: Remove unused or invalid keys
- **Toggle Providers**: Enable/disable entire providers

### Provider Controls
- **Rate Limit Adjustment**: Modify rate limits per provider
- **Status Toggles**: Enable/disable providers globally
- **Configuration**: View and edit provider settings

## 🔒 Security

- **Encrypted Storage**: API keys are obfuscated using a simple encryption scheme
- **Development Only**: Designed for development environments only
- **No External Calls**: All data stays on your local machine
- **Secure Defaults**: Conservative rate limits and automatic key rotation

## 🐛 Key States

| State | Description | Auto-Recovery | Manual Action Required |
|-------|-------------|---------------|----------------------|
| **HEALTHY** | Working normally | N/A | No |
| **RATE_LIMITED** | Temporary 429 errors | Yes (after cooldown) | No |
| **SPENT** | Quota exhausted (402) | No | Yes - Manual revive |
| **DEAD** | Auth error (403/unknown) | No | Yes - Manual revive |

## 🚦 API Endpoints

### Dashboard
- `GET /api/dashboard` - Main mission control interface

### Status & Monitoring
- `GET /api/status` - JSON status of all pools
- `GET /api/config` - Current configuration

### Key Management
- `POST /api/keys` - Add new API key
- `DELETE /api/keys/{provider}/{index}` - Remove API key
- `POST /api/revive` - Manually revive a key

### Provider Management
- `PUT /api/providers/{provider}` - Update provider settings

## 📈 Use Cases

### Development Teams
- **Shared Keys**: Manage team API keys with usage tracking
- **Quota Management**: Monitor and distribute API quotas
- **Failover Testing**: Test application resilience with key failures

### AI Application Development
- **Multi-Provider Support**: Easily switch between AI providers
- **Cost Optimization**: Use free tiers with automatic fallback
- **Load Balancing**: Distribute requests across multiple keys

### CI/CD Pipelines
- **Automated Testing**: Test with different API configurations
- **Quota Monitoring**: Prevent pipeline failures due to exhausted keys
- **Environment Parity**: Consistent key management across environments

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Adding New Providers

1. Create provider implementation in `keyrotator/providers/`
2. Add provider config in `ConfigManager._init_default_providers()`
3. Test with the dashboard

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Originally extracted from the TeachingMonsterAI project. Enhanced and made into a standalone professional tool for the developer community.

---

**Ready to take control of your API keys?** 🚀

Start with: `pip install keyrotator` (coming soon) or clone this repo!
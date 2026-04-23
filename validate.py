#!/usr/bin/env python3
"""
Simple validation script for KeyRotator
"""


def validate_imports():
    """Validate that all imports work correctly."""
    try:
        from keyrotator.config import ConfigManager, KeyRotatorConfig

        print("✅ Config module imports successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from keyrotator.pool import KeyPool, KeyEntry, KeyState

        print("✅ Pool module imports successful")
    except Exception as e:
        print(f"❌ Pool import failed: {e}")
        return False

    try:
        from keyrotator.router import KeyRotatorRouter

        print("✅ Router module imports successful")
    except Exception as e:
        print(f"❌ Router import failed: {e}")
        return False

    try:
        from keyrotator.app import KeyRotatorApp

        print("✅ App module imports successful")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

    return True


def validate_config():
    """Validate configuration system."""
    try:
        from keyrotator.config import ConfigManager

        config = ConfigManager()
        config_data = config.load()
        print(f"✅ Config loaded with {len(config_data.providers)} providers")
        return True
    except Exception as e:
        print(f"❌ Config validation failed: {e}")
        return False


def validate_template():
    """Validate dashboard template."""
    import os

    template_path = os.path.join(
        os.path.dirname(__file__), "keyrotator", "dashboard.html"
    )
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            content = f.read()
        if "{initial_json}" in content:
            print("✅ Dashboard template found with placeholder")
            return True
        else:
            print("❌ Dashboard template missing placeholder")
            return False
    else:
        print("❌ Dashboard template not found")
        return False


if __name__ == "__main__":
    print("🔍 Validating KeyRotator...")
    print()

    all_good = True
    all_good &= validate_imports()
    all_good &= validate_config()
    all_good &= validate_template()

    print()
    if all_good:
        print("🎉 KeyRotator validation successful!")
        print("🚀 Ready to launch Mission Control")
    else:
        print("⚠️  Some validation checks failed")
        print("Please check the error messages above")

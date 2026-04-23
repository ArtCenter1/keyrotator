"""
Main KeyRotator application with dashboard and API.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

from keyrotator.config import ConfigManager
from keyrotator.router import KeyRotatorRouter


class KeyRotatorApp:
    """Main KeyRotator application class."""

    def __init__(
        self, config_path: str = None, host: str = "0.0.0.0", port: int = 8001
    ):
        # Validate config_path for security
        if config_path:
            import os
            from pathlib import Path

            config_path_obj = Path(config_path).resolve()
            # Ensure the path is absolute and within reasonable bounds
            if not config_path_obj.is_absolute():
                raise ValueError("Config path must be absolute")
            # Prevent directory traversal attacks
            try:
                config_path_obj.relative_to(Path.home())
            except ValueError:
                # Allow paths outside home if they're still reasonable
                if ".." in str(config_path_obj) or not config_path_obj.parent.exists():
                    raise ValueError(
                        "Invalid config path: directory traversal not allowed"
                    )

        self.config_manager = ConfigManager(config_path)
        self.host = host
        self.port = port
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create the FastAPI application."""
        app = FastAPI(
            title="KeyRotator Dashboard",
            description="Professional API Key Management and Rotation System",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Create static directory if it doesn't exist
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)

        # Mount static files
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        # Include the KeyRotator router
        router = KeyRotatorRouter(self.config_manager)
        app.include_router(router, prefix="/api")

        # Add root redirect to dashboard
        @app.get("/")
        async def root():
            return {"message": "KeyRotator Dashboard", "dashboard": "/api/dashboard"}

        return app

    def run(self, reload: bool = True):
        """Run the application."""
        print("Starting KeyRotator Dashboard...")
        print(f"Dashboard: http://localhost:{self.port}/api/dashboard")
        print(f"API Docs: http://localhost:{self.port}/docs")
        print(f"Config: {self.config_manager.config_path}")

        uvicorn.run(
            "keyrotator.app:create_app",
            host=self.host,
            port=self.port,
            reload=reload,
            reload_dirs=["."],
            log_level="info",
            factory=True,
        )


# Global app instance for uvicorn
app_instance = None


def create_app():
    """Factory function for creating the app (used by uvicorn)."""
    global app_instance
    if app_instance is None:
        app_instance = KeyRotatorApp()
    return app_instance.app

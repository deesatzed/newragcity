"""
DKR Server entry point for Docker deployment.

This module provides the server entry point for running the DKR service
in a Docker container as part of the newragcity unified system.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Start the DKR FastAPI server using uvicorn."""
    import uvicorn
    from src.main import agent_os_app

    if agent_os_app is None:
        print("ERROR: Failed to initialize DKR application")
        sys.exit(1)

    # Get configuration from environment
    host = os.getenv("DKR_HOST", "0.0.0.0")
    port = int(os.getenv("DKR_PORT", "8010"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    print(f"Starting DKR server on {host}:{port}")
    print(f"Log level: {log_level}")

    uvicorn.run(
        agent_os_app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()

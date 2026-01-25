"""
Configuration and environment tests
"""

import pytest
import os
import json
from pathlib import Path
import subprocess
import requests


class TestConfiguration:
    """Tests for configuration and environment setup"""

    def test_environment_variables(self):
        """Test that required environment variables are set"""
        # Check for API keys and other required env vars
        required_vars = ['GEMINI_API_KEY']

        for var in required_vars:
            assert var in os.environ, f"Required environment variable {var} not set"
            assert len(os.environ[var]) > 0, f"Environment variable {var} is empty"

    def test_service_ports_available(self):
        """Test that required service ports are available"""
        ports = [8000, 8001, 8002]  # PageIndex, LEANN, deepConf

        for port in ports:
            # Check if port is in use (services should be running)
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                capture_output=True,
                text=True
            )
            # Port should be in use (service running)
            assert result.returncode == 0, f"Port {port} not in use - service may not be running"

    def test_file_paths_exist(self):
        """Test that required file paths exist"""
        required_paths = [
            "/Volumes/WS4TB/ERSATZ_RAG/regulus/.env",
            "/Volumes/WS4TB/ERSATZ_RAG/WS_ED/Acceptable Uses and Governance of Artificial Intelligence Policy_FINAL_2-14-24.pdf"
        ]

        for path_str in required_paths:
            path = Path(path_str)
            assert path.exists(), f"Required path does not exist: {path_str}"

    def test_qdrant_connection(self):
        """Test Qdrant vector database connection"""
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(host="localhost", port=6333)
            # Try to list collections
            collections = client.get_collections()
            assert isinstance(collections.collections, list)
        except Exception as e:
            pytest.fail(f"Qdrant connection failed: {e}")


class TestServiceDependencies:
    """Tests for service dependencies and integrations"""

    def test_python_dependencies(self):
        """Test that required Python packages are installed"""
        required_packages = [
            'fastapi',
            'qdrant_client',
            'sentence_transformers',
            'google.generativeai',
            'pydantic'
        ]

        for package in required_packages:
            try:
                __import__(package.replace('.', '_'))
            except ImportError:
                pytest.fail(f"Required package not installed: {package}")

    def test_service_startup_scripts(self):
        """Test that service startup scripts exist and are executable"""
        service_dirs = [
            "/Volumes/WS4TB/ERSATZ_RAG/pageindex_service",
            "/Volumes/WS4TB/ERSATZ_RAG/leann_service",
            "/Volumes/WS4TB/ERSATZ_RAG/deepconf_service"
        ]

        for service_dir in service_dirs:
            service_path = Path(service_dir)
            assert service_path.exists(), f"Service directory missing: {service_dir}"

            app_file = service_path / "app.py"
            assert app_file.exists(), f"Service app.py missing: {app_file}"

            requirements_file = service_path / "requirements.txt"
            assert requirements_file.exists(), f"Service requirements.txt missing: {requirements_file}"


class TestDataValidation:
    """Tests for data validation and integrity"""

    def test_test_data_integrity(self):
        """Test that test data files are valid"""
        test_pdf = "/Volumes/WS4TB/ERSATZ_RAG/WS_ED/Acceptable Uses and Governance of Artificial Intelligence Policy_FINAL_2-14-24.pdf"

        if Path(test_pdf).exists():
            # Check file size (should be > 0)
            assert Path(test_pdf).stat().st_size > 0, "Test PDF is empty"

            # Try to read first few bytes
            with open(test_pdf, 'rb') as f:
                header = f.read(8)
                # PDF files start with %PDF-
                assert header.startswith(b'%PDF'), "Test file is not a valid PDF"

    def test_environment_file_integrity(self):
        """Test that .env file contains required entries"""
        env_file = "/Volumes/WS4TB/ERSATZ_RAG/regulus/.env"

        if Path(env_file).exists():
            with open(env_file, 'r') as f:
                content = f.read()

            # Check for key environment variables
            required_in_env = ['GEMINI_API_KEY']
            for key in required_in_env:
                assert key in content, f"Required key {key} not found in .env file"


class TestSystemIntegration:
    """Tests for overall system integration"""

    def test_all_services_communication(self):
        """Test that all services can communicate with each other"""
        # Test service-to-service communication paths
        services = {
            "pageindex": "http://localhost:8000/health",
            "leann": "http://localhost:8001/health",
            "deepconf": "http://localhost:8002/health"
        }

        for service_name, health_url in services.items():
            response = requests.get(health_url, timeout=10)
            assert response.status_code == 200, f"{service_name} service unhealthy"

            data = response.json()
            assert data.get("status") == "healthy", f"{service_name} status not healthy"
            print(f"✅ {service_name} service is healthy")

    def test_service_versions(self):
        """Test that services are running expected versions"""
        # This could check API versions or capabilities
        # For now, just ensure services respond to basic requests
        version_checks = [
            ("PageIndex", "http://localhost:8000/health"),
            ("LEANN", "http://localhost:8001/health"),
            ("deepConf", "http://localhost:8002/health")
        ]

        for service_name, url in version_checks:
            response = requests.get(url)
            assert response.status_code == 200
            # Could add version checking logic here if services expose version info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import os
import time
from pathlib import Path

import pytest
import requests

MEM_PROXY_URL = os.getenv("MEM_PROXY_URL", "http://localhost:8010").rstrip("/")
MEM_DIR = Path("/Volumes/WS4TB/ERSATZ_RAG/mem_agent/memory")


def memproxy_available() -> bool:
    try:
        r = requests.get(f"{MEM_PROXY_URL}/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


@pytest.mark.skipif(not memproxy_available(), reason="mem-proxy not running")
class TestMemProxy:
    def test_clarify_passthrough(self):
        # With MEM_AGENT_ENABLED=0 (default), clarify should passthrough
        q = "test clarify passthrough"
        payload = {"query": q, "context": {"pytest": True}}
        r = requests.post(f"{MEM_PROXY_URL}/clarify", json=payload, timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data.get("clarified_query") == q
        assert data.get("mode") == "passthrough"

    def test_health(self):
        r = requests.get(f"{MEM_PROXY_URL}/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "healthy"
        assert data.get("service") == "mem-proxy"

    def test_metrics_available(self):
        r = requests.get(f"{MEM_PROXY_URL}/metrics", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert "metrics" in data
        m = data["metrics"]
        assert set(["requests", "avg_response_ms", "errors"]).issubset(m.keys())

    def test_note_write_creates_file(self, tmp_path):
        # Prepare request body
        title = "Test Note from pytest"
        body_md = "This is a test note created by the test suite."
        payload = {
            "title": title,
            "body_md": body_md,
            "tags": ["test", "mem-proxy"],
            "context": {"test": True},
        }
        r = requests.post(f"{MEM_PROXY_URL}/note", json=payload, timeout=5)
        assert r.status_code == 200
        data = r.json()
        rel_path = data.get("path")
        abs_path = data.get("abs_path")
        assert rel_path and abs_path

        # Map container path to host path when necessary
        container_base = os.getenv("MEM_PROXY_MEMORY_DIR", "/app/memory")
        p = Path(abs_path)
        if str(p).startswith(container_base):
            rel = p.relative_to(container_base)
            host_p = MEM_DIR / rel
        else:
            host_p = p

        assert host_p.exists(), f"Expected note file not found at {host_p} (from container path {abs_path})"
        content = host_p.read_text(encoding="utf-8")
        assert title in content
        assert body_md in content

        # Ensure file under sandboxed memory dir
        assert str(host_p.resolve()).startswith(str(MEM_DIR.resolve()))

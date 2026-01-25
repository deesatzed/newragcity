"""
Test configuration and fixtures for Regulus backend tests
"""
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base


@pytest.fixture(scope="session")
def test_db() -> Generator:
    """Create a test database for the session"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal
    
    # Cleanup
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def test_client(test_db) -> TestClient:
    """Create a test client with test database"""
    def get_test_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_pdf_content() -> str:
    """Sample PDF text content for testing"""
    return """
    Sample Policy Document
    
    Section 1: Introduction
    This is the introduction to our corporate policy.
    
    Section 2: Guidelines
    These are the guidelines for proper conduct.
    
    Section 3: Compliance
    All employees must comply with these policies.
    """


@pytest.fixture
def mock_pdf_file(temp_dir: Path, sample_pdf_content: str) -> Path:
    """Create a mock PDF file for testing"""
    pdf_file = temp_dir / "test_policy.pdf"
    
    # Create a simple mock PDF (just text file for testing)
    with open(pdf_file, 'w') as f:
        f.write(sample_pdf_content)
    
    return pdf_file


@pytest.fixture(scope="session")
def golden_questions_and_answers():
    """Golden dataset for testing accuracy"""
    return [
        {
            "question": "What are the guidelines for proper conduct?",
            "expected_keywords": ["guidelines", "conduct", "proper"],
            "expected_node_id": "test_policy_1"
        },
        {
            "question": "Who must comply with these policies?",
            "expected_keywords": ["employees", "comply", "policies"],
            "expected_node_id": "test_policy_2"
        },
        {
            "question": "What is this document about?",
            "expected_keywords": ["policy", "corporate", "introduction"],
            "expected_node_id": "test_policy_0"
        }
    ]


@pytest.fixture
def mock_pageindex_result():
    """Mock PageIndex result structure"""
    return {
        "nodes": [
            {
                "node_id": "test_policy_0",
                "title": "Introduction", 
                "content": "This is the introduction to our corporate policy.",
                "summary": "Introduction to corporate policy",
                "page_ranges": [1, 1]
            },
            {
                "node_id": "test_policy_1", 
                "title": "Guidelines",
                "content": "These are the guidelines for proper conduct.",
                "summary": "Guidelines for proper conduct",
                "page_ranges": [2, 2]
            },
            {
                "node_id": "test_policy_2",
                "title": "Compliance",
                "content": "All employees must comply with these policies.", 
                "summary": "Employee compliance requirements",
                "page_ranges": [3, 3]
            }
        ]
    }
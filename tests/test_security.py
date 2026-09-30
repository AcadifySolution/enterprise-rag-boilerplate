from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)


def test_development_allows_api_requests():
    original_env = settings.APP_ENV
    settings.APP_ENV = "development"
    try:
        response = client.post(
            "/api/ingestion/text",
            json={"text": "# Test\ncontent", "source_name": "test.md"},
        )
        assert response.status_code == 200
    finally:
        settings.APP_ENV = original_env


def test_production_requires_api_key():
    original_env = settings.APP_ENV
    original_key = settings.API_KEY
    settings.APP_ENV = "production"
    settings.API_KEY = "test-secret"
    try:
        missing = client.get("/api/health")
        assert missing.status_code == 200

        missing = client.post(
            "/api/ingestion/text",
            json={"text": "# Test\ncontent", "source_name": "test.md"},
        )
        assert missing.status_code == 401

        authorized = client.post(
            "/api/ingestion/text",
            headers={"X-API-Key": "test-secret"},
            json={"text": "# Test\ncontent", "source_name": "test.md"},
        )
        assert authorized.status_code == 200
    finally:
        settings.APP_ENV = original_env
        settings.API_KEY = original_key

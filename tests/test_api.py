"""API tests."""

from fastapi.testclient import TestClient
from src.ev_charging_stations.api import app

client = TestClient(app)


def test_get_index():
    """Test that the HTML UI is served successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"].lower()


def test_process_query_valid():
    """Test /process with a simple valid query."""
    payload = {
        "query": "Find fast charging stations in New York",
        "file_name": "dummy.txt"
    }
    response = client.post("/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "model_output" in data
    assert isinstance(data["model_output"], list)  # Expecting list of stations or results


def test_process_query_with_city_and_speed():
    """Test with specific parameters to see if LLM pipeline handles structured queries."""
    payload = {
        "query": "Show me public superchargers in Los Angeles",
        "file_name": "dummy.txt"
    }
    response = client.post("/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "model_output" in data
    assert isinstance(data["model_output"], list)


def test_process_query_missing_field():
    """Test that missing fields still return a 422 or handled gracefully."""
    payload = {"query": "Where can I charge my EV?"}
    response = client.post("/process", json=payload)
    assert response.status_code in (200, 422)


def test_process_query_empty_question():
    """Test edge case: empty query string."""
    payload = {"query": "", "file_name": "dummy.txt"}
    response = client.post("/process", json=payload)
    # The API should not crash — either 200 with message or 400
    assert response.status_code in (200, 400)
    data = response.json()
    # If handled gracefully, model_output should exist or error message
    assert "model_output" in data or "error" in data


def test_process_query_invalid_json():
    """Test with malformed JSON (invalid body)."""
    response = client.post("/process", data="not a json")
    assert response.status_code in (400, 422)

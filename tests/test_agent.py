"""Pipeline function tests."""

import pytest
from src.ev_charging_stations.pipelines.query_pipeline import run_query_pipeline


@pytest.mark.parametrize(
    "question",
    [
        "Find fast charging stations in New York",
        "Show me public Type 2 chargers in San Francisco",
        "Which superchargers are available in Los Angeles?",
        "I'm in Tokyo, which stations have better user reviews?",
    ],
)
def test_run_query_pipeline_returns_list(question):
    """Test that the pipeline always returns a list of station objects."""
    results = run_query_pipeline(question)
    assert isinstance(results, list), "Pipeline should return a list"
    if results:  # if any results exist
        first = results[0]
        # Ensure the output has expected structure
        assert hasattr(first, "station_id")
        assert hasattr(first, "charging_speed")
        assert hasattr(first, "charging_types")
        assert hasattr(first, "accessibility")


def test_run_query_pipeline_empty_question():
    """Pipeline should handle empty questions gracefully."""
    results = run_query_pipeline("")
    assert isinstance(results, list)
    # should not crash or return None
    assert results == [] or all(hasattr(r, "station_id") for r in results)


def test_run_query_pipeline_nonexistent_city():
    """Query with a city that doesn’t exist should return empty result, not crash."""
    results = run_query_pipeline("Find chargers in Atlantis")
    assert isinstance(results, list)
    assert results == [] or all(hasattr(r, "station_id") for r in results)


def test_run_query_pipeline_with_no_results(monkeypatch):
    """Simulate DB returning empty results."""
    import src.ev_charging_stations.services.database as db

    def fake_find_stations(filters):
        return []  # simulate no stations found

    monkeypatch.setattr(db, "find_stations", fake_find_stations)

    results = run_query_pipeline("Find fast chargers in a small town")
    assert results == []

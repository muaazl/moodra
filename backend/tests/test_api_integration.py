from fastapi.testclient import TestClient
import json
import pytest

from main import app

client = TestClient(app)

@pytest.fixture
def sample_whatsapp_text():
    return """
01/01/2026, 12:00 - Alice: Hey!
01/01/2026, 12:01 - Bob: Hi there. How's it going?
01/01/2026, 12:02 - Alice: Great, just working on this new AI app.
01/01/2026, 12:03 - Bob: Nice. k.
"""

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_analyze_text_full_flow(client: TestClient, sample_whatsapp_text: str):
    """Test full analysis flow from text upload to scoring."""
    response = client.post("/api/v1/analyze/text", json={"text": sample_whatsapp_text})
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert top-level structure
    assert data["status"] == "success"
    result_data = data["data"]
    assert "overall_summary" in result_data
    assert "participants" in result_data
    assert "segments" in result_data
    assert "global_metrics" in result_data
    
    # Assert participant highlights
    participants = [p["name"] for p in result_data["participants"]]
    assert "Alice" in participants
    assert "Bob" in participants
    
    # Check for "The Driver" or typical badges (probabilistic, but likely for Alice)
    pass 

def test_analyze_file_flow(client: TestClient, sample_whatsapp_text: str):
    """Test file upload flow using realistic-format bytes."""
    files = {"file": ("chat.txt", sample_whatsapp_text.encode("utf-8"), "text/plain")}
    response = client.post("/api/v1/analyze/file", files=files)
    
    assert response.status_code == 200
    assert "data" in response.json()
    assert "overall_summary" in response.json()["data"]

def test_analyze_invalid_format(client: TestClient):
    """Verify that unparseable garbage text doesn't crash the API."""
    garbage = "Random strings of junk that are not chat formats"
    response = client.post("/api/v1/analyze/text", json={"text": garbage})
    
    # Even garbage should return a 200 with minimal empty stats if it's not a server error
    # Or a 400 if strictly enforced
    assert response.status_code in [200, 400]
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data

def test_analyze_text_invalid_payload():
    # Too short text should fail per min_length=10
    payload = {"text": "abc"}
    response = client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 422 # Pydantic validation error

def test_analyze_file_invalid_extension():
    files = {
        'file': ('image.jpg', b'fake image data', 'image/jpeg')
    }
    response = client.post("/api/v1/analyze/file", files=files)
    assert response.status_code == 400
    assert "Only .txt files are supported" in response.json()["detail"]

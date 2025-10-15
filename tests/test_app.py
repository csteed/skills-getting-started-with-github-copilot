import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_and_remove_participant():
    # Use a unique email for testing
    test_email = "pytestuser@mergington.edu"
    activity = "Chess Club"

    # Remove if already present (ignore error)
    client.delete(f"/activities/{activity}/participants/{test_email}")

    # Sign up
    resp_signup = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp_signup.status_code == 200
    assert f"Signed up {test_email}" in resp_signup.json()["message"]

    # Check participant is present
    resp_activities = client.get("/activities")
    assert test_email in resp_activities.json()[activity]["participants"]

    # Remove participant
    resp_remove = client.delete(f"/activities/{activity}/participants/{test_email}")
    assert resp_remove.status_code == 200
    assert f"Removed {test_email}" in resp_remove.json()["message"]

    # Check participant is gone
    resp_activities = client.get("/activities")
    assert test_email not in resp_activities.json()[activity]["participants"]

def test_signup_duplicate():
    activity = "Chess Club"
    email = "michael@mergington.edu"  # Already present
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]

def test_remove_nonexistent_participant():
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    resp = client.delete(f"/activities/{activity}/participants/{email}")
    assert resp.status_code == 404
    assert "Participant not found" in resp.json()["detail"]

def test_signup_nonexistent_activity():
    resp = client.post("/activities/NonexistentActivity/signup?email=test@mergington.edu")
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]

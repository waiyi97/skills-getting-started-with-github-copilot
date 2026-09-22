import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_state = {
        name: list(details["participants"])
        for name, details in activities.items()
    }

    yield

    for name, participants in original_state.items():
        activities[name]["participants"] = list(participants)


@pytest.fixture
def client():
    return TestClient(app)


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@example.com"
    activities[activity_name]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_registration(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@example.com"
    activities[activity_name]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    duplicate_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_delete_unregisters_existing_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"
    activities[activity_name]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_returns_404_for_unregistered_student(client):
    # Arrange
    activity_name = "Gym Class"
    email = "ghost@mergington.edu"
    activities[activity_name]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"

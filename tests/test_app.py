from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    # Should return the same activities keys as the in-memory DB
    assert set(data.keys()) == set(activities.keys())


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"
    activity = activities[activity_name]

    # Ensure a clean starting state
    if email in activity["participants"]:
        activity["participants"].remove(email)

    original_count = len(activity["participants"])

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    assert response.status_code == 200
    body = response.json()
    assert "Signed up" in body["message"]
    assert email in activity["participants"]
    assert len(activity["participants"]) == original_count + 1

    # Cleanup so other tests are not affected
    activity["participants"].remove(email)


def test_signup_for_activity_not_found():
    response = client.post(
        "/activities/Nonexistent Activity/signup", params={"email": "someone@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_duplicate():
    activity_name = "Chess Club"
    activity = activities[activity_name]
    existing_email = activity["participants"][0]

    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success():
    activity_name = "Chess Club"
    activity = activities[activity_name]
    email = activity["participants"][0]

    # Ensure the email is present before attempting to unregister
    if email not in activity["participants"]:
        activity["participants"].append(email)

    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    assert response.status_code == 200
    assert email not in activity["participants"]

    # Cleanup: re-add the participant so other tests remain stable
    activity["participants"].append(email)


def test_unregister_from_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent Activity/participants",
        params={"email": "someone@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_not_registered():
    activity_name = "Chess Club"
    activity = activities[activity_name]
    email = "not-registered@mergington.edu"

    # Ensure email is not in participants list
    if email in activity["participants"]:
        activity["participants"].remove(email)

    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"

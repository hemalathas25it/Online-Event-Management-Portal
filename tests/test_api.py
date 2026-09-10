import os
import pytest
from fastapi.testclient import TestClient

# Set test database path before importing app
os.environ["DB_PATH"] = os.path.join(os.path.dirname(__file__), "test_events.db")

from backend.main import app
from backend.database import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    test_db = os.environ["DB_PATH"]
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except OSError:
            pass
    init_db()
    yield
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except OSError:
            pass


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_token(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


@pytest.fixture
def user_token(client):
    res = client.post("/api/auth/login", json={"username": "student01", "password": "student123"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


# --- Authentication Tests ---

def test_login_success(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"


def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401
    assert "Invalid username or password" in res.json()["detail"]


def test_register_new_user(client):
    res = client.post("/api/auth/register", json={"username": "newuser99", "password": "password123"})
    assert res.status_code == 201
    data = res.json()
    assert data["user"]["username"] == "newuser99"
    assert data["user"]["role"] == "user"
    assert "access_token" in data


def test_register_duplicate_user(client):
    res = client.post("/api/auth/register", json={"username": "admin", "password": "password123"})
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_get_current_user_profile(client, user_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "student01"


# --- Event Tests ---

def test_list_events(client):
    res = client.get("/api/events")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    assert len(events) >= 1


def test_filter_upcoming_and_past_events(client):
    upcoming_res = client.get("/api/events?filter=upcoming")
    assert upcoming_res.status_code == 200
    upcoming = upcoming_res.json()
    assert all(e["is_upcoming"] for e in upcoming)

    past_res = client.get("/api/events?filter=past")
    assert past_res.status_code == 200
    past = past_res.json()
    assert all(not e["is_upcoming"] for e in past)


def test_search_events(client):
    res = client.get("/api/events?search=Symposium")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1
    assert "Symposium" in events[0]["title"]


def test_create_event_admin_only(client, admin_token, user_token):
    # Regular user cannot create event
    unauth_res = client.post(
        "/api/events",
        json={"title": "Unauthorized Event", "date": "2026-11-20", "location": "Room 101"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert unauth_res.status_code == 403

    # Admin can create event
    res = client.post(
        "/api/events",
        json={
            "title": "Cloud Computing Summit 2026",
            "description": "Exploration of cloud architecture",
            "date": "2026-11-25",
            "location": "Auditorium C",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Cloud Computing Summit 2026"
    assert data["id"] > 0


def test_update_and_delete_event(client, admin_token):
    # Create event to edit & delete
    create_res = client.post(
        "/api/events",
        json={"title": "To be edited", "date": "2026-12-12", "location": "Hall A"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    event_id = create_res.json()["id"]

    # Edit event
    update_res = client.put(
        f"/api/events/{event_id}",
        json={"title": "Updated Event Title", "location": "Hall B"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Event Title"
    assert update_res.json()["location"] == "Hall B"

    # Delete event
    del_res = client.delete(f"/api/events/{event_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert del_res.status_code == 200

    # Verify not found
    get_res = client.get(f"/api/events/{event_id}")
    assert get_res.status_code == 404


# --- Registration Tests ---

def test_event_registration(client, user_token):
    # Get an upcoming event
    events = client.get("/api/events?filter=upcoming").json()
    assert len(events) > 0
    event_id = events[0]["id"]

    # Register participant
    res = client.post(
        "/api/registrations",
        json={"event_id": event_id, "participant_name": "Unique Test Participant"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["participant_name"] == "Unique Test Participant"
    reg_id = data["id"]

    # Duplicate registration should fail
    dup_res = client.post(
        "/api/registrations",
        json={"event_id": event_id, "participant_name": "Unique Test Participant"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert dup_res.status_code == 400
    assert "already registered" in dup_res.json()["detail"]

    # Clean up registration
    del_res = client.delete(f"/api/registrations/{reg_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert del_res.status_code == 200


def test_cannot_register_for_past_event(client, user_token):
    past_events = client.get("/api/events?filter=past").json()
    assert len(past_events) > 0
    past_event_id = past_events[0]["id"]

    res = client.post(
        "/api/registrations",
        json={"event_id": past_event_id, "participant_name": "Late Student"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 400
    assert "past events" in res.json()["detail"]


# --- Dashboard & Reports Tests ---

def test_dashboard_stats(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    assert "upcoming_events" in stats
    assert "past_events" in stats
    assert "total_registrations" in stats
    assert "total_users" in stats
    assert stats["upcoming_events"] >= 1


def test_dashboard_reports(client):
    res = client.get("/api/dashboard/reports")
    assert res.status_code == 200
    reports = res.json()
    assert "event_distribution" in reports
    assert "recent_registrations" in reports
    assert isinstance(reports["event_distribution"], list)


# --- User Management Tests ---

def test_list_users_admin_only(client, admin_token, user_token):
    # Regular user forbidden
    res_user = client.get("/api/users", headers={"Authorization": f"Bearer {user_token}"})
    assert res_user.status_code == 403

    # Admin allowed
    res_admin = client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    users = res_admin.json()
    assert len(users) >= 2
    assert any(u["username"] == "admin" for u in users)

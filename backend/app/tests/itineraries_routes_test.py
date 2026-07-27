import pytest
from app.models.trip import create_trip, get_trips_by_user


# helper: creates a trip for a user and returns its id
def make_trip(app, user_id, name="Test Trip"):
    with app.app_context():
        create_trip(user_id, name, "A test trip", "2026-06-01", "2026-06-10")
        trips = get_trips_by_user(user_id)
        return trips[-1]["id"]


# ---------- auth / access control ----------

# no X-User-ID header at all should return 401
def test_get_itinerary_no_auth_header(client):
    response = client.get("/api/trips/1/itinerary")
    assert response.status_code == 401

# a non-numeric X-User-ID header should return 401, not crash with a 500
def test_get_itinerary_invalid_auth_header(client):
    response = client.get("/api/trips/1/itinerary", headers={"X-User-ID": "not-a-number"})
    assert response.status_code == 401

# a trip that doesn't exist (or belongs to someone else) should return 404
def test_get_itinerary_trip_not_found(client):
    response = client.get("/api/trips/9999/itinerary", headers={"X-User-ID": "1"})
    assert response.status_code == 404


# ---------- GET /api/trips/<id>/itinerary ----------

# a trip with no itinerary entries should return an empty list
def test_get_itinerary_empty(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.get(f"/api/trips/{trip_id}/itinerary", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    assert response.get_json() == []

# itinerary entries should come back in day_number order
def test_get_itinerary_returns_entries_in_order(client, app):
    trip_id = make_trip(app, user_id=1)

    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 2, "title": "Day Two"}, headers={"X-User-ID": "1"})
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "Day One"}, headers={"X-User-ID": "1"})

    response = client.get(f"/api/trips/{trip_id}/itinerary", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    entries = response.get_json()
    assert [e["day_number"] for e in entries] == [1, 2]

# a different user shouldn't be able to see this user's trip itinerary at all —
# documents the current owner-only access behavior
def test_get_itinerary_different_user_gets_404(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.get(f"/api/trips/{trip_id}/itinerary", headers={"X-User-ID": "2"})

    assert response.status_code == 404


# ---------- POST /api/trips/<id>/itinerary ----------

# creating an itinerary entry with valid data should return 201 with the new entry
def test_create_itinerary_success(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.post(
        f"/api/trips/{trip_id}/itinerary",
        json={"day_number": 1, "title": "Arrival", "description": "Fly in", "activities": "Airport"},
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["day_number"] == 1
    assert body["title"] == "Arrival"

# missing day_number should return 400
def test_create_itinerary_missing_day_number(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.post(
        f"/api/trips/{trip_id}/itinerary",
        json={"title": "Missing Day Number"},
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 400

# a non-dict JSON body (e.g. a list) should return 400, not crash with a 500
def test_create_itinerary_non_dict_json_body(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.post(
        f"/api/trips/{trip_id}/itinerary",
        json=["not", "a", "dict"],
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 400

# missing JSON body entirely should return 400
def test_create_itinerary_missing_json_body(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.post(
        f"/api/trips/{trip_id}/itinerary",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 400

# a day_number of 0 or negative should return 400 — this confirms the model's
# ValidationError is correctly caught and converted, not a raw 500
def test_create_itinerary_invalid_day_number(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.post(
        f"/api/trips/{trip_id}/itinerary",
        json={"day_number": -1, "title": "Bad Day"},
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 400

# creating a second entry for the same day_number on the same trip should return 409
def test_create_itinerary_duplicate_day(client, app):
    trip_id = make_trip(app, user_id=1)

    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "First"}, headers={"X-User-ID": "1"})
    response = client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "Second"}, headers={"X-User-ID": "1"})

    assert response.status_code == 409

# creating an itinerary entry on a trip that doesn't belong to this user should return 404
def test_create_itinerary_trip_not_found(client):
    response = client.post(
        "/api/trips/9999/itinerary",
        json={"day_number": 1, "title": "Ghost Trip"},
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404


# ---------- PUT /api/trips/<id>/itinerary/<day> ----------

# updating an existing entry should change only the fields sent
def test_update_itinerary_partial(client, app):
    trip_id = make_trip(app, user_id=1)
    client.post(
        f"/api/trips/{trip_id}/itinerary",
        json={"day_number": 1, "title": "Old Title", "description": "Old Description"},
        headers={"X-User-ID": "1"},
    )

    response = client.put(
        f"/api/trips/{trip_id}/itinerary/1",
        json={"title": "New Title"},
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "New Title"
    assert body["description"] == "Old Description"  # should be preserved

# updating a day that doesn't exist should return 404
def test_update_itinerary_not_found(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.put(
        f"/api/trips/{trip_id}/itinerary/99",
        json={"title": "Doesn't Exist"},
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404

# a non-dict JSON body should return 400
def test_update_itinerary_non_dict_json_body(client, app):
    trip_id = make_trip(app, user_id=1)
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "Day One"}, headers={"X-User-ID": "1"})

    response = client.put(
        f"/api/trips/{trip_id}/itinerary/1",
        json=["not", "a", "dict"],
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 400


# ---------- DELETE /api/trips/<id>/itinerary/<day> ----------

# deleting an existing entry should return 200 and remove it
def test_delete_itinerary_success(client, app):
    trip_id = make_trip(app, user_id=1)
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "To Delete"}, headers={"X-User-ID": "1"})

    response = client.delete(f"/api/trips/{trip_id}/itinerary/1", headers={"X-User-ID": "1"})

    assert response.status_code == 200

    # confirm it's actually gone
    get_response = client.get(f"/api/trips/{trip_id}/itinerary", headers={"X-User-ID": "1"})
    assert get_response.get_json() == []

# deleting a day that doesn't exist should return 404
def test_delete_itinerary_not_found(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.delete(f"/api/trips/{trip_id}/itinerary/99", headers={"X-User-ID": "1"})

    assert response.status_code == 404


# ---------- PUT .../complete and .../incomplete ----------

# marking a day complete should update its status
def test_mark_complete(client, app):
    trip_id = make_trip(app, user_id=1)
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "Day One"}, headers={"X-User-ID": "1"})

    response = client.put(f"/api/trips/{trip_id}/itinerary/1/complete", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    assert response.get_json()["message"] == "Marked complete"

# marking a nonexistent day complete should return 404
def test_mark_complete_not_found(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.put(f"/api/trips/{trip_id}/itinerary/99/complete", headers={"X-User-ID": "1"})

    assert response.status_code == 404

# marking a completed day incomplete again should undo it
def test_mark_incomplete(client, app):
    trip_id = make_trip(app, user_id=1)
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1, "title": "Day One"}, headers={"X-User-ID": "1"})
    client.put(f"/api/trips/{trip_id}/itinerary/1/complete", headers={"X-User-ID": "1"})

    response = client.put(f"/api/trips/{trip_id}/itinerary/1/incomplete", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    assert response.get_json()["message"] == "Marked incomplete"


# ---------- GET .../completion-status ----------

# completion status should correctly reflect partial progress
def test_completion_status_partial(client, app):
    trip_id = make_trip(app, user_id=1)
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 1}, headers={"X-User-ID": "1"})
    client.post(f"/api/trips/{trip_id}/itinerary", json={"day_number": 2}, headers={"X-User-ID": "1"})
    client.put(f"/api/trips/{trip_id}/itinerary/1/complete", headers={"X-User-ID": "1"})

    response = client.get(f"/api/trips/{trip_id}/completion-status", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 2
    assert body["completed"] == 1
    assert body["percentage"] == 50.0

# a trip with no itinerary entries should report 0% without error
def test_completion_status_empty_trip(client, app):
    trip_id = make_trip(app, user_id=1)

    response = client.get(f"/api/trips/{trip_id}/completion-status", headers={"X-User-ID": "1"})

    assert response.status_code == 200
    assert response.get_json()["percentage"] == 0

# completion status for a nonexistent trip should return 404
def test_completion_status_trip_not_found(client):
    response = client.get("/api/trips/9999/completion-status", headers={"X-User-ID": "1"})

    assert response.status_code == 404
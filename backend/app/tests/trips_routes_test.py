# tests/test_trips_routes.py
import pytest
import json


# ---------- auth / access control ----------

# no Authorization header should return 401
def test_get_trips_no_auth_header(client):
    response = client.get("/api/trips")
    assert response.status_code == 401

# a garbage/invalid token should return 401, not crash with a 500
def test_get_trips_invalid_auth_header(client):
    response = client.get("/api/trips", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 422


# ---------- GET /api/trips ----------

# a user with no trips should get an empty list
def test_get_trips_empty(client, auth_headers):
    response = client.get("/api/trips", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []

# should only return trips owned by that user
def test_get_trips_only_returns_own_trips(client, auth_headers, auth_headers_2):
    client.post("/api/trips", json={
        "name": "User 1 Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)

    client.post("/api/trips", json={
        "name": "User 2 Trip",
        "start_date": "2026-07-01T00:00:00",
        "end_date": "2026-07-08T00:00:00",
    }, headers=auth_headers_2)

    response = client.get("/api/trips", headers=auth_headers)

    assert response.status_code == 200
    trips = response.get_json()
    assert len(trips) == 1
    assert trips[0]["name"] == "User 1 Trip"


# ---------- POST /api/trips ----------

def test_create_trip_success(client, auth_headers):
    response = client.post("/api/trips", json={
        "name": "Paris Vacation",
        "description": "A week in Paris",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)

    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "Paris Vacation"

def test_create_trip_missing_name(client, auth_headers):
    response = client.post("/api/trips", json={
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)

    assert response.status_code == 400

def test_create_trip_missing_dates(client, auth_headers):
    response = client.post("/api/trips", json={"name": "No Dates Trip"}, headers=auth_headers)
    assert response.status_code == 400

def test_create_trip_invalid_date_format(client, auth_headers):
    response = client.post("/api/trips", json={
        "name": "Bad Date Trip",
        "start_date": "not-a-date",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)

    assert response.status_code == 400

def test_create_trip_start_after_end(client, auth_headers):
    response = client.post("/api/trips", json={
        "name": "Backwards Trip",
        "start_date": "2026-06-08T00:00:00",
        "end_date": "2026-06-01T00:00:00",
    }, headers=auth_headers)

    assert response.status_code == 400

def test_create_trip_non_dict_json_body(client, auth_headers):
    response = client.post("/api/trips", json=["not", "a", "dict"], headers=auth_headers)
    assert response.status_code == 400

def test_create_trip_missing_json_body(client, auth_headers):
    response = client.post("/api/trips", headers=auth_headers)
    assert response.status_code == 400


# ---------- GET /api/trips/<id> ----------

def test_get_trip_includes_events_list(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip With Events",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.get(f"/api/trips/{trip_id}", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["events"] == []

def test_get_trip_not_found(client, auth_headers):
    response = client.get("/api/trips/9999", headers=auth_headers)
    assert response.status_code == 404

def test_get_trip_different_user_gets_404(client, auth_headers, auth_headers_2):
    create_response = client.post("/api/trips", json={
        "name": "Private Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.get(f"/api/trips/{trip_id}", headers=auth_headers_2)

    assert response.status_code == 404


# ---------- PUT /api/trips/<id> ----------

def test_update_trip_partial(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Old Name",
        "description": "Old Description",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.put(f"/api/trips/{trip_id}", json={"name": "New Name"}, headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["name"] == "New Name"
    assert body["description"] == "Old Description"

def test_update_trip_not_found(client, auth_headers):
    response = client.put("/api/trips/9999", json={"name": "Ghost"}, headers=auth_headers)
    assert response.status_code == 404

def test_update_trip_non_dict_json_body(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.put(f"/api/trips/{trip_id}", json=["not", "a", "dict"], headers=auth_headers)
    assert response.status_code == 400

def test_update_trip_start_after_end(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.put(f"/api/trips/{trip_id}", json={"start_date": "2026-06-09T00:00:00"}, headers=auth_headers)
    assert response.status_code == 400


# ---------- DELETE /api/trips/<id> ----------

def test_delete_trip_success(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "To Delete",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.delete(f"/api/trips/{trip_id}", headers=auth_headers)
    assert response.status_code == 200

    get_response = client.get(f"/api/trips/{trip_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_trip_not_found(client, auth_headers):
    response = client.delete("/api/trips/9999", headers=auth_headers)
    assert response.status_code == 404


# ---------- POST /api/trips/<id>/events ----------

def test_create_event_success(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Museum Visit",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers)

    assert response.status_code == 201
    assert response.get_json()["title"] == "Museum Visit"

def test_create_event_missing_required_field(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Missing Times",
    }, headers=auth_headers)

    assert response.status_code == 400

def test_create_event_start_after_end(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Backwards Event",
        "start_time": "2026-06-02T12:00:00",
        "end_time": "2026-06-02T10:00:00",
    }, headers=auth_headers)

    assert response.status_code == 400

def test_create_event_invalid_rrule(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Bad RRULE Event",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
        "rrule": "this is not a valid rrule",
    }, headers=auth_headers)

    assert response.status_code == 400

def test_create_event_valid_rrule(client, auth_headers):
    create_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = create_response.get_json()["id"]

    response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Weekly Standup",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T10:30:00",
        "rrule": "FREQ=WEEKLY;BYDAY=MO",
    }, headers=auth_headers)

    assert response.status_code == 201

def test_create_event_trip_not_found(client, auth_headers):
    response = client.post("/api/trips/9999/events", json={
        "title": "Ghost Event",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers)

    assert response.status_code == 404


# ---------- PUT /api/trips/<id>/events/<event_id> ----------

def test_update_event_partial(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    event_response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Old Title",
        "description": "Old Description",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers)
    event_id = event_response.get_json()["id"]

    response = client.put(f"/api/trips/{trip_id}/events/{event_id}", json={"title": "New Title"}, headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["title"] == "New Title"
    assert body["description"] == "Old Description"

def test_update_event_not_found(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    response = client.put(f"/api/trips/{trip_id}/events/9999", json={"title": "Ghost"}, headers=auth_headers)
    assert response.status_code == 404

def test_update_event_wrong_trip_returns_404(client, auth_headers):
    trip_one = client.post("/api/trips", json={
        "name": "Trip 1", "start_date": "2026-06-01T00:00:00", "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers).get_json()

    trip_two = client.post("/api/trips", json={
        "name": "Trip 2", "start_date": "2026-07-01T00:00:00", "end_date": "2026-07-08T00:00:00",
    }, headers=auth_headers).get_json()

    event = client.post(f"/api/trips/{trip_one['id']}/events", json={
        "title": "Trip 1 Event",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers).get_json()

    response = client.put(f"/api/trips/{trip_two['id']}/events/{event['id']}", json={"title": "Hijacked"}, headers=auth_headers)

    assert response.status_code == 404


# ---------- DELETE /api/trips/<id>/events/<event_id> ----------

def test_delete_event_success(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    event_response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "To Delete",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers)
    event_id = event_response.get_json()["id"]

    response = client.delete(f"/api/trips/{trip_id}/events/{event_id}", headers=auth_headers)
    assert response.status_code == 200

def test_delete_event_not_found(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    response = client.delete(f"/api/trips/{trip_id}/events/9999", headers=auth_headers)
    assert response.status_code == 404


# ---------- GET /api/trips/<id>/events (occurrence expansion) ----------

def test_get_events_window_includes_matching_event(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Museum Visit",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers)

    response = client.get(
        f"/api/trips/{trip_id}/events?start=2026-06-01T00:00:00&end=2026-06-08T00:00:00",
        headers=auth_headers,
    )

    assert response.status_code == 200
    occurrences = response.get_json()
    assert len(occurrences) == 1
    assert occurrences[0]["title"] == "Museum Visit"

def test_get_events_window_missing_params(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    response = client.get(f"/api/trips/{trip_id}/events", headers=auth_headers)
    assert response.status_code == 400

def test_get_events_window_invalid_date_format(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    response = client.get(
        f"/api/trips/{trip_id}/events?start=not-a-date&end=2026-06-08T00:00:00",
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------- GET /api/trips/<id>/calendar.ics ----------

def test_export_calendar_success(client, auth_headers):
    trip_response = client.post("/api/trips", json={
        "name": "Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-08T00:00:00",
    }, headers=auth_headers)
    trip_id = trip_response.get_json()["id"]

    client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Museum Visit",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
    }, headers=auth_headers)

    response = client.get(f"/api/trips/{trip_id}/calendar.ics", headers=auth_headers)

    assert response.status_code == 200
    assert response.content_type.startswith("text/calendar")
    assert b"Museum Visit" in response.data

def test_export_calendar_trip_not_found(client, auth_headers):
    response = client.get("/api/trips/9999/calendar.ics", headers=auth_headers)
    assert response.status_code == 404
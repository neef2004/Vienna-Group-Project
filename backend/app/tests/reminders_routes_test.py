# tests/test_reminders_routes.py
import pytest


# helper: creates a trip, returns its id
def make_trip(client, headers):
    response = client.post("/api/trips", json={
        "name": "Test Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-10T00:00:00",
    }, headers=headers)
    return response.get_json()["id"]

# helper: creates an event on a trip, returns its id
def make_event(client, trip_id, headers, start_time="2026-06-02T10:00:00", end_time="2026-06-02T12:00:00"):
    response = client.post(f"/api/trips/{trip_id}/events", json={
        "title": "Test Event",
        "start_time": start_time,
        "end_time": end_time,
    }, headers=headers)
    return response.get_json()["id"]


# ---------- auth / access control ----------

# no Authorization header should return 401
def test_get_reminders_no_auth_header(client):
    response = client.get("/api/trips/1/events/1/reminders")
    assert response.status_code == 401

# a garbage token should return 422 (malformed JWT), not crash with a 500
def test_get_reminders_invalid_auth_header(client):
    response = client.get("/api/trips/1/events/1/reminders", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 422


# ---------- GET /api/trips/<id>/events/<id>/reminders ----------

# a fresh event with no reminders should return an empty list
def test_get_event_reminders_empty(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)

    response = client.get(f"/api/trips/{trip_id}/events/{event_id}/reminders", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == []

# reminders should show up after being created
def test_get_event_reminders_after_creation(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)
    client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={
        "minutes_before": 30,
    }, headers=auth_headers)

    response = client.get(f"/api/trips/{trip_id}/events/{event_id}/reminders", headers=auth_headers)

    assert response.status_code == 200
    reminders = response.get_json()
    assert len(reminders) == 1

# a trip that doesn't exist/belong to this user should return 404
def test_get_event_reminders_trip_not_found(client, auth_headers):
    response = client.get("/api/trips/9999/events/1/reminders", headers=auth_headers)
    assert response.status_code == 404

# an event that doesn't exist should return 404
def test_get_event_reminders_event_not_found(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    response = client.get(f"/api/trips/{trip_id}/events/9999/reminders", headers=auth_headers)
    assert response.status_code == 404

# an event that exists but belongs to a DIFFERENT trip should return 404
def test_get_event_reminders_event_wrong_trip(client, auth_headers):
    trip_one = make_trip(client, auth_headers)
    trip_two = make_trip(client, auth_headers)
    event_id = make_event(client, trip_one, auth_headers)

    response = client.get(f"/api/trips/{trip_two}/events/{event_id}/reminders", headers=auth_headers)

    assert response.status_code == 404


# ---------- POST /api/trips/<id>/events/<id>/reminders ----------

# creating a reminder with defaults should return 201 with the full reminder list
def test_create_reminder_success_with_defaults(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={},
                            headers=auth_headers)

    assert response.status_code == 201
    reminders = response.get_json()
    assert len(reminders) == 1
    assert reminders[0]["notification_type"] == "email"

# the reminder_time should be correctly anchored to the event's start_time,
# not to "now" — this is the core bug we fixed in create_reminder
def test_create_reminder_time_anchored_to_event_start(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers, start_time="2026-06-02T10:00:00", end_time="2026-06-02T12:00:00")

    response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={
        "minutes_before": 30,
    }, headers=auth_headers)

    assert response.status_code == 201
    reminder = response.get_json()[0]

    # reminder_time should be 30 minutes before 10:00, i.e. 09:30 on the event's day —
    # NOT anywhere near the current real-world date
    assert "2026-06-02 09:30:00" in reminder["reminder_time"]

# a custom notification_type should be respected
def test_create_reminder_custom_notification_type(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={
        "notification_type": "sms",
    }, headers=auth_headers)

    assert response.status_code == 201
    assert response.get_json()[0]["notification_type"] == "sms"

# an invalid notification_type should return 400, not a raw 500
def test_create_reminder_invalid_notification_type(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={
        "notification_type": "carrier_pigeon",
    }, headers=auth_headers)

    assert response.status_code == 400

# a negative minutes_before should return 400
def test_create_reminder_negative_minutes_before(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={
        "minutes_before": -10,
    }, headers=auth_headers)

    assert response.status_code == 400

# a non-dict JSON body should return 400, not crash with a 500
def test_create_reminder_non_dict_json_body(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json=["not", "a", "dict"],
                            headers=auth_headers)

    assert response.status_code == 400

# creating a reminder on a trip that doesn't exist should return 404
def test_create_reminder_trip_not_found(client, auth_headers):
    response = client.post("/api/trips/9999/events/1/reminders", json={}, headers=auth_headers)
    assert response.status_code == 404

# creating a reminder on an event that doesn't exist should return 404
def test_create_reminder_event_not_found(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    response = client.post(f"/api/trips/{trip_id}/events/9999/reminders", json={}, headers=auth_headers)
    assert response.status_code == 404


# ---------- DELETE /api/trips/<id>/reminders/<id> ----------

# deleting an existing reminder should return 200 and remove it
def test_delete_reminder_success(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    event_id = make_event(client, trip_id, auth_headers)
    create_response = client.post(f"/api/trips/{trip_id}/events/{event_id}/reminders", json={},
                                   headers=auth_headers)
    reminder_id = create_response.get_json()[0]["id"]

    response = client.delete(f"/api/trips/{trip_id}/reminders/{reminder_id}", headers=auth_headers)

    assert response.status_code == 200

    get_response = client.get(f"/api/trips/{trip_id}/events/{event_id}/reminders", headers=auth_headers)
    assert get_response.get_json() == []

# deleting a reminder that doesn't exist should return 404
def test_delete_reminder_not_found(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    response = client.delete(f"/api/trips/{trip_id}/reminders/9999", headers=auth_headers)
    assert response.status_code == 404

# THE KEY SECURITY TEST: a reminder that belongs to a DIFFERENT trip should NOT
# be deletable through this trip's URL, even though both trips belong to the
# same user. This is the exact gap flagged in the original code's own comment.
def test_delete_reminder_wrong_trip_returns_404(client, auth_headers):
    trip_one = make_trip(client, auth_headers)
    trip_two = make_trip(client, auth_headers)
    event_on_trip_one = make_event(client, trip_one, auth_headers)

    create_response = client.post(f"/api/trips/{trip_one}/events/{event_on_trip_one}/reminders", json={},
                                   headers=auth_headers)
    reminder_id = create_response.get_json()[0]["id"]

    # attempt to delete trip_one's reminder through trip_two's URL
    response = client.delete(f"/api/trips/{trip_two}/reminders/{reminder_id}", headers=auth_headers)

    assert response.status_code == 404

    # confirm the reminder STILL EXISTS — it must not have been deleted
    get_response = client.get(f"/api/trips/{trip_one}/events/{event_on_trip_one}/reminders", headers=auth_headers)
    assert len(get_response.get_json()) == 1

# deleting a reminder on a trip that doesn't belong to this user should return 404
def test_delete_reminder_trip_not_found(client, auth_headers):
    response = client.delete("/api/trips/9999/reminders/1", headers=auth_headers)
    assert response.status_code == 404
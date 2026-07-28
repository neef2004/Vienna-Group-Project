# tests/test_trip.py
import pytest
import sqlite3
from datetime import datetime
from app.models.trip import (
    create_trip,
    get_trip_by_id,
    get_trips_by_user,
    update_trip,
    delete_trip,
    create_event,
    get_event_by_id,
    get_events_by_trip,
    update_event,
    delete_event,
    add_trip_collaborator,
    get_trip_collaborators,
    get_user_permission_for_trip,
    accept_trip_invitation,
    remove_trip_collaborator,
    update_collaborator_permission,
    get_user_trips
)


# ---------- create_trip / get_trip_by_id ----------

# creating a trip should let us find it again by id + owning user
def test_create_and_get_trip(app):
    with app.app_context():
        create_trip(1, "Paris Vacation", "A week in Paris",
                     datetime(2026, 6, 1), datetime(2026, 6, 8))

        trips = get_trips_by_user(1)
        trip = trips[-1]

        assert trip["name"] == "Paris Vacation"
        assert trip["description"] == "A week in Paris"

        fetched = get_trip_by_id(trip["id"], 1)
        assert fetched is not None
        assert fetched["name"] == "Paris Vacation"

# a trip should not be visible to a user who doesn't own it —
# confirms get_trip_by_id is properly scoped by user_id
def test_get_trip_by_id_wrong_user_returns_none(app):
    with app.app_context():
        create_trip(1, "Owner's Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        result = get_trip_by_id(trip["id"], user_id=2)
        assert result is None

# a nonexistent trip_id should return None, not raise
def test_get_trip_by_id_not_found(app):
    with app.app_context():
        result = get_trip_by_id(9999, user_id=1)
        assert result is None


# ---------- get_trips_by_user ----------

# should only return trips owned by that user, not another user's trips
def test_get_trips_by_user_only_returns_own_trips(app):
    with app.app_context():
        create_trip(1, "User 1 Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        create_trip(2, "User 2 Trip", "desc", datetime(2026, 7, 1), datetime(2026, 7, 8))

        user_one_trips = get_trips_by_user(1)

        assert len(user_one_trips) == 1
        assert user_one_trips[0]["name"] == "User 1 Trip"

# a user with no trips should get an empty list, not an error
def test_get_trips_by_user_empty(app):
    with app.app_context():
        trips = get_trips_by_user(999)
        assert trips == []


# ---------- update_trip ----------

# updating a trip should change its fields when re-fetched
def test_update_trip(app):
    with app.app_context():
        create_trip(1, "Old Name", "Old Description", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        update_trip(trip["id"], "New Name", "New Description",
                     datetime(2026, 7, 1), datetime(2026, 7, 8))

        updated = get_trip_by_id(trip["id"], 1)
        assert updated["name"] == "New Name"
        assert updated["description"] == "New Description"


# ---------- delete_trip ----------

# deleting a trip should make it unfindable afterward
def test_delete_trip(app):
    with app.app_context():
        create_trip(1, "To Delete", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        delete_trip(trip["id"])

        assert get_trip_by_id(trip["id"], 1) is None

# deleting a nonexistent trip_id should not raise — silent no-op
def test_delete_trip_nonexistent_is_noop(app):
    with app.app_context():
        delete_trip(9999)  # should not raise


# ---------- create_event / get_event_by_id ----------

# creating an event should let us find it again by id
def test_create_and_get_event(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        create_event(trip["id"], "Museum Visit", "See the Louvre",
                     datetime(2026, 6, 2, 10, 0), datetime(2026, 6, 2, 12, 0), "UTC", None)

        events = get_events_by_trip(trip["id"])
        event = events[-1]

        assert event["title"] == "Museum Visit"
        assert event["description"] == "See the Louvre"

# a nonexistent event_id should return None, not raise
def test_get_event_by_id_not_found(app):
    with app.app_context():
        result = get_event_by_id(9999)
        assert result is None


# ---------- get_events_by_trip ----------

# should only return events for that trip, not events on other trips
def test_get_events_by_trip_only_returns_matching_trip(app):
    with app.app_context():
        create_trip(1, "Trip 1", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        create_trip(1, "Trip 2", "desc", datetime(2026, 7, 1), datetime(2026, 7, 8))
        trips = get_trips_by_user(1)
        trip_one, trip_two = trips[0], trips[1]

        create_event(trip_one["id"], "Trip 1 Event", "desc",
                     datetime(2026, 6, 2, 10, 0), datetime(2026, 6, 2, 12, 0), "UTC", None)
        create_event(trip_two["id"], "Trip 2 Event", "desc",
                     datetime(2026, 7, 2, 10, 0), datetime(2026, 7, 2, 12, 0), "UTC", None)

        trip_one_events = get_events_by_trip(trip_one["id"])

        assert len(trip_one_events) == 1
        assert trip_one_events[0]["title"] == "Trip 1 Event"

# a trip with no events should return an empty list
def test_get_events_by_trip_empty(app):
    with app.app_context():
        result = get_events_by_trip(9999)
        assert result == []


# ---------- update_event ----------

# updating an event should change its fields when re-fetched
def test_update_event(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        create_event(trip["id"], "Old Title", "Old Desc",
                     datetime(2026, 6, 2, 10, 0), datetime(2026, 6, 2, 12, 0), "UTC", None)
        event = get_events_by_trip(trip["id"])[-1]

        update_event(event["id"], "New Title", "New Desc",
                     datetime(2026, 6, 3, 9, 0), datetime(2026, 6, 3, 11, 0), "America/New_York", None)

        updated = get_event_by_id(event["id"])
        assert updated["title"] == "New Title"
        assert updated["timezone"] == "America/New_York"


# ---------- delete_event ----------

# deleting an event should make it unfindable afterward
def test_delete_event(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        create_event(trip["id"], "To Delete", "desc",
                     datetime(2026, 6, 2, 10, 0), datetime(2026, 6, 2, 12, 0), "UTC", None)
        event = get_events_by_trip(trip["id"])[-1]

        delete_event(event["id"])

        assert get_event_by_id(event["id"]) is None


# ---------- add_trip_collaborator / get_trip_collaborators ----------

# adding a collaborator should let us find them in the trip's collaborator list
def test_add_and_get_trip_collaborator(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        add_trip_collaborator(trip["id"], user_id=2)

        collaborators = get_trip_collaborators(trip["id"])
        assert len(collaborators) == 1
        assert collaborators[0]["user_id"] == 2
        assert collaborators[0]["permission_level"] == "editor"  # confirms the default

# permission_level should be overridable from the default
def test_add_trip_collaborator_custom_permission(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        add_trip_collaborator(trip["id"], user_id=2, permission_level="viewer")

        collaborators = get_trip_collaborators(trip["id"])
        assert collaborators[0]["permission_level"] == "viewer"


# ---------- get_user_permission_for_trip ----------

# should return the correct permission level for a known collaborator
def test_get_user_permission_for_trip(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        add_trip_collaborator(trip["id"], user_id=2, permission_level="viewer")

        permission = get_user_permission_for_trip(trip["id"], user_id=2)
        assert permission == "viewer"

# a user who isn't a collaborator should get None, not an error
def test_get_user_permission_for_trip_not_a_collaborator(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        permission = get_user_permission_for_trip(trip["id"], user_id=999)
        assert permission is None


# ---------- accept_trip_invitation ----------

# accepting an invitation should mark the collaborator as accepted
def test_accept_trip_invitation(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        add_trip_collaborator(trip["id"], user_id=2)

        accept_trip_invitation(trip["id"], user_id=2)

        collaborators = get_trip_collaborators(trip["id"])
        assert collaborators[0]["accepted"] == 1
        assert collaborators[0]["accepted_at"] is not None


# ---------- remove_trip_collaborator ----------

# removing a collaborator should make them disappear from the trip's collaborator list
def test_remove_trip_collaborator(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        add_trip_collaborator(trip["id"], user_id=2)

        remove_trip_collaborator(trip["id"], user_id=2)

        collaborators = get_trip_collaborators(trip["id"])
        assert len(collaborators) == 0


# ---------- update_collaborator_permission ----------

# updating a collaborator's permission should be reflected afterward
def test_update_collaborator_permission(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        add_trip_collaborator(trip["id"], user_id=2, permission_level="viewer")

        update_collaborator_permission(trip["id"], user_id=2, permission_level="editor")

        permission = get_user_permission_for_trip(trip["id"], user_id=2)
        assert permission == "editor"


# ---------- get_user_trips ----------

# should include trips the user owns
def test_get_user_trips_includes_owned_trips(app):
    with app.app_context():
        create_trip(1, "Owned Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))

        trips = get_user_trips(1)

        assert len(trips) == 1
        assert trips[0]["name"] == "Owned Trip"

# should include trips the user is an ACCEPTED collaborator on
def test_get_user_trips_includes_accepted_collaborations(app):
    with app.app_context():
        create_trip(1, "Owner's Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]
        add_trip_collaborator(trip["id"], user_id=2)
        accept_trip_invitation(trip["id"], user_id=2)

        trips = get_user_trips(2)

        assert len(trips) == 1
        assert trips[0]["name"] == "Owner's Trip"


# ---------- add_trip_collaborator ----------

# adding the same collaborator twice should raise, not silently duplicate
def test_add_trip_collaborator_duplicate_raises(app):
    with app.app_context():
        create_trip(1, "Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 8))
        trip = get_trips_by_user(1)[-1]

        add_trip_collaborator(trip["id"], user_id=2)

        with pytest.raises(sqlite3.IntegrityError):
            add_trip_collaborator(trip["id"], user_id=2)
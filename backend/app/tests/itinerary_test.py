# tests/test_itinerary.py
import pytest
from datetime import datetime
from app.models.itinerary import (
    create_itinerary,
    get_itinerary_by_id,
    get_itinerary_by_trip_and_day,
    get_itinerary_by_trip,
    update_itinerary,
    delete_itinerary,
    get_day_date,
    mark_itinerary_complete,
    mark_itinerary_incomplete,
    get_trip_completion_status,
    ValidationError,
)


# ---------- create_itinerary ----------

# creating an itinerary entry should let us find it again by trip + day
def test_create_and_get_itinerary(app):
    with app.app_context():
        create_itinerary(1, 1, "Arrival Day", "Fly in and check into hotel", "Airport, hotel")
        entry = get_itinerary_by_trip_and_day(1, 1)

        assert entry is not None
        assert entry["title"] == "Arrival Day"
        assert entry["description"] == "Fly in and check into hotel"
        assert entry["activities"] == "Airport, hotel"

# title/description/activities are optional — creating with only the required fields should work
def test_create_itinerary_with_only_required_fields(app):
    with app.app_context():
        create_itinerary(1, 1)
        entry = get_itinerary_by_trip_and_day(1, 1)

        assert entry is not None
        assert entry["title"] is None
        assert entry["description"] is None
        assert entry["activities"] is None

# day_number of 0 should be rejected — days are 1-indexed
def test_create_itinerary_rejects_zero_day_number(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            create_itinerary(1, 0, "Bad Day")

# negative day_number should be rejected
def test_create_itinerary_rejects_negative_day_number(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            create_itinerary(1, -3, "Bad Day")

# non-integer day_number (e.g. a string) should be rejected
def test_create_itinerary_rejects_non_integer_day_number(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            create_itinerary(1, "one", "Bad Day")

# booleans are technically ints in Python (True == 1) — this confirms that
# loophole is explicitly closed, since True/False aren't meaningful day numbers
def test_create_itinerary_rejects_boolean_day_number(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            create_itinerary(1, True, "Bad Day")


# ---------- get_itinerary_by_id / get_itinerary_by_trip_and_day ----------

# looking up a day that was never created should return nothing
def test_get_itinerary_by_trip_and_day_not_found(app):
    with app.app_context():
        entry = get_itinerary_by_trip_and_day(1, 99)
        assert entry is None

# looking up an id that doesn't exist should return nothing
def test_get_itinerary_by_id_not_found(app):
    with app.app_context():
        entry = get_itinerary_by_id(9999)
        assert entry is None


# ---------- get_itinerary_by_trip ----------

# should return every day for a trip, ordered by day_number
def test_get_itinerary_by_trip_returns_all_days_in_order(app):
    with app.app_context():
        create_itinerary(1, 2, "Day Two")
        create_itinerary(1, 1, "Day One")
        create_itinerary(1, 3, "Day Three")

        entries = get_itinerary_by_trip(1)

        assert len(entries) == 3
        assert [e["day_number"] for e in entries] == [1, 2, 3]

# a trip with no itinerary entries should return an empty list, not None or an error
def test_get_itinerary_by_trip_empty(app):
    with app.app_context():
        entries = get_itinerary_by_trip(999)
        assert entries == []

# entries for a different trip_id should never show up in another trip's results
def test_get_itinerary_by_trip_only_returns_matching_trip(app):
    with app.app_context():
        create_itinerary(1, 1, "Trip 1 Day 1")
        create_itinerary(2, 1, "Trip 2 Day 1")

        trip_one_entries = get_itinerary_by_trip(1)

        assert len(trip_one_entries) == 1
        assert trip_one_entries[0]["title"] == "Trip 1 Day 1"


# ---------- update_itinerary ----------

# updating with all three fields should change all three
def test_update_itinerary_all_fields(app):
    with app.app_context():
        create_itinerary(1, 1, "Old Title", "Old Description", "Old Activities")
        entry = get_itinerary_by_trip_and_day(1, 1)

        update_itinerary(entry["id"], "New Title", "New Description", "New Activities")
        updated = get_itinerary_by_id(entry["id"])

        assert updated["title"] == "New Title"
        assert updated["description"] == "New Description"
        assert updated["activities"] == "New Activities"

# the key fix: calling update_itinerary with ONLY title should NOT wipe out
# description/activities — this is the bug we specifically fixed with _UNSET
def test_update_itinerary_partial_update_preserves_other_fields(app):
    with app.app_context():
        create_itinerary(1, 1, "Old Title", "Old Description", "Old Activities")
        entry = get_itinerary_by_trip_and_day(1, 1)

        update_itinerary(entry["id"], title="New Title")
        updated = get_itinerary_by_id(entry["id"])

        assert updated["title"] == "New Title"
        assert updated["description"] == "Old Description"  # should survive untouched
        assert updated["activities"] == "Old Activities"     # should survive untouched

# updating a nonexistent itinerary_id should raise, not silently do nothing
def test_update_itinerary_nonexistent_id_raises(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            update_itinerary(9999, title="Doesn't matter")


# ---------- delete_itinerary ----------

# deleting an entry should make it unfindable afterward
def test_delete_itinerary(app):
    with app.app_context():
        create_itinerary(1, 1, "To Be Deleted")
        entry = get_itinerary_by_trip_and_day(1, 1)

        delete_itinerary(entry["id"])

        assert get_itinerary_by_id(entry["id"]) is None

# deleting an id that doesn't exist should not raise — silent no-op
def test_delete_itinerary_nonexistent_id_is_noop(app):
    with app.app_context():
        delete_itinerary(9999)  # should not raise


# ---------- mark_itinerary_complete / mark_itinerary_incomplete ----------

# marking a day complete should be reflected when re-fetched
def test_mark_itinerary_complete(app):
    with app.app_context():
        create_itinerary(1, 1, "Day One")
        entry = get_itinerary_by_trip_and_day(1, 1)

        mark_itinerary_complete(entry["id"])
        updated = get_itinerary_by_id(entry["id"])

        assert updated["completed"] == 1

# marking a completed day incomplete again should undo it
def test_mark_itinerary_incomplete(app):
    with app.app_context():
        create_itinerary(1, 1, "Day One")
        entry = get_itinerary_by_trip_and_day(1, 1)

        mark_itinerary_complete(entry["id"])
        mark_itinerary_incomplete(entry["id"])
        updated = get_itinerary_by_id(entry["id"])

        assert updated["completed"] == 0


# ---------- get_trip_completion_status ----------

# a trip with 2 of 4 days marked complete should report 50%
def test_get_trip_completion_status_partial(app):
    with app.app_context():
        create_itinerary(1, 1, "Day One")
        create_itinerary(1, 2, "Day Two")
        create_itinerary(1, 3, "Day Three")
        create_itinerary(1, 4, "Day Four")

        entries = get_itinerary_by_trip(1)
        mark_itinerary_complete(entries[0]["id"])
        mark_itinerary_complete(entries[1]["id"])

        status = get_trip_completion_status(1)

        assert status["total"] == 4
        assert status["completed"] == 2
        assert status["percentage"] == 50.0

# a trip with zero itinerary entries should report 0% without dividing by zero
def test_get_trip_completion_status_no_entries(app):
    with app.app_context():
        status = get_trip_completion_status(999)

        assert status["total"] == 0
        assert status["completed"] == 0
        assert status["percentage"] == 0

# a fully completed trip should report 100%
def test_get_trip_completion_status_fully_complete(app):
    with app.app_context():
        create_itinerary(1, 1, "Day One")
        create_itinerary(1, 2, "Day Two")

        entries = get_itinerary_by_trip(1)
        mark_itinerary_complete(entries[0]["id"])
        mark_itinerary_complete(entries[1]["id"])

        status = get_trip_completion_status(1)

        assert status["percentage"] == 100.0


# ---------- get_day_date ----------

# day 1 of a trip should equal the trip's start date exactly
def test_get_day_date_day_one(app):
    start = datetime(2026, 6, 1)
    result = get_day_date(start, 1)
    assert result == "2026-06-01T00:00:00"

# day 5 should be 4 days after the start date
def test_get_day_date_day_five(app):
    start = datetime(2026, 6, 1)
    result = get_day_date(start, 5)
    assert result == "2026-06-05T00:00:00"
# tests/test_trip_utils.py
import pytest
from datetime import datetime
from app.utils.trip_utils import (
    validate_rrule,
    expand_recurring_event_raw,
    expand_trip_events_raw,
    generate_ics_from_events,
)


# ---------- validate_rrule ----------

# a well-formed weekly rrule should validate successfully
def test_validate_rrule_valid_weekly():
    valid, error = validate_rrule("FREQ=WEEKLY;BYDAY=MO")
    assert valid is True
    assert error is None

# a well-formed daily rrule should validate successfully
def test_validate_rrule_valid_daily():
    valid, error = validate_rrule("FREQ=DAILY;COUNT=5")
    assert valid is True
    assert error is None

# garbage input should fail validation with an error message
def test_validate_rrule_invalid_garbage():
    valid, error = validate_rrule("this is not a valid rrule")
    assert valid is False
    assert error is not None

# an empty string should fail validation
def test_validate_rrule_empty_string():
    valid, error = validate_rrule("")
    assert valid is False


# ---------- expand_recurring_event_raw ----------

# a non-recurring event with no rrule, inside the window, should be returned as-is
def test_expand_recurring_event_no_rrule_inside_window(app):
    event = {
        "id": 1,
        "trip_id": 1,
        "title": "One-time Event",
        "description": "desc",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
        "timezone": "UTC",
        "rrule": None,
    }

    result = expand_recurring_event_raw(
        event,
        datetime(2026, 6, 1),
        datetime(2026, 6, 8),
    )

    assert len(result) == 1
    assert result[0] == event

# a non-recurring event OUTSIDE the window should return an empty list
def test_expand_recurring_event_no_rrule_outside_window(app):
    event = {
        "id": 1,
        "trip_id": 1,
        "title": "Out of Range",
        "description": "desc",
        "start_time": "2026-06-02T10:00:00",
        "end_time": "2026-06-02T12:00:00",
        "timezone": "UTC",
        "rrule": None,
    }

    result = expand_recurring_event_raw(
        event,
        datetime(2026, 7, 1),
        datetime(2026, 7, 8),
    )

    assert result == []

# a weekly recurring event should expand into multiple occurrences within the window
def test_expand_recurring_event_weekly_expands_multiple_occurrences(app):
    event = {
        "id": 1,
        "trip_id": 1,
        "title": "Weekly Standup",
        "description": "desc",
        "start_time": "2026-06-01T10:00:00",  # a Monday
        "end_time": "2026-06-01T10:30:00",
        "timezone": "UTC",
        "rrule": "FREQ=WEEKLY;BYDAY=MO",
    }

    result = expand_recurring_event_raw(
        event,
        datetime(2026, 6, 1),
        datetime(2026, 6, 22),  # 3-week window
    )

    # should get 3 Monday occurrences: June 1, 8, 15 (22nd is the boundary, exclusive-ish depending on rrule lib)
    assert len(result) >= 3
    for occurrence in result:
        assert occurrence["title"] == "Weekly Standup"
        assert occurrence["id"] == 1

# each expanded occurrence should preserve the original event's duration
def test_expand_recurring_event_preserves_duration(app):
    event = {
        "id": 1,
        "trip_id": 1,
        "title": "Standup",
        "description": None,
        "start_time": "2026-06-01T10:00:00",
        "end_time": "2026-06-01T10:30:00",  # 30 minute duration
        "timezone": "UTC",
        "rrule": "FREQ=WEEKLY;BYDAY=MO",
    }

    result = expand_recurring_event_raw(
        event,
        datetime(2026, 6, 1),
        datetime(2026, 6, 15),
    )

    for occurrence in result:
        start = datetime.fromisoformat(occurrence["start_time"])
        end = datetime.fromisoformat(occurrence["end_time"])
        assert (end - start).total_seconds() == 30 * 60

# a malformed rrule should not crash — should return an empty list
def test_expand_recurring_event_invalid_rrule_returns_empty(app):
    event = {
        "id": 1,
        "trip_id": 1,
        "title": "Broken Event",
        "description": None,
        "start_time": "2026-06-01T10:00:00",
        "end_time": "2026-06-01T10:30:00",
        "timezone": "UTC",
        "rrule": "this is garbage",
    }

    result = expand_recurring_event_raw(
        event,
        datetime(2026, 6, 1),
        datetime(2026, 6, 15),
    )

    assert result == []


# ---------- expand_trip_events_raw ----------

# multiple events should all be expanded and combined into one sorted list
def test_expand_trip_events_combines_and_sorts(app):
    events = [
        {
            "id": 1, "trip_id": 1, "title": "Later Event", "description": None,
            "start_time": "2026-06-05T10:00:00", "end_time": "2026-06-05T11:00:00",
            "timezone": "UTC", "rrule": None,
        },
        {
            "id": 2, "trip_id": 1, "title": "Earlier Event", "description": None,
            "start_time": "2026-06-02T10:00:00", "end_time": "2026-06-02T11:00:00",
            "timezone": "UTC", "rrule": None,
        },
    ]

    result = expand_trip_events_raw(events, datetime(2026, 6, 1), datetime(2026, 6, 8))

    assert len(result) == 2
    # should be sorted chronologically, not in the order they were passed in
    assert result[0]["title"] == "Earlier Event"
    assert result[1]["title"] == "Later Event"

# an empty events list should return an empty list
def test_expand_trip_events_empty_list(app):
    result = expand_trip_events_raw([], datetime(2026, 6, 1), datetime(2026, 6, 8))
    assert result == []


# ---------- generate_ics_from_events ----------

# the generated .ics content should include the event's title and be valid bytes
def test_generate_ics_includes_event_title():
    trip = {"name": "Test Trip"}
    events = [
        {
            "id": 1,
            "title": "Museum Visit",
            "description": "See the Louvre",
            "start_time": "2026-06-02T10:00:00",
            "end_time": "2026-06-02T12:00:00",
            "rrule": None,
        }
    ]

    ics_data = generate_ics_from_events(trip, events)

    assert isinstance(ics_data, bytes)
    assert b"Museum Visit" in ics_data
    assert b"BEGIN:VCALENDAR" in ics_data
    assert b"BEGIN:VEVENT" in ics_data

# an event with an rrule should include the RRULE line in the .ics output
def test_generate_ics_includes_rrule():
    trip = {"name": "Test Trip"}
    events = [
        {
            "id": 1,
            "title": "Weekly Standup",
            "description": "",
            "start_time": "2026-06-02T10:00:00",
            "end_time": "2026-06-02T10:30:00",
            "rrule": "FREQ=WEEKLY;BYDAY=MO",
        }
    ]

    ics_data = generate_ics_from_events(trip, events)

    assert b"RRULE" in ics_data

# a trip with zero events should still produce a valid (empty) calendar
def test_generate_ics_empty_events_list():
    trip = {"name": "Empty Trip"}
    ics_data = generate_ics_from_events(trip, [])

    assert isinstance(ics_data, bytes)
    assert b"BEGIN:VCALENDAR" in ics_data
    assert b"BEGIN:VEVENT" not in ics_data
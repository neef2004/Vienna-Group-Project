# tests/reminder_test.py
import pytest
from datetime import datetime, timedelta
from app.models.trip import create_trip, get_trips_by_user, create_event, get_events_by_trip
from app.models.reminder import (
    create_reminder,
    get_reminders_by_event,
    get_reminder_by_id,
    get_pending_reminders,
    mark_reminder_sent,
    delete_reminder,
    ValidationError,
)


# helper: creates a trip + one event on it, returns the event dict
def make_event(app, start_time=datetime(2026, 6, 2, 10, 0), end_time=datetime(2026, 6, 2, 12, 0)):
    create_trip(1, "Test Trip", "desc", datetime(2026, 6, 1), datetime(2026, 6, 10))
    trip = get_trips_by_user(1)[-1]
    create_event(trip["id"], "Test Event", "desc", start_time, end_time, "UTC", None)
    return get_events_by_trip(trip["id"])[-1]


# ---------- create_reminder ----------

# creating a reminder should let us find it again by event_id
def test_create_and_get_reminder(app):
    with app.app_context():
        event = make_event(app)

        create_reminder(event["id"], user_id=1, minutes_before=30)

        reminders = get_reminders_by_event(event["id"])
        assert len(reminders) == 1
        assert reminders[0]["notification_type"] == "email"  # default

# THE KEY FIX: reminder_time should be anchored to the event's own start_time,
# not to "right now" — this is the core bug we fixed
def test_create_reminder_time_anchored_to_event_start(app):
    with app.app_context():
        event = make_event(app, start_time=datetime(2026, 6, 2, 10, 0))

        create_reminder(event["id"], user_id=1, minutes_before=30)

        reminder = get_reminders_by_event(event["id"])[0]
        reminder_time = datetime.fromisoformat(str(reminder["reminder_time"]))

        # should be exactly 30 minutes before 10:00 on the event's actual day —
        # NOT anywhere near today's real-world date
        assert reminder_time == datetime(2026, 6, 2, 9, 30)

# minutes_before=0 should mean the reminder fires exactly at event start
def test_create_reminder_zero_minutes_before(app):
    with app.app_context():
        event = make_event(app, start_time=datetime(2026, 6, 2, 10, 0))

        create_reminder(event["id"], user_id=1, minutes_before=0)

        reminder = get_reminders_by_event(event["id"])[0]
        reminder_time = datetime.fromisoformat(str(reminder["reminder_time"]))

        assert reminder_time == datetime(2026, 6, 2, 10, 0)

# a custom notification_type should be stored correctly
def test_create_reminder_custom_notification_type(app):
    with app.app_context():
        event = make_event(app)

        create_reminder(event["id"], user_id=1, minutes_before=15, notification_type="sms")

        reminder = get_reminders_by_event(event["id"])[0]
        assert reminder["notification_type"] == "sms"

# a negative minutes_before should be rejected
def test_create_reminder_negative_minutes_before_raises(app):
    with app.app_context():
        event = make_event(app)

        with pytest.raises(ValidationError):
            create_reminder(event["id"], user_id=1, minutes_before=-10)

# a non-integer minutes_before should be rejected
def test_create_reminder_non_integer_minutes_before_raises(app):
    with app.app_context():
        event = make_event(app)

        with pytest.raises(ValidationError):
            create_reminder(event["id"], user_id=1, minutes_before="thirty")

# an invalid notification_type should be rejected
def test_create_reminder_invalid_notification_type_raises(app):
    with app.app_context():
        event = make_event(app)

        with pytest.raises(ValidationError):
            create_reminder(event["id"], user_id=1, minutes_before=30, notification_type="carrier_pigeon")

# creating a reminder for an event that doesn't exist should raise, not silently insert garbage
def test_create_reminder_nonexistent_event_raises(app):
    with app.app_context():
        with pytest.raises(ValidationError):
            create_reminder(event_id=9999, user_id=1, minutes_before=30)


# ---------- get_reminders_by_event ----------

# an event with no reminders should return an empty list
def test_get_reminders_by_event_empty(app):
    with app.app_context():
        event = make_event(app)

        reminders = get_reminders_by_event(event["id"])
        assert reminders == []

# should only return reminders for that event, not reminders on other events
def test_get_reminders_by_event_only_returns_matching_event(app):
    with app.app_context():
        event_one = make_event(app, start_time=datetime(2026, 6, 2, 10, 0), end_time=datetime(2026, 6, 2, 12, 0))
        event_two = make_event(app, start_time=datetime(2026, 6, 3, 10, 0), end_time=datetime(2026, 6, 3, 12, 0))

        create_reminder(event_one["id"], user_id=1, minutes_before=30)
        create_reminder(event_two["id"], user_id=1, minutes_before=15)

        event_one_reminders = get_reminders_by_event(event_one["id"])

        assert len(event_one_reminders) == 1


# ---------- get_reminder_by_id ----------

# should return the correct reminder by its own id
def test_get_reminder_by_id(app):
    with app.app_context():
        event = make_event(app)
        create_reminder(event["id"], user_id=1, minutes_before=30)
        reminder = get_reminders_by_event(event["id"])[0]

        fetched = get_reminder_by_id(reminder["id"])

        assert fetched is not None
        assert fetched["id"] == reminder["id"]

# a nonexistent reminder_id should return None, not raise
def test_get_reminder_by_id_not_found(app):
    with app.app_context():
        result = get_reminder_by_id(9999)
        assert result is None


# ---------- get_pending_reminders ----------

# a reminder whose time is in the past (relative to now) and not yet sent should be "pending"
def test_get_pending_reminders_includes_past_unsent(app):
    with app.app_context():
        # event started well in the past, so its reminder_time is also in the past
        event = make_event(app, start_time=datetime(2020, 1, 1, 10, 0), end_time=datetime(2020, 1, 1, 12, 0))
        create_reminder(event["id"], user_id=1, minutes_before=30)

        pending = get_pending_reminders()

        assert len(pending) == 1

# a reminder whose time is in the future should NOT be pending yet
def test_get_pending_reminders_excludes_future(app):
    with app.app_context():
        # event far in the future, so its reminder_time is also in the future
        event = make_event(app, start_time=datetime(2030, 1, 1, 10, 0), end_time=datetime(2030, 1, 1, 12, 0))
        create_reminder(event["id"], user_id=1, minutes_before=30)

        pending = get_pending_reminders()

        assert len(pending) == 0

# a reminder already marked sent should NOT show up as pending, even if its time has passed
def test_get_pending_reminders_excludes_already_sent(app):
    with app.app_context():
        event = make_event(app, start_time=datetime(2020, 1, 1, 10, 0), end_time=datetime(2020, 1, 1, 12, 0))
        create_reminder(event["id"], user_id=1, minutes_before=30)
        reminder = get_reminders_by_event(event["id"])[0]

        mark_reminder_sent(reminder["id"])

        pending = get_pending_reminders()
        assert len(pending) == 0


# ---------- mark_reminder_sent ----------

# marking a reminder sent should be reflected when re-fetched
def test_mark_reminder_sent(app):
    with app.app_context():
        event = make_event(app)
        create_reminder(event["id"], user_id=1, minutes_before=30)
        reminder = get_reminders_by_event(event["id"])[0]

        mark_reminder_sent(reminder["id"])

        updated = get_reminder_by_id(reminder["id"])
        assert updated["sent"] == 1


# ---------- delete_reminder ----------

# deleting a reminder should make it unfindable afterward
def test_delete_reminder(app):
    with app.app_context():
        event = make_event(app)
        create_reminder(event["id"], user_id=1, minutes_before=30)
        reminder = get_reminders_by_event(event["id"])[0]

        delete_reminder(reminder["id"])

        assert get_reminder_by_id(reminder["id"]) is None

# deleting a nonexistent reminder_id should not raise — silent no-op
def test_delete_reminder_nonexistent_is_noop(app):
    with app.app_context():
        delete_reminder(9999)  # should not raise
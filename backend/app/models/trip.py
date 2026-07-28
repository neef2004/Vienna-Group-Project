from app.db import get_db
from datetime import datetime

# create trip to the database
# trip_id primary key(int)
# attributes: trip_id(int), name(str), description(str), start_date(date/time), end_date(date/time)
def create_trip(user_id, name, description, start_date, end_date):
    db = get_db()
    
    db.execute(
        "INSERT INTO trip (user_id, name, description, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, description, start_date, end_date)
    )
    
    db.commit()

# retrieve trip from database using trip_id and user_id
def get_trip_by_id(trip_id, user_id):
    db = get_db()
    
    return db.execute(
        """
        SELECT t.*, u.email AS owner_email
        FROM trip t
        JOIN users u ON u.id = t.user_id
        LEFT JOIN trip_collaborator tc
          ON tc.trip_id = t.id
         AND tc.user_id = ?
         AND tc.accepted = 1
        WHERE t.id = ?
          AND (t.user_id = ? OR tc.user_id IS NOT NULL)
        """,
        (user_id, trip_id, user_id)
    ).fetchone()

# get trips using just user_id
def get_trips_by_user(user_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM trip WHERE user_id = ?",
        (user_id,)
    ).fetchall()

# update trip with new name, description, start and end dates
def update_trip(trip_id, name, description, start_date, end_date):
    db = get_db()
    
    db.execute(
        "UPDATE trip SET name = ?, description = ?, start_date = ?, end_date = ? WHERE id = ?",
        (name, description, start_date, end_date, trip_id)
    )
    
    db.commit()

# delete trip from database using trip_id
def delete_trip(trip_id):
    db = get_db()
    
    db.execute("DELETE FROM trip WHERE id = ?", (trip_id,))
    db.commit()

# create event as part of trip with trip_id
# attributes: trip_id, title, descriptioin, start and end time, timezone, rrule
# rrule: recurring event rule for icalendar
def create_event(trip_id, title, description, start_time, end_time, timezone, rrule):
    db = get_db()
    
    db.execute(
        "INSERT INTO event (trip_id, title, description, start_time, end_time, timezone, rrule) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (trip_id, title, description, start_time, end_time, timezone, rrule)
    )
    
    db.commit()

# retrieve event using event_id
def get_event_by_id(event_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM event WHERE id = ?",
        (event_id,)
    ).fetchone()

# retrieve event that a trip_id is under
def get_events_by_trip(trip_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM event WHERE trip_id = ?",
        (trip_id,)
    ).fetchall()

# update event: event_id
# attributes: event_id, title, descriptioin, start and end time, timezone, rrule
# rrule: recurring event rule for icalendar
def update_event(event_id, title, description, start_time, end_time, timezone, rrule):
    db = get_db()
    
    db.execute(
        "UPDATE event SET title = ?, description = ?, start_time = ?, end_time = ?, timezone = ?, rrule = ? WHERE id = ?",
        (title, description, start_time, end_time, timezone, rrule, event_id)
    )
    
    db.commit()

# delete event using event_id
def delete_event(event_id):
    db = get_db()
    
    db.execute("DELETE FROM event WHERE id = ?", (event_id,))
    db.commit()

# add collaborators to a trip
# attributes: trip_id, user_id, permission_level
# default permission level = editor
def add_trip_collaborator(trip_id, user_id, permission_level='editor'):
    db = get_db()
    
    db.execute(
        "INSERT INTO trip_collaborator (trip_id, user_id, permission_level) VALUES (?, ?, ?)",
        (trip_id, user_id, permission_level)
    )
    
    db.commit()

# get trip collaborators using trip_id
def get_trip_collaborators(trip_id):
    db = get_db()
    
    return db.execute(
        """
        SELECT tc.*, u.email
        FROM trip_collaborator tc
        JOIN users u ON u.id = tc.user_id
        WHERE tc.trip_id = ?
        ORDER BY tc.invited_at
        """,
        (trip_id,)
    ).fetchall()

# get permission level for a user for a trip (user_id, trip_id)
def get_user_permission_for_trip(trip_id, user_id):
    db = get_db()
    
    result = db.execute(
        "SELECT permission_level FROM trip_collaborator WHERE trip_id = ? AND user_id = ?",
        (trip_id, user_id)
    ).fetchone()
    
    return result['permission_level'] if result else None

# set invitation as accepted for a user
def accept_trip_invitation(trip_id, user_id):
    db = get_db()
    
    db.execute(
        "UPDATE trip_collaborator SET accepted = 1, accepted_at = ? WHERE trip_id = ? AND user_id = ?",
        (datetime.utcnow(), trip_id, user_id)
    )
    
    db.commit()

# remove a collaborator from a trip
def remove_trip_collaborator(trip_id, user_id):
    db = get_db()
    
    db.execute(
        "DELETE FROM trip_collaborator WHERE trip_id = ? AND user_id = ?",
        (trip_id, user_id)
    )
    
    db.commit()

# update collaborator permission level
def update_collaborator_permission(trip_id, user_id, permission_level):
    db = get_db()
    
    db.execute(
        "UPDATE trip_collaborator SET permission_level = ? WHERE trip_id = ? AND user_id = ?",
        (permission_level, trip_id, user_id)
    )
    
    db.commit()

# retrieve all trips for a given user
def get_user_trips(user_id):
    db = get_db()
    
    return db.execute(
        """
        SELECT DISTINCT t.*, u.email AS owner_email
        FROM trip t
        JOIN users u ON u.id = t.user_id
        LEFT JOIN trip_collaborator tc
          ON tc.trip_id = t.id
         AND tc.user_id = ?
         AND tc.accepted = 1
        WHERE t.user_id = ? OR tc.user_id IS NOT NULL
        ORDER BY t.created_at
        """,
        (user_id, user_id)
    ).fetchall()

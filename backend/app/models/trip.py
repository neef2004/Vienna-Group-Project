from app.db import get_db
from datetime import datetime

def create_trip(user_id, name, description, start_date, end_date):
    db = get_db()
    
    db.execute(
        "INSERT INTO trip (user_id, name, description, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, description, start_date, end_date)
    )
    
    db.commit()

def get_trip_by_id(trip_id, user_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM trip WHERE id = ? AND user_id = ?",
        (trip_id, user_id)
    ).fetchone()

def get_trips_by_user(user_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM trip WHERE user_id = ?",
        (user_id,)
    ).fetchall()

def update_trip(trip_id, name, description, start_date, end_date):
    db = get_db()
    
    db.execute(
        "UPDATE trip SET name = ?, description = ?, start_date = ?, end_date = ? WHERE id = ?",
        (name, description, start_date, end_date, trip_id)
    )
    
    db.commit()

def delete_trip(trip_id):
    db = get_db()
    
    db.execute("DELETE FROM trip WHERE id = ?", (trip_id,))
    db.commit()

def create_event(trip_id, title, description, start_time, end_time, timezone, rrule):
    db = get_db()
    
    db.execute(
        "INSERT INTO event (trip_id, title, description, start_time, end_time, timezone, rrule) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (trip_id, title, description, start_time, end_time, timezone, rrule)
    )
    
    db.commit()

def get_event_by_id(event_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM event WHERE id = ?",
        (event_id,)
    ).fetchone()

def get_events_by_trip(trip_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM event WHERE trip_id = ?",
        (trip_id,)
    ).fetchall()

def update_event(event_id, title, description, start_time, end_time, timezone, rrule):
    db = get_db()
    
    db.execute(
        "UPDATE event SET title = ?, description = ?, start_time = ?, end_time = ?, timezone = ?, rrule = ? WHERE id = ?",
        (title, description, start_time, end_time, timezone, rrule, event_id)
    )
    
    db.commit()

def delete_event(event_id):
    db = get_db()
    
    db.execute("DELETE FROM event WHERE id = ?", (event_id,))
    db.commit()

def add_trip_collaborator(trip_id, user_id, permission_level='editor'):
    db = get_db()
    
    db.execute(
        "INSERT INTO trip_collaborator (trip_id, user_id, permission_level) VALUES (?, ?, ?)",
        (trip_id, user_id, permission_level)
    )
    
    db.commit()

def get_trip_collaborators(trip_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM trip_collaborator WHERE trip_id = ?",
        (trip_id,)
    ).fetchall()

def get_user_permission_for_trip(trip_id, user_id):
    db = get_db()
    
    result = db.execute(
        "SELECT permission_level FROM trip_collaborator WHERE trip_id = ? AND user_id = ?",
        (trip_id, user_id)
    ).fetchone()
    
    return result['permission_level'] if result else None

def accept_trip_invitation(trip_id, user_id):
    db = get_db()
    
    db.execute(
        "UPDATE trip_collaborator SET accepted = 1, accepted_at = ? WHERE trip_id = ? AND user_id = ?",
        (datetime.utcnow(), trip_id, user_id)
    )
    
    db.commit()

def remove_trip_collaborator(trip_id, user_id):
    db = get_db()
    
    db.execute(
        "DELETE FROM trip_collaborator WHERE trip_id = ? AND user_id = ?",
        (trip_id, user_id)
    )
    
    db.commit()

def update_collaborator_permission(trip_id, user_id, permission_level):
    db = get_db()
    
    db.execute(
        "UPDATE trip_collaborator SET permission_level = ? WHERE trip_id = ? AND user_id = ?",
        (permission_level, trip_id, user_id)
    )
    
    db.commit()

def get_user_trips(user_id):
    db = get_db()
    
    return db.execute(
        "SELECT t.* FROM trip t LEFT JOIN trip_collaborator tc ON t.id = tc.trip_id WHERE t.user_id = ? OR tc.user_id = ? AND tc.accepted = 1",
        (user_id, user_id)
    ).fetchall()
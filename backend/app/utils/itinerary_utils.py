from datetime import datetime, timedelta
from app.db import get_db


def create_itinerary(trip_id, day_number, title=None, description=None, activities=None):
    db = get_db()
    
    db.execute(
        "INSERT INTO itinerary (trip_id, day_number, title, description, activities) VALUES (?, ?, ?, ?, ?)",
        (trip_id, day_number, title, description, activities)
    )
    
    db.commit()


def get_itinerary_by_id(itinerary_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM itinerary WHERE id = ?",
        (itinerary_id,)
    ).fetchone()


def get_itinerary_by_trip_and_day(trip_id, day_number):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM itinerary WHERE trip_id = ? AND day_number = ?",
        (trip_id, day_number)
    ).fetchone()


def get_itinerary_by_trip(trip_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM itinerary WHERE trip_id = ? ORDER BY day_number",
        (trip_id,)
    ).fetchall()


def update_itinerary(itinerary_id, title=None, description=None, activities=None):
    db = get_db()
    
    db.execute(
        "UPDATE itinerary SET title = ?, description = ?, activities = ?, updated_at = ? WHERE id = ?",
        (title, description, activities, datetime.utcnow(), itinerary_id)
    )
    
    db.commit()


def delete_itinerary(itinerary_id):
    db = get_db()
    
    db.execute("DELETE FROM itinerary WHERE id = ?", (itinerary_id,))
    db.commit()


def get_day_date(trip_start_date, day_number):
    day_offset = day_number - 1
    return (trip_start_date + timedelta(days=day_offset)).isoformat()
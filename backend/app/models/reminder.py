from datetime import datetime, timedelta
from app.db import get_db


def create_reminder(event_id, user_id, minutes_before, notification_type='email'):
    db = get_db()
    
    db.execute(
        "INSERT INTO reminder (event_id, user_id, reminder_time, notification_type) VALUES (?, ?, ?, ?)",
        (event_id, user_id, datetime.utcnow() + timedelta(minutes=minutes_before), notification_type)
    )
    
    db.commit()


def get_reminders_by_event(event_id):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM reminder WHERE event_id = ?",
        (event_id,)
    ).fetchall()


def get_pending_reminders():
    db = get_db()
    
    return db.execute(
        "SELECT * FROM reminder WHERE sent = 0 AND reminder_time <= ?",
        (datetime.utcnow(),)
    ).fetchall()


def mark_reminder_sent(reminder_id):
    db = get_db()
    
    db.execute("UPDATE reminder SET sent = 1 WHERE id = ?", (reminder_id,))
    db.commit()


def delete_reminder(reminder_id):
    db = get_db()
    
    db.execute("DELETE FROM reminder WHERE id = ?", (reminder_id,))
    db.commit()
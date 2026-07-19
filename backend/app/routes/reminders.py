from flask import Blueprint, request, jsonify
from datetime import datetime
from functools import wraps

from app.models.trip import get_trip_by_id, get_event_by_id
from app.models.reminder import (
    create_reminder,
    get_reminders_by_event,
    delete_reminder
)

reminders_bp = Blueprint('reminders', __name__, url_prefix='/api/trips')


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, user_id=int(user_id), **kwargs)
    return decorated_function


@reminders_bp.route('/<int:trip_id>/events/<int:event_id>/reminders', methods=['GET'])
@require_auth
def get_event_reminders(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        reminders = get_reminders_by_event(event_id)
        
        return jsonify([dict(r) for r in reminders]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reminders_bp.route('/<int:trip_id>/events/<int:event_id>/reminders', methods=['POST'])
@require_auth
def create_event_reminder(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        
        minutes_before = data.get('minutes_before', 30)
        notification_type = data.get('notification_type', 'email')
        
        create_reminder(event_id, user_id, minutes_before, notification_type)
        
        reminders = get_reminders_by_event(event_id)
        
        return jsonify([dict(r) for r in reminders]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reminders_bp.route('/<int:trip_id>/reminders/<int:reminder_id>', methods=['DELETE'])
@require_auth
def delete_event_reminder(trip_id, reminder_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        delete_reminder(reminder_id)
        
        return jsonify({'message': 'Reminder deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
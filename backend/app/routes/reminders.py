from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from datetime import datetime
from functools import wraps

from app.models.trip import get_trip_by_id, get_event_by_id
from app.models.reminder import (
    create_reminder,
    get_reminders_by_event,
    get_reminder_by_id,
    delete_reminder,
    ValidationError,
)

# all urls start with /api/trips
reminders_bp = Blueprint('reminders', __name__, url_prefix='/api/trips')

# login check for every route below.
def require_auth(f):
    @wraps(f) # keep the wrapped route's name/info intact
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if not user_id:
            # no valid token means not logged in
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'error': 'Invalid token identity'}), 401

        # hand user_id to the route
        return f(*args, user_id=user_id, **kwargs)
    return decorated_function

# GET /api/trips/<trip_id(int, required)>/events/<event_id(int, required)>/reminders, list all reminders on an event.
# method: GET
# header: Authorization: Bearer <jwt>
# body: none
# return list of reminders (200), 404 if no trip or no event, 500 if error
@reminders_bp.route('/<int:trip_id>/events/<int:event_id>/reminders', methods=['GET'])
@require_auth
# List every reminder attached to one event.
def get_event_reminders(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id) # scoped to user_id, so it also checks access
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        # event must exist AND belong to this trip
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        reminders = get_reminders_by_event(event_id)
        
        # turn each db row into a dict so it can be json'd
        return jsonify([dict(r) for r in reminders]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST /api/trips/<trip_id(int, required)>/events/<event_id(int, required)>/reminders, add a reminder to an event.
# method: POST
# header: Authorization: Bearer <jwt>
# body(json): minutes_before(int, default 30), notification_type(str, default "email")
# return full list of reminders on the event (201), 404 if no trip or no event, 500 if error
@reminders_bp.route('/<int:trip_id>/events/<int:event_id>/reminders', methods=['POST'])
@require_auth
# Add a reminder to one event, then return the event's full reminder list.
def create_event_reminder(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        # event must exist AND belong to this trip
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid or missing JSON body'}), 400
        
        # both fields are optional, so fall back to defaults if not sent
        minutes_before = data.get('minutes_before', 30) # fire 30 min before by default
        notification_type = data.get('notification_type', 'email') # email by default
        
        try:
            create_reminder(event_id, user_id, minutes_before, notification_type)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        
        # re-fetch so we return the updated list including the new reminder
        reminders = get_reminders_by_event(event_id)
        
        return jsonify([dict(r) for r in reminders]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE /api/trips/<trip_id(int, required)>/reminders/<reminder_id(int, required)>, remove a reminder.
# method: DELETE
# header: Authorization: Bearer <jwt>
# body: none
# return {"message":"Reminder deleted"} (200), 404 if no trip, 500 if error
@reminders_bp.route('/<int:trip_id>/reminders/<int:reminder_id>', methods=['DELETE'])
@require_auth
def delete_event_reminder(trip_id, reminder_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id) # only checks the trip, not the reminder itself
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        reminder = get_reminder_by_id(reminder_id)
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
        
        event = get_event_by_id(reminder['event_id'])
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Reminder not found'}), 404
        
        # deletes by reminder_id without checking it belongs to this trip/user
        delete_reminder(reminder_id)
        
        return jsonify({'message': 'Reminder deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
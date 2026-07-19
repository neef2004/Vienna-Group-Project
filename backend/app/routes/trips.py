from flask import Blueprint, request, jsonify
from datetime import datetime
from functools import wraps
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
    delete_event
)

from app.utils.trip_utils import (
    expand_trip_events_raw,
    expand_recurring_event_raw,
    import_ics_to_trip,
    validate_rrule,
    generate_ics_from_events
)

trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, user_id=int(user_id), **kwargs)
    return decorated_function


@trips_bp.route('', methods=['GET'])
@require_auth
def get_trips(user_id):
    try:
        trips = get_trips_by_user(user_id)
        return jsonify([dict(trip) for trip in trips]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('', methods=['POST'])
@require_auth
def create_trip_route(user_id):
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Trip name is required'}), 400
        
        start_date = datetime.fromisoformat(data.get('start_date'))
        end_date = datetime.fromisoformat(data.get('end_date'))
        
        if start_date >= end_date:
            return jsonify({'error': 'start_date must be before end_date'}), 400
        
        create_trip(user_id, data['name'], data.get('description'), start_date, end_date)
        
        trip = get_trips_by_user(user_id)[-1]
        
        return jsonify(dict(trip)), 201
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>', methods=['GET'])
@require_auth
def get_trip(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        events = get_events_by_trip(trip_id)
        trip_dict = dict(trip)
        trip_dict['events'] = [dict(e) for e in events]
        
        return jsonify(trip_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>', methods=['PUT'])
@require_auth
def update_trip_route(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        data = request.get_json()
        
        name = data.get('name', trip['name'])
        description = data.get('description', trip['description'])
        start_date = data.get('start_date', trip['start_date'])
        end_date = data.get('end_date', trip['end_date'])
        
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        if start_date >= end_date:
            return jsonify({'error': 'start_date must be before end_date'}), 400
        
        update_trip(trip_id, name, description, start_date, end_date)
        
        updated_trip = get_trip_by_id(trip_id, user_id)
        
        return jsonify(dict(updated_trip)), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>', methods=['DELETE'])
@require_auth
def delete_trip_route(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        delete_trip(trip_id)
        
        return jsonify({'message': 'Trip deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>/events', methods=['GET'])
@require_auth
def get_events(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        start_param = request.args.get('start')
        end_param = request.args.get('end')
        
        if not start_param or not end_param:
            return jsonify({'error': 'start and end query parameters required'}), 400
        
        try:
            start_date = datetime.fromisoformat(start_param)
            end_date = datetime.fromisoformat(end_param)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
        
        if start_date >= end_date:
            return jsonify({'error': 'start must be before end'}), 400
        
        events = get_events_by_trip(trip_id)
        events_list = [dict(e) for e in events]
        
        occurrences = expand_trip_events_raw(events_list, start_date, end_date)
        
        return jsonify(occurrences), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>/events', methods=['POST'])
@require_auth
def create_event_route(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        data = request.get_json()
        
        required_fields = ['title', 'start_time', 'end_time']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Required fields: {required_fields}'}), 400
        
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        
        if start_time >= end_time:
            return jsonify({'error': 'start_time must be before end_time'}), 400
        
        rrule = data.get('rrule')
        if rrule:
            valid, error = validate_rrule(rrule)
            if not valid:
                return jsonify({'error': f'Invalid RRULE: {error}'}), 400
        
        create_event(trip_id, data['title'], data.get('description'), start_time, end_time, data.get('timezone', 'UTC'), rrule)
        
        event = get_events_by_trip(trip_id)[-1]
        
        return jsonify(dict(event)), 201
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>/events/<int:event_id>', methods=['PUT'])
@require_auth
def update_event_route(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        
        title = data.get('title', event['title'])
        description = data.get('description', event['description'])
        start_time = data.get('start_time', event['start_time'])
        end_time = data.get('end_time', event['end_time'])
        timezone = data.get('timezone', event['timezone'])
        rrule = data.get('rrule', event['rrule'])
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        
        if start_time >= end_time:
            return jsonify({'error': 'start_time must be before end_time'}), 400
        
        if rrule:
            valid, error = validate_rrule(rrule)
            if not valid:
                return jsonify({'error': f'Invalid RRULE: {error}'}), 400
        
        update_event(event_id, title, description, start_time, end_time, timezone, rrule)
        
        updated_event = get_event_by_id(event_id)
        
        return jsonify(dict(updated_event)), 200
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>/events/<int:event_id>', methods=['DELETE'])
@require_auth
def delete_event_route(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        delete_event(event_id)
        
        return jsonify({'message': 'Event deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@trips_bp.route('/<int:trip_id>/calendar.ics', methods=['GET'])
@require_auth
def export_calendar(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        events = get_events_by_trip(trip_id)
        events_list = [dict(e) for e in events]
        
        ics_data = generate_ics_from_events(trip, events_list)
        
        return ics_data, 200, {
            'Content-Type': 'text/calendar',
            'Content-Disposition': f'attachment; filename="{trip["name"]}.ics"'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500
from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
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

# all routes start with /api/trips
trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')

# login check for every route below.
# header: X-User-ID (int), required
def require_auth(f):
    @wraps(f) # keep the wrapped route's name/info intact
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity()) # header value is text or None
        # convert to int and hand user_id to the route
        return f(*args, user_id=user_id, **kwargs)
    return decorated_function

# GET /api/trips, list all trips of the user.
# method: GET
# header: X-User-ID (int)
# body: none
# return list of trips (200), 500 if error
@trips_bp.route('', methods=['GET'])
@require_auth
# List every trip owned by the current user.
def get_trips(user_id):
    try:
        trips = get_trips_by_user(user_id)
        # turn each db row into a dict so it can be json'd
        return jsonify([dict(trip) for trip in trips]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST /api/trips, make a new trip.
# method: POST
# header: X-User-ID (int)
# body(json): name(str, required), description(str), start_date(str iso, required), end_date(str iso, required)
# return new trip (201), 400 if bad input, 500 if error
@trips_bp.route('', methods=['POST'])
@require_auth
# Create a new trip after validating name and the date range.
def create_trip_route(user_id):
    try:
        data = request.get_json()
        
        if not data.get('name'):
            # name is required
            return jsonify({'error': 'Trip name is required'}), 400
        
        # parse iso strings into datetimes (raises ValueError if malformed -> caught below)
        start_date = datetime.fromisoformat(data.get('start_date'))
        end_date = datetime.fromisoformat(data.get('end_date'))
        
        if start_date >= end_date:
            # a trip must start before it ends
            return jsonify({'error': 'start_date must be before end_date'}), 400
        
        create_trip(user_id, data['name'], data.get('description'), start_date, end_date)
        
        # create_trip doesn't return the row, so grab the newest one (last in the list)
        trip = get_trips_by_user(user_id)[-1]
        
        return jsonify(dict(trip)), 201
    except ValueError:
        # a date string wasn't valid iso
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET /api/trips/<trip_id(int, required)>, one trip plus its events.
# method: GET
# header: X-User-ID (int)
# body: none
# return trip with "events" list (200), 404 if no trip, 500 if error
@trips_bp.route('/<int:trip_id>', methods=['GET'])
@require_auth
# Get one trip and attach all of its events under an "events" key.
def get_trip(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        events = get_events_by_trip(trip_id)
        trip_dict = dict(trip)
        # embed the events list inside the trip object
        trip_dict['events'] = [dict(e) for e in events]
        
        return jsonify(trip_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>, change trip. fields not sent keep old value.
# method: PUT
# header: X-User-ID (int)
# body(json, all optional): name(str), description(str), start_date(str iso), end_date(str iso)
# return updated trip (200), 400 if bad input, 404 if no trip, 500 if error
@trips_bp.route('/<int:trip_id>', methods=['PUT'])
@require_auth
# Update a trip. Any field not sent keeps its current value.
def update_trip_route(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        data = request.get_json()
        
        # fall back to the existing value when a field isn't sent (partial update)
        name = data.get('name', trip['name'])
        description = data.get('description', trip['description'])
        start_date = data.get('start_date', trip['start_date'])
        end_date = data.get('end_date', trip['end_date'])
        
        # incoming dates may be iso strings (from json) or already datetimes (kept from db);
        # only parse when they're strings
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        if start_date >= end_date:
            # a trip must start before it ends
            return jsonify({'error': 'start_date must be before end_date'}), 400
        
        update_trip(trip_id, name, description, start_date, end_date)
        
        # re-fetch so we return the fresh row
        updated_trip = get_trip_by_id(trip_id, user_id)
        
        return jsonify(dict(updated_trip)), 200
    except ValueError:
        # a date string wasn't valid iso
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE /api/trips/<trip_id(int, required)>, remove trip.
# method: DELETE
# header: X-User-ID (int)
# body: none
# return {"message":"Trip deleted"} (200), 404 if no trip, 500 if error
@trips_bp.route('/<int:trip_id>', methods=['DELETE'])
@require_auth
# Delete a trip.
def delete_trip_route(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id) # also confirms the user owns/can see it
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        delete_trip(trip_id)
        
        return jsonify({'message': 'Trip deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET /api/trips/<trip_id(int, required)>/events?start(str iso, required), end(str iso, required), events between two dates (repeating events expanded).
# method: GET
# header: X-User-ID (int)
# body: none
# return list of occurrences (200), 400 if missing/bad dates, 404 if no trip, 500 if error
@trips_bp.route('/<int:trip_id>/events', methods=['GET'])
@require_auth
# List event occurrences in a date window; recurring events are expanded into each occurrence.
def get_events(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        # start/end come from the query string (after "?"), so they're text or None
        start_param = request.args.get('start')
        end_param = request.args.get('end')
        
        if not start_param or not end_param:
            # both window bounds are required
            return jsonify({'error': 'start and end query parameters required'}), 400
        
        # parse the window; bad iso -> 400 (handled right here, not by the outer except)
        try:
            start_date = datetime.fromisoformat(start_param)
            end_date = datetime.fromisoformat(end_param)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
        
        if start_date >= end_date:
            # window start must be before window end
            return jsonify({'error': 'start must be before end'}), 400
        
        events = get_events_by_trip(trip_id)
        events_list = [dict(e) for e in events]
        
        # expand stored events (some recurring) into concrete occurrences inside the window
        occurrences = expand_trip_events_raw(events_list, start_date, end_date)
        
        return jsonify(occurrences), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST /api/trips/<trip_id(int, required)>/events, make a calendar event.  <-- SCRUM MASTER: this one
# method: POST
# header: X-User-ID (int)
# body(json): title(str, required), start_time(str iso, required), end_time(str iso, required),
#             description(str), timezone(str, default UTC), rrule(str, repeat e.g. "FREQ=WEEKLY;BYDAY=MO")
# return new event (201), 400 if bad input, 404 if no trip, 500 if error
@trips_bp.route('/<int:trip_id>/events', methods=['POST'])
@require_auth
# Create a calendar event on a trip; validates required fields, the time range, and any rrule.
def create_event_route(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        data = request.get_json()
        
        # every one of these must be present in the body
        required_fields = ['title', 'start_time', 'end_time']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Required fields: {required_fields}'}), 400
        
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        
        if start_time >= end_time:
            # event must start before it ends
            return jsonify({'error': 'start_time must be before end_time'}), 400
        
        # rrule is optional; only validate it if one was sent
        rrule = data.get('rrule')
        if rrule:
            valid, error = validate_rrule(rrule) # returns (bool, message)
            if not valid:
                return jsonify({'error': f'Invalid RRULE: {error}'}), 400
        
        # timezone defaults to UTC when not provided
        create_event(trip_id, data['title'], data.get('description'), start_time, end_time, data.get('timezone', 'UTC'), rrule)
        
        # create_event doesn't return the row, so grab the newest one (last in the list)
        event = get_events_by_trip(trip_id)[-1]
        
        return jsonify(dict(event)), 201
    except ValueError:
        # a date string wasn't valid iso
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>/events/<event_id(int, required)>, change event. fields not sent keep old value.
# method: PUT
# header: X-User-ID (int)
# body(json, all optional): title(str), description(str), start_time(str iso),
#                           end_time(str iso), timezone(str), rrule(str)
# return updated event (200), 400 if bad input, 404 if no event, 500 if error
@trips_bp.route('/<int:trip_id>/events/<int:event_id>', methods=['PUT'])
@require_auth
# Update an event. Any field not sent keeps its current value.
def update_event_route(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        event = get_event_by_id(event_id)
        
        # event must exist AND belong to this trip
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        
        # fall back to the existing value when a field isn't sent (partial update)
        title = data.get('title', event['title'])
        description = data.get('description', event['description'])
        start_time = data.get('start_time', event['start_time'])
        end_time = data.get('end_time', event['end_time'])
        timezone = data.get('timezone', event['timezone'])
        rrule = data.get('rrule', event['rrule'])
        
        # only parse the times that came in as strings
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        
        if start_time >= end_time:
            # event must start before it ends
            return jsonify({'error': 'start_time must be before end_time'}), 400
        
        # validate rrule only if there is one
        if rrule:
            valid, error = validate_rrule(rrule)
            if not valid:
                return jsonify({'error': f'Invalid RRULE: {error}'}), 400

        update_event(event_id, title, description, start_time, end_time, timezone, rrule)
        
        # re-fetch so we return the fresh row
        updated_event = get_event_by_id(event_id)
        
        return jsonify(dict(updated_event)), 200
    except ValueError:
        # a date string wasn't valid iso
        return jsonify({'error': 'Invalid date format. Use ISO 8601.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE /api/trips/<trip_id>/events/<event_id>, remove event.
# method: DELETE
# header: X-User-ID (int)
# url: trip_id(int, required), event_id(int, required)
# body: none
# return {"message":"Event deleted"} (200), 404 if no event, 500 if error
@trips_bp.route('/<int:trip_id>/events/<int:event_id>', methods=['DELETE'])
@require_auth
# Delete one event, confirming it belongs to the given trip first.
def delete_event_route(trip_id, event_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)

        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404

        event = get_event_by_id(event_id)

        # event must exist AND belong to this trip
        if not event or event['trip_id'] != trip_id:
            return jsonify({'error': 'Event not found'}), 404

        delete_event(event_id)
        
        return jsonify({'message': 'Event deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET /api/trips/<trip_id>/calendar.ics, download .ics file (google/outlook/apple calendar).
# method: GET
# header: X-User-ID (int)
# url: trip_id(int, required)
# body: none
# return .ics file text, type text/calendar (200), 404 if no trip, 500 if error
@trips_bp.route('/<int:trip_id>/calendar.ics', methods=['GET'])
@require_auth
# Build and return an .ics calendar file containing all of the trip's events.
def export_calendar(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)

        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404

        events = get_events_by_trip(trip_id)
        events_list = [dict(e) for e in events]
        
        # build the .ics document text from the trip & its events
        ics_data = generate_ics_from_events(trip, events_list)

        # return raw text with calendar headers so the browser downloads it as a file
        return ics_data, 200, {
            'Content-Type': 'text/calendar',
            'Content-Disposition': f'attachment; filename="{trip["name"]}.ics"'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500
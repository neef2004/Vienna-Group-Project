from flask import Blueprint, request, jsonify
from datetime import datetime
from functools import wraps

from app.models.trip import get_trip_by_id
from app.models.itinerary import (
    create_itinerary,
    get_itinerary_by_trip_and_day,
    get_itinerary_by_trip,
    update_itinerary,
    delete_itinerary,
    mark_itinerary_complete,
    mark_itinerary_incomplete,
    get_trip_completion_status
)

# all urls start with /api/trips
itineraries_bp = Blueprint('itineraries', __name__, url_prefix='/api/trips')

# login check for every route below
# header: X-User-ID (int), required
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, user_id=int(user_id), **kwargs)
    return decorated_function

# GET /api/trips/<trip_id(int, required)>/itinerary, list all itinerary days for a trip.
# method: GET
# header: X-User-ID (int)
# body: none
# return list of itinerary entries (200), 404 if no trip, 500 if error
@itineraries_bp.route('/<int:trip_id>/itinerary', methods=['GET'])
@require_auth
def get_itinerary(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        itinerary_entries = get_itinerary_by_trip(trip_id)
        
        return jsonify([dict(item) for item in itinerary_entries]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST /api/trips/<trip_id(int, required)>/itinerary, add one itinerary day to a trip.
# method: POST
# header: X-User-ID (int)
# Content-Type: application/json
# body(json): day_number(int, required), title(str), description(str), activities(str/list)
# return new itinerary entry (201), 400 if no day_number, 404 if no trip,
#        409 if that day already exists, 500 if error
@itineraries_bp.route('/<int:trip_id>/itinerary', methods=['POST'])
@require_auth
def create_itinerary_entry(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        data = request.get_json()
        
        if 'day_number' not in data:
            return jsonify({'error': 'day_number is required'}), 400
        
        day_number = data.get('day_number')
        
        existing = get_itinerary_by_trip_and_day(trip_id, day_number)
        if existing:
            return jsonify({'error': f'Itinerary entry for day {day_number} already exists'}), 409
        
        create_itinerary(
            trip_id,
            day_number,
            data.get('title'),
            data.get('description'),
            data.get('activities')
        )
        
        itinerary_entry = get_itinerary_by_trip_and_day(trip_id, day_number)
        
        return jsonify(dict(itinerary_entry)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>/itinerary/<day_number(int, required)>, change one itinerary day. fields not sent keep old value.
# method: PUT
# header: X-User-ID (int)
# Content-Type: application/json
# body(json, all optional): title(str), description(str), activities(str/list)
# return updated itinerary entry (200), 404 if no trip or no entry, 500 if error
@itineraries_bp.route('/<int:trip_id>/itinerary/<int:day_number>', methods=['PUT'])
@require_auth
def update_itinerary_entry(trip_id, day_number, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        itinerary_entry = get_itinerary_by_trip_and_day(trip_id, day_number)
        
        if not itinerary_entry:
            return jsonify({'error': 'Itinerary entry not found'}), 404
        
        data = request.get_json()
        
        title = data.get('title', itinerary_entry['title'])
        description = data.get('description', itinerary_entry['description'])
        activities = data.get('activities', itinerary_entry['activities'])
        
        update_itinerary(itinerary_entry['id'], title, description, activities)
        
        updated_entry = get_itinerary_by_trip_and_day(trip_id, day_number)
        
        return jsonify(dict(updated_entry)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE /api/trips/<trip_id(int, required)>/itinerary/<day_number(int, required)>, remove one itinerary day.
# method: DELETE
# header: X-User-ID (int)
# body: none
# return {"message":"Itinerary entry deleted"} (200), 404 if no trip or no entry, 500 if error
@itineraries_bp.route('/<int:trip_id>/itinerary/<int:day_number>', methods=['DELETE'])
@require_auth
def delete_itinerary_entry(trip_id, day_number, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        itinerary_entry = get_itinerary_by_trip_and_day(trip_id, day_number)
        
        if not itinerary_entry:
            return jsonify({'error': 'Itinerary entry not found'}), 404
        
        delete_itinerary(itinerary_entry['id'])
        
        return jsonify({'message': 'Itinerary entry deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>/itinerary/<day_number(int, required)>/complete, mark one itinerary day as done.
# method: PUT
# header: X-User-ID (int)
# body: none
# return {"message":"Marked complete"} (200), 404 if no trip or no entry, 500 if error
@itineraries_bp.route('/<int:trip_id>/itinerary/<int:day_number>/complete', methods=['PUT'])
@require_auth
def mark_complete(trip_id, day_number, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        itinerary = get_itinerary_by_trip_and_day(trip_id, day_number)
        if not itinerary:
            return jsonify({'error': 'Itinerary entry not found'}), 404
        
        mark_itinerary_complete(itinerary['id'])
        
        return jsonify({'message': 'Marked complete'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET /api/trips/<trip_id(int, required)>/completion-status, get how much of the trip itinerary is done.
# method: GET
# header: X-User-ID (int)
# body: none
# return completion status object (200), 404 if no trip, 500 if error
@itineraries_bp.route('/<int:trip_id>/completion-status', methods=['GET'])
@require_auth
def get_completion_status(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        status = get_trip_completion_status(trip_id)
        
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>/itinerary/<day_number(int, required)>/incomplete, mark one itinerary day as not done.
# method: PUT
# header: X-User-ID (int)
# body: none
# return {"message":"Marked incomplete"} (200), 404 if no trip or no entry, 500 if error
@itineraries_bp.route('/<int:trip_id>/itinerary/<int:day_number>/incomplete', methods=['PUT'])
@require_auth
def mark_incomplete(trip_id, day_number, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        itinerary = get_itinerary_by_trip_and_day(trip_id, day_number)
        if not itinerary:
            return jsonify({'error': 'Itinerary entry not found'}), 404
        
        mark_itinerary_incomplete(itinerary['id'])
        
        return jsonify({'message': 'Marked incomplete'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
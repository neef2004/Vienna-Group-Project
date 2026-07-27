from flask import Blueprint, request, jsonify
from functools import wraps

from app.models.trip import (
    get_trip_by_id,
    add_trip_collaborator,
    get_trip_collaborators,
    accept_trip_invitation,
    remove_trip_collaborator,
    update_collaborator_permission,
    get_user_permission_for_trip
)
from app.models.user import get_user_by_email

# all urls start with /api/trips
collaborators_bp = Blueprint('collaborators', __name__, url_prefix='/api/trips')

# login check for every route below.
# header: X-User-ID (int), required
def require_auth(f):
    @wraps(f) # keep the wrapped route's name/info intact
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            # no header means not logged in
            return jsonify({'error': 'Unauthorized'}), 401
        # convert to int and hand user_id to the route
        return f(*args, user_id=int(user_id), **kwargs)
    return decorated_function

# GET /api/trips/<trip_id(int, required)>/collaborators, list everyone shared on a trip.
# method: GET
# header: X-User-ID (int)
# body: none
# return list of collaborators (200), 404 if no trip, 500 if error
@collaborators_bp.route('/<int:trip_id>/collaborators', methods=['GET'])
@require_auth
# List every collaborator on a trip.
def get_collaborators(trip_id, user_id):
    try:
        # scoped to user_id, so it also checks access
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            # trip missing or this user can't see it
            return jsonify({'error': 'Trip not found'}), 404
        
        collaborators = get_trip_collaborators(trip_id)
        # turn each db row into a dict so it can be json'd
        return jsonify([dict(c) for c in collaborators]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# POST /api/trips/<trip_id(int, required)>/collaborators, invite a user to a trip by email. (owner only)
# method: POST
# header: X-User-ID (int)
# Content-Type: application/json
# body(json): email(str, required), permission_level(str, default "editor" -> "viewer"/"editor")
# return {"message":"Invitation sent"} (201), 400 if no email, 403 if not owner,
#        404 if that email has no user, 500 if error
@collaborators_bp.route('/<int:trip_id>/collaborators', methods=['POST'])
@require_auth
# Invite a user to a trip by email. Only the trip owner may do this.
def invite_collaborator(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        # must exist AND caller must be the owner (trip['user_id'] is the owner id)
        if not trip or trip['user_id'] != user_id:
            return jsonify({'error': 'Only trip owner can invite'}), 403
        
        data = request.get_json()
        
        if not data.get('email'):
            # email is the only required field
            return jsonify({'error': 'Email is required'}), 400
        
        # normalize email (lowercase + trim) before looking up the invitee
        collaborator = get_user_by_email(data['email'].lower().strip())
        
        if not collaborator:
            # no account exists for that email
            return jsonify({'error': 'User not found'}), 404
        
        # default new collaborators to 'editor' if no level was given
        permission_level = data.get('permission_level', 'editor')
        
        add_trip_collaborator(trip_id, collaborator['id'], permission_level)
        
        return jsonify({'message': 'Invitation sent'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>/collaborators/<collab_user_id(int, required)>, change a collaborator's permission. (owner only)
# method: PUT
# header: X-User-ID (int)
# Content-Type: application/json
# body(json): permission_level(str, required -> "viewer"/"editor")
# return {"message":"Permission updated"} (200), 400 if bad permission, 403 if not owner, 500 if error
@collaborators_bp.route('/<int:trip_id>/collaborators/<int:collab_user_id>', methods=['PUT'])
@require_auth
# Change one collaborator's permission level. Only for the trip owner.
def update_collaborator_perm(trip_id, collab_user_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        # owner-only check (same as invite)
        if not trip or trip['user_id'] != user_id:
            return jsonify({'error': 'Only trip owner can update permissions'}), 403
        
        data = request.get_json()
        
        new_permission = data.get('permission_level')
        
        # only these two levels are allowed; reject anything else
        if new_permission not in ['viewer', 'editor']:
            return jsonify({'error': 'Invalid permission level'}), 400
        
        update_collaborator_permission(trip_id, collab_user_id, new_permission)
        
        return jsonify({'message': 'Permission updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# DELETE /api/trips/<trip_id(int, required)>/collaborators/<collab_user_id(int, required)>, remove a collaborator from a trip. (owner only)
# method: DELETE
# header: X-User-ID (int)
# body: none
# return {"message":"Collaborator removed"} (200), 403 if not owner, 500 if error
@collaborators_bp.route('/<int:trip_id>/collaborators/<int:collab_user_id>', methods=['DELETE'])
@require_auth
# Remove a collaborator from a trip. Only the trip owner may do this.
def remove_collaborator(trip_id, collab_user_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        # owner-only check
        if not trip or trip['user_id'] != user_id:
            return jsonify({'error': 'Only trip owner can remove collaborators'}), 403
        
        remove_trip_collaborator(trip_id, collab_user_id)
        
        return jsonify({'message': 'Collaborator removed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PUT /api/trips/<trip_id(int, required)>/accept-invitation, the invited user accepts their invite. (called by the invitee)
# method: PUT
# header: X-User-ID (int)
# body: none
# return {"message":"Invitation accepted"} (200), 404 if no invitation for this user, 500 if error
@collaborators_bp.route('/<int:trip_id>/accept-invitation', methods=['PUT'])
@require_auth
# The invited user accepts their own pending invitation (caller is the invitee, not the owner).
def accept_invitation(trip_id, user_id):
    try:
        # is there a permission row (invitation) for this user on this trip?
        perm = get_user_permission_for_trip(trip_id, user_id)
        
        if not perm:
            # no invitation exists for this user
            return jsonify({'error': 'No invitation found'}), 404
        
        accept_trip_invitation(trip_id, user_id)
        
        return jsonify({'message': 'Invitation accepted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
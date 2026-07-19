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

collaborators_bp = Blueprint('collaborators', __name__, url_prefix='/api/trips')


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, user_id=int(user_id), **kwargs)
    return decorated_function


@collaborators_bp.route('/<int:trip_id>/collaborators', methods=['GET'])
@require_auth
def get_collaborators(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        collaborators = get_trip_collaborators(trip_id)
        
        return jsonify([dict(c) for c in collaborators]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaborators_bp.route('/<int:trip_id>/collaborators', methods=['POST'])
@require_auth
def invite_collaborator(trip_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip or trip['user_id'] != user_id:
            return jsonify({'error': 'Only trip owner can invite'}), 403
        
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        collaborator = get_user_by_email(data['email'].lower().strip())
        
        if not collaborator:
            return jsonify({'error': 'User not found'}), 404
        
        permission_level = data.get('permission_level', 'editor')
        
        add_trip_collaborator(trip_id, collaborator['id'], permission_level)
        
        return jsonify({'message': 'Invitation sent'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaborators_bp.route('/<int:trip_id>/collaborators/<int:collab_user_id>', methods=['PUT'])
@require_auth
def update_collaborator_perm(trip_id, collab_user_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip or trip['user_id'] != user_id:
            return jsonify({'error': 'Only trip owner can update permissions'}), 403
        
        data = request.get_json()
        
        new_permission = data.get('permission_level')
        
        if new_permission not in ['viewer', 'editor']:
            return jsonify({'error': 'Invalid permission level'}), 400
        
        update_collaborator_permission(trip_id, collab_user_id, new_permission)
        
        return jsonify({'message': 'Permission updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaborators_bp.route('/<int:trip_id>/collaborators/<int:collab_user_id>', methods=['DELETE'])
@require_auth
def remove_collaborator(trip_id, collab_user_id, user_id):
    try:
        trip = get_trip_by_id(trip_id, user_id)
        
        if not trip or trip['user_id'] != user_id:
            return jsonify({'error': 'Only trip owner can remove collaborators'}), 403
        
        remove_trip_collaborator(trip_id, collab_user_id)
        
        return jsonify({'message': 'Collaborator removed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaborators_bp.route('/<int:trip_id>/accept-invitation', methods=['PUT'])
@require_auth
def accept_invitation(trip_id, user_id):
    try:
        perm = get_user_permission_for_trip(trip_id, user_id)
        
        if not perm:
            return jsonify({'error': 'No invitation found'}), 404
        
        accept_trip_invitation(trip_id, user_id)
        
        return jsonify({'message': 'Invitation accepted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
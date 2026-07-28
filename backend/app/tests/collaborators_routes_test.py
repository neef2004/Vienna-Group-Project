# tests/collaborators_routes_test.py
import pytest


# helper: creates a trip owned by given user (via their auth headers), returns its id
def make_trip(client, headers):
    response = client.post("/api/trips", json={
        "name": "Test Trip",
        "start_date": "2026-06-01T00:00:00",
        "end_date": "2026-06-10T00:00:00",
    }, headers=headers)
    return response.get_json()["id"]

# helper: creates a user via signup+login, returns (email, auth_headers) so we can
# invite them by email AND act as them later (e.g. accepting an invitation)
def make_user(client, email="collaborator@example.com", password="SecurePass123!"):
    client.post("/api/signup", json={
        "email": email,
        "password": password,
        "confirm_password": password,
    })
    login_response = client.post("/api/login", json={
        "email": email,
        "password": password,
    })
    token = login_response.get_json()["token"]
    return email, {"Authorization": f"Bearer {token}"}


# ---------- auth / access control ----------

# no Authorization header should return 401
def test_get_collaborators_no_auth_header(client):
    response = client.get("/api/trips/1/collaborators")
    assert response.status_code == 401

# a garbage token should return 422, not crash with a 500
def test_get_collaborators_invalid_auth_header(client):
    response = client.get("/api/trips/1/collaborators", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 422


# ---------- GET /api/trips/<id>/collaborators ----------

# a trip with no collaborators should return an empty list
def test_get_collaborators_empty(client, auth_headers):
    trip_id = make_trip(client, auth_headers)

    response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == []

# a trip that doesn't exist/belong to this user should return 404
def test_get_collaborators_trip_not_found(client, auth_headers):
    response = client.get("/api/trips/9999/collaborators", headers=auth_headers)
    assert response.status_code == 404


# ---------- POST /api/trips/<id>/collaborators ----------

# the trip owner should be able to invite an existing user by email
def test_invite_collaborator_success(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")

    response = client.post(f"/api/trips/{trip_id}/collaborators", json={
        "email": email,
    }, headers=auth_headers)

    assert response.status_code == 201
    assert response.get_json()["message"] == "Invitation sent"

    # confirm the collaborator now shows up in the list
    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    collaborators = get_response.get_json()
    assert len(collaborators) == 1
    assert collaborators[0]["permission_level"] == "editor"  # default

# a custom permission_level should be respected
def test_invite_collaborator_custom_permission(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="alice@example.com")

    response = client.post(f"/api/trips/{trip_id}/collaborators", json={
        "email": email,
        "permission_level": "viewer",
    }, headers=auth_headers)

    assert response.status_code == 201

    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    assert get_response.get_json()[0]["permission_level"] == "viewer"

# a non-owner trying to invite someone should get 403
def test_invite_collaborator_not_owner(client, auth_headers, auth_headers_2):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")

    response = client.post(f"/api/trips/{trip_id}/collaborators", json={
        "email": email,
    }, headers=auth_headers_2)  # this user doesn't own the trip

    assert response.status_code == 403

# missing email should return 400
def test_invite_collaborator_missing_email(client, auth_headers):
    trip_id = make_trip(client, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/collaborators", json={}, headers=auth_headers)

    assert response.status_code == 400

# inviting an email with no matching account should return 404
def test_invite_collaborator_user_not_found(client, auth_headers):
    trip_id = make_trip(client, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/collaborators", json={
        "email": "ghost@example.com",
    }, headers=auth_headers)

    assert response.status_code == 404

# a non-dict JSON body should return 400, not crash with a 500
def test_invite_collaborator_non_dict_json_body(client, auth_headers):
    trip_id = make_trip(client, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/collaborators", json=["not", "a", "dict"],
                            headers=auth_headers)

    assert response.status_code == 400

# missing JSON body entirely should return 400
def test_invite_collaborator_missing_json_body(client, auth_headers):
    trip_id = make_trip(client, auth_headers)

    response = client.post(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)

    assert response.status_code == 400

# inviting the SAME user twice should return 409, not a raw 500 —
# this is the exact fix we made for the UNIQUE(trip_id, user_id) constraint
def test_invite_collaborator_duplicate_returns_409(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")

    first_response = client.post(f"/api/trips/{trip_id}/collaborators", json={
        "email": email,
    }, headers=auth_headers)
    assert first_response.status_code == 201

    second_response = client.post(f"/api/trips/{trip_id}/collaborators", json={
        "email": email,
    }, headers=auth_headers)

    assert second_response.status_code == 409

# inviting on a trip that doesn't exist should return 403 (owner check fails first)
def test_invite_collaborator_trip_not_found(client, auth_headers):
    response = client.post("/api/trips/9999/collaborators", json={
        "email": "bob@example.com",
    }, headers=auth_headers)

    assert response.status_code == 403


# ---------- PUT /api/trips/<id>/collaborators/<collab_user_id> ----------

# the owner should be able to update a collaborator's permission level
def test_update_collaborator_permission_success(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")
    client.post(f"/api/trips/{trip_id}/collaborators", json={"email": email}, headers=auth_headers)

    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    collab_user_id = get_response.get_json()[0]["user_id"]

    response = client.put(f"/api/trips/{trip_id}/collaborators/{collab_user_id}", json={
        "permission_level": "viewer",
    }, headers=auth_headers)

    assert response.status_code == 200

    updated = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers).get_json()
    assert updated[0]["permission_level"] == "viewer"

# an invalid permission_level should return 400
def test_update_collaborator_permission_invalid_value(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")
    client.post(f"/api/trips/{trip_id}/collaborators", json={"email": email}, headers=auth_headers)

    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    collab_user_id = get_response.get_json()[0]["user_id"]

    response = client.put(f"/api/trips/{trip_id}/collaborators/{collab_user_id}", json={
        "permission_level": "admin",  # not a valid level
    }, headers=auth_headers)

    assert response.status_code == 400

# a non-owner trying to update permissions should get 403
def test_update_collaborator_permission_not_owner(client, auth_headers, auth_headers_2):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")
    client.post(f"/api/trips/{trip_id}/collaborators", json={"email": email}, headers=auth_headers)

    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    collab_user_id = get_response.get_json()[0]["user_id"]

    response = client.put(f"/api/trips/{trip_id}/collaborators/{collab_user_id}", json={
        "permission_level": "viewer",
    }, headers=auth_headers_2)  # this user doesn't own the trip

    assert response.status_code == 403

# a non-dict JSON body should return 400
def test_update_collaborator_permission_non_dict_json_body(client, auth_headers):
    trip_id = make_trip(client, auth_headers)

    response = client.put(f"/api/trips/{trip_id}/collaborators/2", json=["not", "a", "dict"],
                           headers=auth_headers)

    assert response.status_code == 400


# ---------- DELETE /api/trips/<id>/collaborators/<collab_user_id> ----------

# the owner should be able to remove a collaborator
def test_remove_collaborator_success(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")
    client.post(f"/api/trips/{trip_id}/collaborators", json={"email": email}, headers=auth_headers)

    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    collab_user_id = get_response.get_json()[0]["user_id"]

    response = client.delete(f"/api/trips/{trip_id}/collaborators/{collab_user_id}", headers=auth_headers)

    assert response.status_code == 200

    updated = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers).get_json()
    assert updated == []

# a non-owner trying to remove a collaborator should get 403
def test_remove_collaborator_not_owner(client, auth_headers, auth_headers_2):
    trip_id = make_trip(client, auth_headers)
    email, _ = make_user(client, email="bob@example.com")
    client.post(f"/api/trips/{trip_id}/collaborators", json={"email": email}, headers=auth_headers)

    get_response = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers)
    collab_user_id = get_response.get_json()[0]["user_id"]

    response = client.delete(f"/api/trips/{trip_id}/collaborators/{collab_user_id}", headers=auth_headers_2)

    assert response.status_code == 403


# ---------- PUT /api/trips/<id>/accept-invitation ----------

# a user with a pending invitation should be able to accept it —
# note this uses the COLLABORATOR's own token, not the owner's
def test_accept_invitation_success(client, auth_headers):
    trip_id = make_trip(client, auth_headers)
    email, collaborator_headers = make_user(client, email="bob@example.com")
    client.post(f"/api/trips/{trip_id}/collaborators", json={"email": email}, headers=auth_headers)

    response = client.put(f"/api/trips/{trip_id}/accept-invitation", headers=collaborator_headers)

    assert response.status_code == 200
    assert response.get_json()["message"] == "Invitation accepted"

    updated = client.get(f"/api/trips/{trip_id}/collaborators", headers=auth_headers).get_json()
    assert updated[0]["accepted"] == 1

# a user with no invitation should get 404
def test_accept_invitation_no_invitation_found(client, auth_headers, auth_headers_2):
    trip_id = make_trip(client, auth_headers)

    response = client.put(f"/api/trips/{trip_id}/accept-invitation", headers=auth_headers_2)

    assert response.status_code == 404
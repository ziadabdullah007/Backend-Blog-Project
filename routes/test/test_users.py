"""Tests for user management: roles, access control"""

def test_get_all_users_as_admin(client, admin_token):
    res = client.get("/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_all_users_as_reader_forbidden(client, reader_token):
    res = client.get("/users/", headers={"Authorization": f"Bearer {reader_token}"})
    assert res.status_code == 403

def test_get_all_users_unauthenticated(client):
    res = client.get("/users/")
    assert res.status_code == 401

def test_get_user_by_id_as_admin(client, admin_token):
    # create a user to fetch
    res = client.post("/users/", json={"username": "fetch_me", "email": "fm@test.com", "password": "pass", "role": "reader"})
    user_id = res.json()["id"]
    res = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

def test_update_own_user(client, reader_token):
    me = client.get("/users/me", headers={"Authorization": f"Bearer {reader_token}"}).json()
    res = client.put(f"/users/{me['id']}", json={"username": "updated_reader"},
                     headers={"Authorization": f"Bearer {reader_token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "updated_reader"

def test_update_other_user_forbidden(client, reader_token, author_token):
    author_me = client.get("/users/me", headers={"Authorization": f"Bearer {author_token}"}).json()
    res = client.put(f"/users/{author_me['id']}", json={"username": "stolen"},
                     headers={"Authorization": f"Bearer {reader_token}"})
    assert res.status_code == 403

def test_delete_user_as_admin(client, admin_token):
    res = client.post("/users/", json={"username": "todel", "email": "del@test.com", "password": "pass", "role": "reader"})
    user_id = res.json()["id"]
    res = client.delete(f"/users/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200

def test_delete_user_as_reader_forbidden(client, reader_token, author_token):
    author_me = client.get("/users/me", headers={"Authorization": f"Bearer {author_token}"}).json()
    res = client.delete(f"/users/{author_me['id']}", headers={"Authorization": f"Bearer {reader_token}"})
    assert res.status_code == 403

def test_invalid_role_registration(client):
    res = client.post("/users/", json={"username": "hacker", "email": "hack@test.com", "password": "pass", "role": "superadmin"})
    assert res.status_code == 422

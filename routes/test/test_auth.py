"""Tests for authentication: register, login, token validation"""

def test_register_success(client):
    res = client.post("/users/", json={
        "username": "testuser", "email": "test@test.com",
        "password": "pass123", "role": "reader"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "testuser"
    assert data["role"] == "reader"
    assert "password" not in data

def test_register_duplicate_username(client):
    client.post("/users/", json={"username": "dup", "email": "dup@test.com", "password": "pass", "role": "reader"})
    res = client.post("/users/", json={"username": "dup", "email": "dup2@test.com", "password": "pass", "role": "reader"})
    assert res.status_code == 400

def test_register_duplicate_email(client):
    client.post("/users/", json={"username": "u1", "email": "same@test.com", "password": "pass", "role": "reader"})
    res = client.post("/users/", json={"username": "u2", "email": "same@test.com", "password": "pass", "role": "reader"})
    assert res.status_code == 400

def test_login_success(client):
    client.post("/users/", json={"username": "loginuser", "email": "login@test.com", "password": "pass123", "role": "reader"})
    res = client.post("/users/login", data={"username": "loginuser", "password": "pass123"})
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post("/users/", json={"username": "lu", "email": "lu@test.com", "password": "correct", "role": "reader"})
    res = client.post("/users/login", data={"username": "lu", "password": "wrong"})
    assert res.status_code == 401

def test_login_nonexistent_user(client):
    res = client.post("/users/login", data={"username": "ghost", "password": "pass"})
    assert res.status_code == 401

def test_protected_route_no_token(client):
    res = client.get("/users/me")
    assert res.status_code == 401

def test_protected_route_invalid_token(client):
    res = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401

def test_get_me_with_token(client, reader_token):
    res = client.get("/users/me", headers={"Authorization": f"Bearer {reader_token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "reader1"

def test_auth_register_endpoint(client):
    res = client.post("/auth/register", json={
        "username": "authuser", "email": "auth@test.com",
        "password": "pass123", "role": "author"
    })
    assert res.status_code == 201

def test_auth_login_endpoint(client):
    client.post("/auth/register", json={"username": "au2", "email": "au2@test.com", "password": "pass", "role": "reader"})
    res = client.post("/auth/login", data={"username": "au2", "password": "pass"})
    assert res.status_code == 200
    assert "access_token" in res.json()

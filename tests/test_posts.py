def create_post(client, token, title="Post", content="Content"):
    return client.post(
        "/posts/",
        json={"title": title, "content": content},
        headers={"Authorization": f"Bearer {token}"},
    )


def test_get_posts(client):
    response = client.get("/posts/")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 10
    assert isinstance(body["data"], list)


def test_create_post_as_author(client, author_token):
    response = create_post(client, author_token, "pytest post", "pytest content")
    assert response.status_code == 201
    assert response.json()["title"] == "pytest post"
    assert response.json()["content"] == "pytest content"


def test_create_post_as_reader_forbidden(client, reader_token):
    response = create_post(client, reader_token, "reader post", "reader content")
    assert response.status_code == 403


def test_get_single_post(client, author_token):
    create_res = create_post(client, author_token, "single", "body")
    post_id = create_res.json()["id"]
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["id"] == post_id


def test_update_post_by_owner(client, author_token):
    create_res = create_post(client, author_token, "old", "old content")
    post_id = create_res.json()["id"]
    response = client.put(
        f"/posts/{post_id}",
        json={"title": "new", "content": "new content"},
        headers={"Authorization": f"Bearer {author_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "new"


def test_update_post_by_other_forbidden(client, author_token, admin_token):
    create_res = create_post(client, author_token, "owner title", "owner content")
    post_id = create_res.json()["id"]

    client.post(
        "/auth/register",
        json={"username": "author2", "email": "author2@test.com", "password": "author123", "role": "author"},
    )
    login_res = client.post("/auth/login", data={"username": "author2", "password": "author123"})
    other_author_token = login_res.json()["access_token"]

    response = client.put(
        f"/posts/{post_id}",
        json={"title": "hack"},
        headers={"Authorization": f"Bearer {other_author_token}"},
    )
    assert response.status_code == 403


def test_admin_can_update_post(client, author_token, admin_token):
    create_res = create_post(client, author_token, "admin target", "content")
    post_id = create_res.json()["id"]
    response = client.put(
        f"/posts/{post_id}",
        json={"content": "updated by admin"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "updated by admin"


def test_delete_post_by_owner(client, author_token):
    create_res = create_post(client, author_token, "delete test", "delete content")
    post_id = create_res.json()["id"]
    response = client.delete(f"/posts/{post_id}", headers={"Authorization": f"Bearer {author_token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted"


def test_delete_post_by_admin(client, author_token, admin_token):
    create_res = create_post(client, author_token, "delete admin", "content")
    post_id = create_res.json()["id"]
    response = client.delete(f"/posts/{post_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


def test_delete_post_unauthenticated(client, author_token):
    create_res = create_post(client, author_token, "delete anon", "content")
    post_id = create_res.json()["id"]
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 401

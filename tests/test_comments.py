def create_post(client, token):
    return client.post(
        "/posts/",
        json={"title": "Post", "content": "Content"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()["id"]


def create_comment(client, token, post_id, content="A comment", parent_id=None):
    body = {"content": content, "post_id": post_id}
    if parent_id is not None:
        body["parent_id"] = parent_id
    return client.post("/comments/", json=body, headers={"Authorization": f"Bearer {token}"})


def test_create_comment_authenticated(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    res = create_comment(client, reader_token, post_id)
    assert res.status_code == 201
    assert res.json()["content"] == "A comment"


def test_create_comment_unauthenticated(client, author_token):
    post_id = create_post(client, author_token)
    res = client.post("/comments/", json={"content": "x", "post_id": post_id})
    assert res.status_code == 401


def test_create_nested_comment(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    parent_id = create_comment(client, reader_token, post_id).json()["id"]
    res = create_comment(client, reader_token, post_id, content="Reply", parent_id=parent_id)
    assert res.status_code == 201
    assert res.json()["parent_id"] == parent_id


def test_create_comment_invalid_parent(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    res = create_comment(client, reader_token, post_id, parent_id=99999)
    assert res.status_code == 404


def test_create_comment_parent_from_another_post(client, reader_token, author_token):
    post_id_1 = create_post(client, author_token)
    post_id_2 = create_post(client, author_token)
    parent_id = create_comment(client, reader_token, post_id_1).json()["id"]
    res = create_comment(client, reader_token, post_id_2, parent_id=parent_id)
    assert res.status_code == 400


def test_get_all_comments(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    create_comment(client, reader_token, post_id)
    res = client.get("/comments/")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert len(body["data"]) >= 1


def test_get_comment_by_id(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    comment_id = create_comment(client, reader_token, post_id).json()["id"]
    res = client.get(f"/comments/{comment_id}")
    assert res.status_code == 200
    assert res.json()["id"] == comment_id


def test_get_comment_not_found(client):
    res = client.get("/comments/99999")
    assert res.status_code == 404


def test_get_nested_comments(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    parent_id = create_comment(client, reader_token, post_id, "Root").json()["id"]
    create_comment(client, reader_token, post_id, "Reply", parent_id)
    res = client.get(f"/comments/post/{post_id}/nested")
    assert res.status_code == 200
    roots = res.json()
    assert len(roots) == 1
    assert len(roots[0]["replies"]) == 1


def test_update_comment_by_owner(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    comment_id = create_comment(client, reader_token, post_id).json()["id"]
    res = client.put(
        f"/comments/{comment_id}",
        json={"content": "Updated"},
        headers={"Authorization": f"Bearer {reader_token}"},
    )
    assert res.status_code == 200
    assert res.json()["content"] == "Updated"


def test_update_comment_by_other_forbidden(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    comment_id = create_comment(client, reader_token, post_id).json()["id"]
    res = client.put(
        f"/comments/{comment_id}",
        json={"content": "Hack"},
        headers={"Authorization": f"Bearer {author_token}"},
    )
    assert res.status_code == 403


def test_delete_comment_by_owner(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    comment_id = create_comment(client, reader_token, post_id).json()["id"]
    res = client.delete(f"/comments/{comment_id}", headers={"Authorization": f"Bearer {reader_token}"})
    assert res.status_code == 200


def test_delete_comment_by_admin(client, reader_token, author_token, admin_token):
    post_id = create_post(client, author_token)
    comment_id = create_comment(client, reader_token, post_id).json()["id"]
    res = client.delete(f"/comments/{comment_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200


def test_delete_comment_unauthenticated(client, reader_token, author_token):
    post_id = create_post(client, author_token)
    comment_id = create_comment(client, reader_token, post_id).json()["id"]
    res = client.delete(f"/comments/{comment_id}")
    assert res.status_code == 401

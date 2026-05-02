from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_posts():
    response = client.get("/posts/")
    assert response.status_code == 200
    assert "data" in response.json()



def test_create_post():
    data = {
        "title": "pytest post",
        "content": "pytest content",
        "user_id": 1
    }

    response = client.post("/posts/", json=data)

    assert response.status_code == 200
    assert response.json()["title"] == "pytest post"
    assert response.json()["content"] == "pytest content"


def test_get_single_post():
    response = client.get("/posts/1")
    assert response.status_code in [200, 404]



def test_delete_post():
    # create post first
    data = {
        "title": "delete test",
        "content": "delete content",
        "user_id": 1
    }

    create_res = client.post("/posts/", json=data)
    post_id = create_res.json()["id"]

    
    response = client.delete(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Post deleted"
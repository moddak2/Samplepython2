from fastapi.testclient import TestClient

from app.main import app


def test_health_ok() -> None:
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_login_and_profile_authorized() -> None:
    client = TestClient(app)

    login = client.post("/login", json={"user_id": 1})
    assert login.status_code == 200
    token = login.json()["token"]

    profile = client.get("/users/1/profile", headers={"X-Demo-Token": token})
    assert profile.status_code == 200
    assert profile.json()["id"] == 1


def test_profile_idor_blocked() -> None:
    client = TestClient(app)

    login = client.post("/login", json={"user_id": 1})
    token = login.json()["token"]

    # Try accessing another user's resource
    profile = client.get("/users/2/profile", headers={"X-Demo-Token": token})
    assert profile.status_code == 403


def test_download_ok() -> None:
    client = TestClient(app)
    resp = client.get("/download/hello.txt")
    assert resp.status_code == 200
    assert resp.text.replace("\r\n", "\n") == "hello\n"


def test_download_path_traversal_blocked() -> None:
    client = TestClient(app)

    # Attempt to escape base directory
    resp = client.get("/download/../main.py")
    assert resp.status_code in (400, 404)

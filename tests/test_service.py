import pytest

def test_auth_flow(client, test_user):
    r = client.post("/api/auth/register", json=test_user)
    assert r.status_code == 201
    r = client.post("/api/auth/login", data={"username": test_user["username"], "password": test_user["password"]})
    assert r.status_code == 200 and "access_token" in r.json()

def test_password_validation(client):
    weak = ["short", "nouppercase1!", "NOLOWERCASE1!", "NoDigits!", "NoSpecial123"]
    for p in weak:
        r = client.post("/api/auth/register", json={"username": "user1", "email": "a@b.com", "password": p})
        assert r.status_code == 422 and "VALIDATION_ERROR" in r.json()["error"]["code"]

def test_full_paintings_crud(client, auth_token):
    h = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/api/paintings", json={
        "title": "Test Art", "artist_name": "Artist A", "genre_name": "Genre X",
        "image_url": "https://example.com/img.jpg", "year": 2020, "painting_type": "digital"
    }, headers=h)
    assert r.status_code == 201
    pid = r.json()["id"]
    r = client.put(f"/api/paintings/{pid}", json={"title": "Updated Art"}, headers=h)
    assert r.status_code == 200 and r.json()["title"] == "Updated Art"
    r = client.get(f"/api/paintings/search?q=Updated")
    assert r.status_code == 200 and len(r.json()) >= 1
    r = client.delete(f"/api/paintings/{pid}", headers=h)
    assert r.status_code == 204

def test_favorites_duplication(client, auth_token):
    h = {"Authorization": f"Bearer {auth_token}"}
    client.post("/api/favorites/artists", json={"artist_name": "Van Gogh"}, headers=h)
    r = client.post("/api/favorites/artists", json={"artist_name": "Van Gogh"}, headers=h)
    assert r.status_code == 400 and "already in favorites" in r.json()["error"]["message"]

def test_recommendations_and_explain(client, auth_token):
    h = {"Authorization": f"Bearer {auth_token}"}
    client.post("/api/favorites/artists", json={"artist_name": "Van Gogh"}, headers=h)
    client.post("/api/favorites/genres", json={"genre_name": "Post-Imp"}, headers=h)
    client.post("/api/paintings", json={
        "title": "Starry", "artist_name": "Van Gogh", "genre_name": "Post-Imp",
        "image_url": "https://x.com/1.jpg", "year": 1889, "painting_type": "oil", "description": "Test"
    }, headers=h)
    r = client.post("/api/recommendations", json={"criteria": "by_both"}, headers=h)
    assert r.status_code == 200 and r.json()["total_count"] >= 1
    pid = r.json()["paintings"][0]["id"]
    r = client.post(f"/api/recommendations/explain/{pid}", headers=h)
    assert r.status_code == 200 and r.json()["total_score"] > 0

def test_analytics_and_export(client):
    r = client.get("/api/analytics/gallery")
    assert r.status_code == 200 and "total_paintings" in r.json()
    r = client.get("/api/export/paintings/csv")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
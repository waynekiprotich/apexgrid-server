import json
from app.models.user import User
from app.services.auth_service import hash_password
from app.extensions import db

def test_register(client, app):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "username": "testuser"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["data"]["email"] == "test@example.com"
    
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None

def test_login(client, app):
    with app.app_context():
        user = User(
            email="login@example.com",
            password_hash=hash_password("password123"),
            username="loginuser"
        )
        db.session.add(user)
        db.session.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data["data"]

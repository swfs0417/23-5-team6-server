from fastapi.testclient import TestClient
from pydantic_settings import SettingsConfigDict
import pytest
from datetime import datetime, timedelta
from asset_management.app.auth.settings import AuthSettings
from tests.conftest import SETTINGS
from authlib.jose import jwt, JWTClaims

class TestAuthSettings(AuthSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=SETTINGS.env_file,
        extra='ignore'
    )

AUTH_SETTINGS = TestAuthSettings()

@pytest.fixture(scope="function")
def user_data(client, db_session):
  """Create a test user and return an authentication token"""
  test_user_data = {
    "name": "testuser",
    "email": "testuser@example.com",
    "password": "testpassword",
  }

  response = client.post("/api/users/signup", json=test_user_data)
  assert response.status_code == 201
  data = response.json()

  return data

def issue_token(user_id: int) -> str:
  header = {"alg": "HS256"}
  payload_acc = {
    "sub": user_id,
    "type": "access",
    "exp": datetime.now()
    + timedelta(minutes=AUTH_SETTINGS.SHORT_SESSION_LIFESPAN),
  }
  payload_ref = {
    "sub": user_id,
    "type": "refresh",
    "exp": datetime.now()
    + timedelta(minutes=AUTH_SETTINGS.LONG_SESSION_LIFESPAN),
  }
  access_token = jwt.encode(header, payload_acc, AUTH_SETTINGS.ACCESS_TOKEN_SECRET)
  refresh_token = jwt.encode(header, payload_ref, AUTH_SETTINGS.REFRESH_TOKEN_SECRET)

  return {"access_token": access_token, "refresh_token": refresh_token}

@pytest.fixture(scope="function")
def auth_token(user_data):
  """Provide an authentication token for the test user"""
  user_id = user_data["id"]
  tokens = issue_token(user_id)
  return tokens

def test_get_token(client: TestClient, auth_token, user_data):
  tokens = client.post(
    "/api/auth/login",
    data={"email": user_data["email"], "password": user_data["password"]})
  assert tokens.status_code == 200
  tokens = tokens.json()
  
  assert "access_token" in tokens
  assert "refresh_token" in tokens
  access_token = jwt.decode(tokens["access_token"], AUTH_SETTINGS.ACCESS_TOKEN_SECRET)
  refresh_token = jwt.decode(tokens["refresh_token"], AUTH_SETTINGS.REFRESH_TOKEN_SECRET)
  assert "sub" in access_token
  assert "sub" in refresh_token
  assert access_token["sub"] == user_data["id"]
  assert access_token["type"] == "access"
  assert access_token["exp"] < datetime.now().timestamp()
  assert refresh_token["sub"] == user_data["id"]
  assert refresh_token["type"] == "refresh"
  assert refresh_token["exp"] < datetime.now().timestamp()

def test_expired_token(client: TestClient, user_data):
  header = {"alg": "HS256"}
  payload_acc = {
    "sub": user_data["id"],
    "type": "refresh",
    "exp": datetime.now() - timedelta(minutes=1),
  }
  access_token = jwt.encode(header, payload_acc, AUTH_SETTINGS.ACCESS_TOKEN_SECRET)

  response = client.get(
    "/api/auth/refresh",
    headers={"Authorization": f"Bearer {access_token}"}
  )
  assert response.status_code == 401

def test_refresh_token(client: TestClient, user_data, auth_token):
  response = client.get(
    "/api/auth/refresh",
    headers={"Authorization": f"Bearer {auth_token['refresh_token']}"}
  )
  assert response.status_code == 200
  tokens = response.json()
  
  assert "access_token" in tokens
  assert "refresh_token" in tokens
  access_token = jwt.decode(tokens["access_token"], AUTH_SETTINGS.ACCESS_TOKEN_SECRET)
  refresh_token = jwt.decode(tokens["refresh_token"], AUTH_SETTINGS.REFRESH_TOKEN_SECRET)
  assert "sub" in access_token
  assert "sub" in refresh_token
  assert access_token["sub"] == user_data["id"]
  assert access_token["type"] == "access"
  assert access_token["exp"] < datetime.now().timestamp()
  assert refresh_token["sub"] == user_data["id"]
  assert refresh_token["type"] == "refresh"
  assert refresh_token["exp"] < datetime.now().timestamp()

def test_logout(client: TestClient, auth_token):
  access_token = auth_token["refresh_token"]

  response = client.post(
    "/api/auth/logout",
    headers={"Authorization": f"Bearer {access_token}"})
  assert response.status_code == 204
  
  response = client.get(
    "/api/auth/refresh",
    headers={"Authorization": f"Bearer {access_token}"})
  assert response.status_code == 401
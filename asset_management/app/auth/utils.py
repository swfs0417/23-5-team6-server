from asset_management.app.auth.settings import AUTH_SETTINGS
from datetime import datetime, timedelta
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from fastapi import Depends, Header, HTTPException, status
from typing import Annotated
import hashlib


def issue_token(user_id: int) -> str:
  header = {"alg": "HS256"}
  payload_acc = {
    "sub": user_id,
    "type": "access",
    "exp": datetime.now() + timedelta(minutes=AUTH_SETTINGS.SHORT_SESSION_LIFESPAN),
  }
  payload_ref = {
    "sub": user_id,
    "type": "refresh",
    "exp": datetime.now() + timedelta(minutes=AUTH_SETTINGS.LONG_SESSION_LIFESPAN),
  }
  access_token = jwt.encode(header, payload_acc, AUTH_SETTINGS.ACCESS_TOKEN_SECRET)
  refresh_token = jwt.encode(header, payload_ref, AUTH_SETTINGS.REFRESH_TOKEN_SECRET)
  
  # Convert bytes to string if necessary
  if isinstance(access_token, bytes):
    access_token = access_token.decode('utf-8')
  if isinstance(refresh_token, bytes):
    refresh_token = refresh_token.decode('utf-8')

  return {"access_token": access_token, "refresh_token": refresh_token}

def get_header_token(authorization: Annotated[str | None, Header()] = None) -> str:
  if not authorization or not authorization.startswith("Bearer "):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid authorization header",
      headers={"WWW-Authenticate": "Bearer"},
    )
  return authorization.split(" ")[1]

def login_with_header(token: Annotated[str | None, Depends(get_header_token)] = None):
  return verify_token(token, AUTH_SETTINGS.ACCESS_TOKEN_SECRET, "access")

def verify_token(token: str, secret: str, expected_type: str) -> str:
  try:
    claims = jwt.decode(token, secret)
    claims.validate_exp(now=datetime.now().timestamp(), leeway=0)
    if claims.get("type") != expected_type:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token type",
        headers={"WWW-Authenticate": "Bearer"},
      )
    return claims.get("sub")
  except JoseError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )

def refresh_token(token: Annotated[str | None, Depends(get_header_token)] = None):
  return verify_token(token, AUTH_SETTINGS.REFRESH_TOKEN_SECRET, "refresh")

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password

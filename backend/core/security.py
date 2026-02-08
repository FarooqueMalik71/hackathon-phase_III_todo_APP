from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token with the provided data and expiration time
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 1 hour if no expiration is provided
        expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and return the payload if valid
    """
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])

        # Check if token is expired (this is handled by jwt.decode automatically)
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None:
            return None

        return {
            "user_id": user_id,
            "email": email,
            "exp": payload.get("exp")
        }
    except JWTError:
        # Token is invalid
        return None


def decode_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for debugging purposes)
    """
    try:
        # This does not verify the signature, just decodes the payload
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError:
        return None


def is_token_expired(payload: Dict[str, Any]) -> bool:
    """
    Check if a token is expired based on its payload
    """
    exp = payload.get("exp")
    if exp is None:
        return True

    return datetime.fromtimestamp(exp) < datetime.utcnow()


def verify_and_extract_user_data(token: str) -> Optional[Dict[str, str]]:
    """
    Verify the token and extract user data (user_id and email)
    """
    payload = verify_token(token)
    if payload is None:
        return None

    # Check if token is expired
    if is_token_expired(payload):
        return None

    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email")
    }
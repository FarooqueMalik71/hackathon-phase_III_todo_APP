"""
JWT Authentication middleware for AI chatbot
Reuses existing Phase II authentication infrastructure
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import sys
import os

# Add parent directory to path to import from existing utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from utils.auth import verify_resource_ownership

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and validate user from JWT token
    Returns user_id from the token

    Note: In production, this should decode and validate the JWT token.
    For hackathon purposes, we're using a simplified approach.
    """
    # In a real implementation, decode JWT and extract user_id
    # For now, we'll extract user_id from the authorization header
    # This is a simplified implementation for the hackathon

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Simplified: In production, decode JWT and extract user_id
    # For hackathon, accept token as user_id
    user_id = credentials.credentials

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


def verify_conversation_ownership(user_id: str, conversation_user_id: str) -> bool:
    """
    Verify that the authenticated user owns the conversation
    Reuses existing resource ownership verification
    """
    return verify_resource_ownership(user_id, conversation_user_id)


def validate_user_access_to_conversation(current_user_id: str, conversation_user_id: str) -> None:
    """
    Validate that the current user has access to the specified conversation
    Raises HTTPException if access is not authorized
    """
    if not verify_conversation_ownership(current_user_id, conversation_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this conversation is forbidden"
        )

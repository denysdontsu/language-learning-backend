from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from jose import ExpiredSignatureError, JWTError, jwt

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.schemas.jwt_token import JWTPayload

# Password hashing context
# Project parameters (lower for development speed)
password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1,
    hash_len=32,
    salt_len=16
)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using Argon2id.

    Args:
        password: Plain text password

    Returns:
        Hashed password string (Argon2id format)
    """
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against an Argon2 hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Argon2 hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        password_hasher.verify(hashed_password, plain_password)
        return True

    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(data: dict[str, Any],
                        expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload to encode (must contain "user_id", optionally "role")
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Raises:
        ValueError: If required fields are missing or invalid

    """
    if 'user_id' not in data:
        raise ValueError("'user_id' is required on token data")

    if not isinstance(data['user_id'], int):
        raise ValueError("'user_id' must be an integer")

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        'sub': str(data['user_id']),
        'role': data.get('role', 'user'),
        'iat': int(now.timestamp()),
        'exp': int(expire.timestamp())
    }
    encoded_jwt = jwt.encode(payload,
                      key=settings.SECRET_KEY,
                      algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> JWTPayload:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Validated JWTPayload with sub, role, iat, exp

    Raises:
        HTTPException: If token is invalid, expired, or validation fails
    """
    try:
        payload = jwt.decode(token,
                          key=settings.SECRET_KEY,
                          algorithms=[settings.JWT_ALGORITHM])

        # Validate payload fields with Pydantic
        payload = JWTPayload(**payload)
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"})

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"})

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token payload {e}",
            headers={"WWW-Authenticate": "Bearer"})
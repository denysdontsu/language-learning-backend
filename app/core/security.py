from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

# Password hashing context
password_hasher = PasswordHasher()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

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

    except VerifyMismatchError:
        return False

    except InvalidHashError:
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

    to_encode = data.copy()

    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        'sub': str(data['user_id']),
        'role': data.get('role', 'user'),
        'iat': now,
        'exp': expire
    })
    encoded_jwt = jwt.encode(to_encode,
                      key=settings.SECRET_KEY,
                      algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict containing sub, role, iat, exp

    Raises:
        JWTError: If token is invalid, expired, or signature verification fails
    """
    try:
        payload = jwt.decode(token,
                          key=settings.SECRET_KEY,
                          algorithms=[settings.JWT_ALGORITHM])
        if 'user_id' not in payload:
            raise JWTError("'Token missing 'user_id'' claim")

        return payload

    except JWTError:
        raise JWTError(f'Invalid or expired token')
    except Exception as e:
        raise Exception(f'Token validation failed: {e}')
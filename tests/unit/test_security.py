from contextlib import nullcontext as does_not_raise
from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.security import verify_password, create_access_token, hash_password, decode_access_token
from app.schemas import UserRoleEnum, JWTPayload


@pytest.mark.parametrize(
    'password_to_hash, password_to_verify, expected',
    [
        ('same_password', 'same_password', True),
        ('same_password', 'diff_password1', False),
    ],
    ids=[
        'matching_passwords_returns_true',
        'different_passwords_returns_false',
    ]
)
def test_hash_and_verify_password(password_to_hash, password_to_verify, expected):
    hashed_password = hash_password(password_to_hash)

    result = verify_password(password_to_verify, hashed_password)

    assert result == expected


@pytest.mark.parametrize(
    "data, expires_delta, expected, expectation",
    [
        ({'user_id': 1, 'role': UserRoleEnum.USER.value}, None, 'jwt', does_not_raise()),
        ({'user_id': 1, 'role': UserRoleEnum.ADMIN.value}, timedelta(days=7), 'jwt', does_not_raise()),
        (
            {'user_id': "not_an_integer", 'role': UserRoleEnum.USER.value},
            timedelta(days=7),
            None,
            pytest.raises(ValueError, match="'user_id' must be an integer"),
        ),
        (
            {'role': UserRoleEnum.USER.value},
            timedelta(days=7),
            None,
            pytest.raises(ValueError, match="'user_id' is required on token data"),
        ),
    ],
    ids=[
        'data_without_expires_delta_return_token',
        'data_with_expires_delta_return_token',
        'data_with_str_user_id_return_error',
        'data_without_user_id_return_error'
    ]
)
def test_create_access_token(data, expires_delta, expected, expectation):
    with expectation:
        result = create_access_token(data, expires_delta)
        if expected:
            assert isinstance(result, str)


@pytest.mark.parametrize(
    'data, expires_delta, expected, exception',
    [
        ({'user_id': 1, 'role': UserRoleEnum.USER.value}, timedelta(days=7), 'payload', does_not_raise()),
        (
            {'user_id': 1, 'role': UserRoleEnum.USER.value},
            timedelta(days=-7),
            None,
            pytest.raises(HTTPException, match='Token has expired')
        ),
        (
            {'user_id': -999, 'role': UserRoleEnum.USER.value},
            timedelta(days=7),
            None,
            pytest.raises(HTTPException, match='Invalid token payload')
        ),
    ],
    ids=[
        'data_with_expires_delta_return_payload',
        'negative_expires_delta_return_error',
        'negative_user_id_return_error'
    ]
)
def test_decode_access_token(data, expires_delta, expected, exception):
    with exception:
        token = create_access_token(data, expires_delta)
        payload = decode_access_token(token)
        if expected:
            assert isinstance(payload, JWTPayload)
            assert payload.sub == str(data['user_id'])
            assert payload.role == data['role']
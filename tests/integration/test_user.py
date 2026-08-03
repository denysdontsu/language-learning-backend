from app.api.dependencies import limiter
from app.core.security import create_access_token
from app.schemas import UserRoleEnum, UserUpdate, UserChangePassword
from tests.integration.conftest import get_auth_headers


class TestGetCurrentUser:
    async def test_get_user_without_language_return_user(
            self,
            client,
            test_user,
            get_auth_headers,
    ):
        headers = get_auth_headers(test_user)
        response = await client.get(url='/users/me/', headers=headers)
        assert response.status_code == 200

        response_dict = response.json()
        assert response_dict['email'] == test_user.email
        assert response_dict['username'] == test_user.username
        assert 'active_learning_language' not in response_dict

    async def test_get_user_with_language_return_user_with_language(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.get(url='/users/me/', headers=headers)
        assert response.status_code == 200

        response_dict = response.json()

        assert 'active_learning_language' in response_dict
        assert (response_dict['active_learning_language']['language']
                == test_user_learning_language.language)
        assert (response_dict['active_learning_language']['level']
                == test_user_learning_language.level)

    async def test_get_unknown_user_return_401(
            self,
            client,
            get_auth_headers
    ):
        token = create_access_token({'user_id': 999, 'role': UserRoleEnum.USER.value})
        headers = {'Authorization': f'Bearer {token}'}
        response = await client.get(url='/users/me/', headers=headers)
        assert response.status_code == 401

        assert response.json()['detail'] == 'User not found'

    async def test_get_user_unauthorized_raises_401(
            self,
            client
    ):
        response = await client.get(
            url='/users/me/'
        )
        assert response.status_code == 401

    async def test_get_deactivated_user_return_403(
            self,
            client,
            get_auth_headers,
            test_deactivate_user
    ):
        headers = get_auth_headers(test_deactivate_user)
        response = await client.get(url='/users/me/', headers=headers)
        assert response.status_code == 403
        assert response.json()['detail'] == 'Inactive user'


class TestUpdateUserProfile:

    async def test_update_user_no_changes(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        data = UserUpdate().model_dump(exclude_unset=True)
        response = await client.patch(
            url='/users/me/',
            headers=headers,
            json=data
        )
        assert response.status_code == 200

        response_dict = response.json()
        assert test_user.email == response_dict['email']
        assert test_user.name == response_dict['name']
        assert test_user.username == response_dict['username']
        assert test_user.native_language == response_dict['native_language']

    async def test_update_user_same_credentials_success(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        data = UserUpdate(
            email=test_user.email,
            username=test_user.username
        ).model_dump(exclude_unset=True)

        response = await client.patch(
            url='/users/me/',
            headers=headers,
            json=data
        )
        assert response.status_code == 200

        response_dict = response.json()
        assert test_user.email == response_dict['email']
        assert test_user.username == response_dict['username']

    async def test_update_user_duplicate_email_raises_409(
            self,
            client,
            test_user,
            get_auth_headers,
            test_other_user
    ):
        headers = get_auth_headers(test_user)
        data = UserUpdate(
            email=test_other_user.email
        ).model_dump(exclude_unset=True)

        response = await client.patch(
            url='/users/me/',
            headers=headers,
            json=data
        )
        assert response.status_code == 409
        assert response.json()['detail'] == 'Email already registered'

    async def test_update_user_duplicate_username_raises_409(
            self,
            client,
            test_user,
            get_auth_headers,
            test_other_user
    ):
        headers = get_auth_headers(test_user)
        data = UserUpdate(
            username=test_other_user.username
        ).model_dump(exclude_unset=True)

        response = await client.patch(
            url='/users/me/',
            headers=headers,
            json=data
        )
        assert response.status_code == 409
        assert response.json()['detail'] == 'Username already taken'

    async def test_update_user_unauthorized_raises_401(
            self,
            client
    ):
        response = await client.patch(
            url='/users/me/',
            json={}
        )
        assert response.status_code == 401

    async def test_update_user_deactivated_user_return_403(
            self,
            client,
            get_auth_headers,
            test_deactivate_user
    ):
        headers = get_auth_headers(test_deactivate_user)
        response = await client.patch(url='/users/me/', headers=headers)
        assert response.status_code == 403

        assert response.json()['detail'] == 'Inactive user'


class TestChangePassword:

    async def test_change_password_success(
            self,
            client,
            test_user,
            get_auth_headers,
            user_data
    ):
        headers = get_auth_headers(test_user)
        data = UserChangePassword(
            old_password=user_data['password'],
            new_password='newpass1'
        ).model_dump()

        response = await client.patch(
            url='/users/me/password',
            headers=headers,
            json=data
        )
        assert response.status_code == 204

    async def test_change_password_wrong_old_password_raises_400(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        data = UserChangePassword(
            old_password='wrongpass1',
            new_password='newpass1'
        ).model_dump()

        response = await client.patch(
            url='/users/me/password',
            headers=headers,
            json=data
        )
        assert response.status_code == 400
        assert response.json()['detail'] == 'Incorrect old password'

    async def test_change_password_same_as_old_raises_400(
            self,
            client,
            test_user,
            get_auth_headers,
            user_data
    ):
        headers = get_auth_headers(test_user)
        data = UserChangePassword(
            old_password=user_data['password'],
            new_password=user_data['password']
        ).model_dump()

        response = await client.patch(
            url='/users/me/password',
            headers=headers,
            json=data
        )
        assert response.status_code == 400
        assert response.json()['detail'] == 'New password must be different from old password'

    async def test_change_password_weak_new_password_raises_422(
            self,
            client,
            test_user,
            get_auth_headers,
            user_data
    ):
        headers = get_auth_headers(test_user)
        data = {
            'old_password': user_data['password'],
            'new_password': 'onlyletters'
        }

        response = await client.patch(
            url='/users/me/password',
            headers=headers,
            json=data
        )
        assert response.status_code == 422

    async def test_change_password_rate_limit_exceeded_raises_429(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        limiter.reset()

        headers = get_auth_headers(test_user)
        data = UserChangePassword(
            old_password='wrongpass1',
            new_password='newpass1'
        ).model_dump()

        for _ in range(5):
            response = await client.patch(
                url='/users/me/password',
                headers=headers,
                json=data
            )
            assert response.status_code == 400

        response = await client.patch(
            url='/users/me/password',
            headers=headers,
            json=data
        )
        assert response.status_code == 429

    async def test_change_password_unauthorized_raises_401(
            self,
            client
    ):
        response = await client.patch(
            url='/users/me/password',
            json={}
        )
        assert response.status_code == 401

    async def test_change_password_deactivated_user_return_403(
            self,
            client,
            get_auth_headers,
            test_deactivate_user
    ):
        headers = get_auth_headers(test_deactivate_user)
        response = await client.patch(url='/users/me/password', headers=headers)
        assert response.status_code == 403

        assert response.json()['detail'] == 'Inactive user'
import pytest


class TestRegister:
    async def test_register_success(self, client, user_data):
        response = await client.post('/auth/register', json=user_data)

        assert response.status_code == 201
        body = response.json()
        assert body['email'] == user_data['email']
        assert body['username'] == user_data['username']
        assert 'password' not in body
        assert 'hashed_password' not in body

    async def test_register_duplicate_email(self, client, user_data):
        await client.post('/auth/register', json=user_data)

        # test_user fixture already created user with same email
        duplicate = {**user_data, 'username': 'other_user'}
        response = await client.post('/auth/register', json=duplicate)

        assert response.status_code == 400
        assert 'email' in response.json()['detail'].lower()

    async def test_register_duplicate_username(self, client, user_data):
        await client.post('/auth/register', json=user_data)

        # test_user fixture already created user with same username
        duplicate = {**user_data, 'email': 'other@example.com'}
        response = await client.post('/auth/register', json=duplicate)

        assert response.status_code == 400
        assert 'username' in response.json()['detail'].lower()

    async def test_register_weak_password(self, client, user_data):
        weak = {**user_data, 'password': 'pass'}
        response = await client.post('/auth/register', json=weak)

        assert response.status_code == 422


    async def test_register_invalid_email(self, client, user_data):
        invalid = {**user_data, 'email': 'not-an-email'}
        response = await client.post('/auth/register', json=invalid)

        assert response.status_code == 422


class TestRegisterWithLanguage:
    @pytest.fixture
    def user_data_with_language(self, user_data):
        return {
            **user_data,
            'active_learning_language': 'en',
            'active_language_level': 'B1',
        }

    async def test_register_with_language_success(self, client, user_data_with_language):
        response = await client.post('/auth/register/complete', json=user_data_with_language)

        assert response.status_code == 201
        body = response.json()
        assert body['email'] == user_data_with_language['email']
        assert body['active_learning_language']['language'] == 'en'
        assert body['active_learning_language']['level'] == 'B1'
        assert 'hashed_password' not in body

    async def test_register_with_language_default_level(self, client, user_data_with_language):
        # active_language_level is optional, defaults to A1
        data = {**user_data_with_language}
        data.pop('active_language_level')
        response = await client.post('/auth/register/complete', json=data)

        assert response.status_code == 201
        assert response.json()['active_learning_language']['level'] == 'A1'

    async def test_register_with_language_duplicate_email(self, client, user_data_with_language, test_user):
        # test_user already created user with same email
        duplicate = {**user_data_with_language, 'username': 'other_user'}
        response = await client.post('/auth/register/complete', json=duplicate)

        assert response.status_code == 400
        assert 'email' in response.json()['detail'].lower()

    async def test_register_with_language_invalid_language_code(self, client, user_data_with_language):
        invalid = {**user_data_with_language, 'active_learning_language': 'C3'}
        response = await client.post('/auth/register/complete', json=invalid)

        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, client, user_data, test_user):
        response = await client.post('/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password'],
        })

        assert response.status_code == 200
        body = response.json()
        assert 'access_token' in body
        assert body['token_type'] == 'bearer'

    async def test_login_wrong_password(self, client, test_user, user_data):
        response = await client.post('/auth/login', json={
            'email': user_data['email'],
            'password': 'wrongpass1',
        })

        assert response.status_code == 401
        assert 'incorrect email or password' in response.json()['detail'].lower()


    async def test_login_nonexistent_email(self, client):
        response = await client.post('/auth/login', json={
            'email': 'nobody@example.com',
            'password': 'somepass1',
        })

        assert response.status_code == 401
        assert 'incorrect email or password' in response.json()['detail'].lower()


    async def test_login_inactive_user(self, client, db, user_data, test_user):
        test_user.is_active = False
        await db.flush()

        response = await client.post('/auth/login', json={
            'email': user_data['email'],
            'password': user_data['password'],
        })

        assert response.status_code == 403
        assert 'account is disabled' in response.json()['detail'].lower()
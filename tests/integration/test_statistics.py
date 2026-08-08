class TestUserStatistics:

    async def test_statistics_returns_correct_structure(
            self,
            client,
            get_auth_headers,
            test_user,
            user_history
    ):
        response = await client.get(
            '/users/me/statistics/',
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200
        body = response.json()
        assert 'total_exercises' in body
        assert 'total_answered' in body
        assert 'accuracy' in body
        assert 'total_study_hours' in body
        assert 'current_streak_days' in body
        assert 'is_today_completed' in body

    async def test_statistics_correct_counts(
            self,
            client,
            get_auth_headers,
            test_user,
            user_history
    ):
        response = await client.get(
            '/users/me/statistics/',
            headers=get_auth_headers(test_user)
        )

        body = response.json()
        assert body['total_exercises'] == 5   # 3 correct + 1 incorrect + 1 skip
        assert body['total_answered'] == 4    # excluding skip
        assert body['accuracy'] == 75.0       # 3 correct / 4 answered

    async def test_statistics_is_today_completed(
            self,
            client,
            get_auth_headers,
            test_user,
            user_history
    ):
        # user_history records created today — is_today_completed must be True
        response = await client.get(
            '/users/me/statistics/',
            headers=get_auth_headers(test_user)
        )

        assert response.json()['is_today_completed'] is True

    async def test_statistics_empty_when_no_history(
            self,
            client,
            get_auth_headers,
            test_user
    ):
        response = await client.get(
            '/users/me/statistics/',
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200
        body = response.json()
        assert body['total_exercises'] == 0
        assert body['accuracy'] == 0.0
        assert body['is_today_completed'] is False

    async def test_statistics_requires_auth(self, client):
        response = await client.get('/users/me/statistics/')

        assert response.status_code == 401
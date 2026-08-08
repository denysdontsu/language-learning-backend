class TestExerciseTopics:

    async def test_topics_returns_list(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercises_batch
    ):
        response = await client.get(
            '/exercises/topics',
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_topics_returns_correct_topics(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercises_batch
    ):
        response = await client.get(
            '/exercises/topics',
            headers=get_auth_headers(test_user)
        )

        topics = response.json()
        assert 'Grammar' in topics
        assert 'Vocabulary' in topics

    async def test_topics_empty_when_no_exercises(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language
    ):
        # No exercises in DB
        response = await client.get(
            '/exercises/topics',
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_topics_requires_active_language(
            self,
            client,
            get_auth_headers,
            test_user,
            exercises_batch
    ):
        # test_user without active language
        response = await client.get(
            '/exercises/topics',
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 403

    async def test_topics_requires_auth(self, client, exercises_batch):
        response = await client.get('/exercises/topics')

        assert response.status_code == 401


class TestGetNextExercise:

    async def test_get_next_returns_exercise(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        response = await client.get(
            '/exercises/next',
            params={'topic': 'Grammar', 'difficult_level': 'B1'},
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200
        body = response.json()
        assert body['id'] == exercise_en_uk.id
        assert 'question_text' in body
        assert 'instruction' in body

    async def test_get_next_defaults_to_user_level(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        # test_user_learning_language has level B1
        # no difficult_level param — should use user's level
        response = await client.get(
            '/exercises/next',
            params={'topic': 'Grammar'},
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200
        assert response.json()['id'] == exercise_en_uk.id

    async def test_get_next_normalizes_topic(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        # topic is case-insensitive, normalized to title case
        response = await client.get(
            '/exercises/next',
            params={'topic': 'grammar', 'difficult_level': 'B1'},
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 200

    async def test_get_next_404_when_no_exercises(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
    ):
        response = await client.get(
            '/exercises/next',
            params={'topic': 'NonExistentTopic', 'difficult_level': 'B1'},
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 404

    async def test_get_next_excludes_exercise_by_id(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        # Only one exercise exists — excluding it should return 404
        response = await client.get(
            '/exercises/next',
            params={
                'topic': 'Grammar',
                'difficult_level': 'B1',
                'exclude_id': exercise_en_uk.id
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 404

    async def test_get_next_requires_active_language(
            self,
            client,
            get_auth_headers,
            test_user,
            exercise_en_uk
    ):
        # test_user without active language
        response = await client.get(
            '/exercises/next',
            params={'topic': 'Grammar'},
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 403

    async def test_get_next_requires_auth(self, client, exercise_en_uk):
        response = await client.get(
            '/exercises/next',
            params={'topic': 'Grammar'}
        )

        assert response.status_code == 401


class TestSubmitExercise:

    async def test_submit_correct_answer(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        response = await client.post(
            f'/exercises/{exercise_en_uk.id}/submit',
            json={
                'user_answer': exercise_en_uk.correct_answer,
                'time_spent_seconds': 30
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 201
        body = response.json()
        assert body['status'] == 'correct'
        assert body['is_correct'] is True
        assert body['correct_answer'] == exercise_en_uk.correct_answer

    async def test_submit_incorrect_answer(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        response = await client.post(
            f'/exercises/{exercise_en_uk.id}/submit',
            json={
                'user_answer': 'wrong answer',
                'time_spent_seconds': 15
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 201
        body = response.json()
        assert body['status'] == 'incorrect'
        assert body['is_correct'] is False

    async def test_submit_skip(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        # Empty answer treated as skip
        response = await client.post(
            f'/exercises/{exercise_en_uk.id}/submit',
            json={
                'user_answer': '',
                'time_spent_seconds': 5
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 201
        body = response.json()
        assert body['status'] == 'skip'
        assert body['is_correct'] is False

    async def test_submit_case_insensitive(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language,
            exercise_en_uk
    ):
        # Answer matching is case-insensitive via normalize_answer
        response = await client.post(
            f'/exercises/{exercise_en_uk.id}/submit',
            json={
                'user_answer': exercise_en_uk.correct_answer.upper(),
                'time_spent_seconds': 20
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 201
        assert response.json()['status'] == 'correct'

    async def test_submit_nonexistent_exercise(
            self,
            client,
            get_auth_headers,
            test_user,
            test_user_learning_language
    ):
        response = await client.post(
            '/exercises/99999/submit',
            json={
                'user_answer': 'some answer',
                'time_spent_seconds': 10
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 404

    async def test_submit_requires_active_language(
            self,
            client,
            get_auth_headers,
            test_user,
            exercise_en_uk
    ):
        response = await client.post(
            f'/exercises/{exercise_en_uk.id}/submit',
            json={
                'user_answer': 'answer',
                'time_spent_seconds': 10
            },
            headers=get_auth_headers(test_user)
        )

        assert response.status_code == 403

    async def test_submit_requires_auth(self, client, exercise_en_uk):
        response = await client.post(
            f'/exercises/{exercise_en_uk.id}/submit',
            json={
                'user_answer': 'answer',
                'time_spent_seconds': 10
            }
        )

        assert response.status_code == 401
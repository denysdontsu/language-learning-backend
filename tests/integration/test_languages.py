from app.models import UserLevelLanguage
from app.schemas import LanguageEnum, LanguageLevelEnum, UserLanguageLevelUpdate


class TestGetLearningLanguages:

    async def test_get_languages_empty_list(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.get(url='/users/me/languages/', headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_languages_return_list(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.get(url='/users/me/languages/', headers=headers)
        assert response.status_code == 200

        response_list = response.json()
        assert len(response_list) == 1
        assert response_list[0]['id'] == test_user_learning_language.id
        assert response_list[0]['language'] == test_user_learning_language.language
        assert response_list[0]['level'] == test_user_learning_language.level

    async def test_get_languages_return_only_own_languages(
            self,
            client,
            db,
            test_user,
            test_other_user,
            test_user_learning_language,
            get_auth_headers
    ):
        other_language = UserLevelLanguage(
            user_id=test_other_user.id,
            language=LanguageEnum.UK,
            level=LanguageLevelEnum.A1
        )
        db.add(other_language)
        await db.flush()

        headers = get_auth_headers(test_user)
        response = await client.get(url='/users/me/languages/', headers=headers)
        assert response.status_code == 200

        response_list = response.json()
        assert len(response_list) == 1
        assert response_list[0]['id'] == test_user_learning_language.id

    async def test_get_language_deactivated_user_return_403(
            self,
            client,
            get_auth_headers,
            test_deactivate_user
    ):
        headers = get_auth_headers(test_deactivate_user)
        response = await client.get(url='/users/me/languages/', headers=headers)
        assert response.status_code == 403

        assert response.json()['detail'] == 'Inactive user'


class TestCreateUpdateLanguage:
    """Base class with shared validation/auth tests, inherited by subclasses."""

    async def test_add_language_invalid_language_code_raises_422(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.post(
            url='/users/me/languages/xx',
            headers=headers,
            json={}
        )
        assert response.status_code == 422

    async def test_add_language_unauthorized_raises_401(
            self,
            client
    ):
        response = await client.post(
            url='/users/me/languages/en',
            json={}
        )
        assert response.status_code == 401


class TestCreateFirstLanguage(TestCreateUpdateLanguage):

    async def test_create_new_language_default_level(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.post(
            url=f'/users/me/languages/{LanguageEnum.EN.value}',
            headers=headers,
            json={}
        )
        assert response.status_code == 201

        response_dict = response.json()
        assert response_dict['language'] == LanguageEnum.EN.value
        assert response_dict['level'] == LanguageLevelEnum.A1.value

    async def test_create_new_language_with_level(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        data = UserLanguageLevelUpdate(
            level=LanguageLevelEnum.B2.value
        ).model_dump()

        response = await client.post(
            url=f'/users/me/languages/{LanguageEnum.EN.value}',
            headers=headers,
            json=data
        )
        assert response.status_code == 201

        response_dict = response.json()
        assert response_dict['language'] == LanguageEnum.EN.value
        assert response_dict['level'] == LanguageLevelEnum.B2.value

    async def test_create_first_language_auto_activates(
            self,
            db,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.post(
            url=f'/users/me/languages/{LanguageEnum.EN.value}',
            headers=headers,
            json={}
        )
        assert response.status_code == 201

        me_response = await client.get(url='/users/me/', headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()['active_learning_language']['language'] == LanguageEnum.EN.value
        assert me_response.json()['active_learning_language']['level'] == LanguageLevelEnum.A1.value

    async def test_create_second_language_not_active_by_default(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.post(
            url=f'/users/me/languages/{LanguageEnum.UK.value}',
            headers=headers,
            json={}
        )
        assert response.status_code == 201

        me_response = await client.get(url='/users/me/', headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()['active_learning_language']['language'] == LanguageEnum.EN.value
        assert me_response.json()['active_learning_language']['level'] == LanguageLevelEnum.B1.value

    async def test_create_language_with_make_active_true(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        data = UserLanguageLevelUpdate(
            make_active=True
        ).model_dump()

        response = await client.post(
            url=f'/users/me/languages/{LanguageEnum.UK.value}',
            headers=headers,
            json=data
        )
        assert response.status_code == 201

        me_response = await client.get(url='/users/me/', headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()['active_learning_language']['language'] == LanguageEnum.UK.value


class TestUpdateLanguage(TestCreateUpdateLanguage):

    async def test_update_existing_language_level(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        data = UserLanguageLevelUpdate(
            level=LanguageLevelEnum.C1.value
        ).model_dump()

        response = await client.post(
            url=f'/users/me/languages/{test_user_learning_language.language.value}',
            headers=headers,
            json=data
        )
        assert response.status_code == 201

        response_dict = response.json()
        assert response_dict['id'] == test_user_learning_language.id
        assert response_dict['level'] == LanguageLevelEnum.C1.value

    async def test_update_existing_language_no_level_returns_unchanged(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.post(
            url=f'/users/me/languages/{test_user_learning_language.language.value}',
            headers=headers,
            json={}
        )
        assert response.status_code == 201

        response_dict = response.json()
        assert response_dict['id'] == test_user_learning_language.id
        assert response_dict['level'] == test_user_learning_language.level

    async def test_update_existing_language_make_active_true(
            self,
            client,
            db,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        second_language = UserLevelLanguage(
            user_id=test_user.id,
            language=LanguageEnum.UK,
            level=LanguageLevelEnum.A1
        )
        db.add(second_language)
        await db.flush()

        headers = get_auth_headers(test_user)
        data = UserLanguageLevelUpdate(
            make_active=True
        ).model_dump()

        response = await client.post(
            url=f'/users/me/languages/{second_language.language.value}',
            headers=headers,
            json=data
        )
        assert response.status_code == 201

        me_response = await client.get(url='/users/me/', headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()['active_learning_language']['language'] == second_language.language.value
        assert me_response.json()['active_learning_language']['level'] == second_language.level.value


class TestDeleteLanguage:

    async def test_delete_language_success(
            self,
            client,
            db,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        second_language = UserLevelLanguage(
            user_id=test_user.id,
            language=LanguageEnum.UK,
            level=LanguageLevelEnum.A1
        )
        db.add(second_language)
        await db.flush()

        headers = get_auth_headers(test_user)
        response = await client.delete(
            url=f'/users/me/languages/{second_language.language.value}',
            headers=headers
        )
        assert response.status_code == 204

        list_response = await client.get(url='/users/me/languages/', headers=headers)
        assert list_response.status_code == 200
        remaining_languages = [lang['language'] for lang in list_response.json()]
        assert second_language.language.value not in remaining_languages

    async def test_delete_language_not_in_list_raises_404(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.delete(
            url=f'/users/me/languages/{LanguageEnum.UK.value}',
            headers=headers
        )
        assert response.status_code == 404
        assert response.json()['detail'] == f'Language {LanguageEnum.UK.value} not found in learning list'

    async def test_delete_last_language_raises_400(
            self,
            client,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.delete(
            url=f'/users/me/languages/{test_user_learning_language.language.value}',
            headers=headers
        )
        assert response.status_code == 400
        assert response.json()['detail'] == 'Cannot remove last language from learning list'

    async def test_delete_active_language_raises_400(
            self,
            client,
            db,
            test_user,
            test_user_learning_language,
            get_auth_headers
    ):
        second_language = UserLevelLanguage(
            user_id=test_user.id,
            language=LanguageEnum.UK,
            level=LanguageLevelEnum.A1
        )
        db.add(second_language)
        await db.flush()

        headers = get_auth_headers(test_user)
        response = await client.delete(
            url=f'/users/me/languages/{test_user_learning_language.language.value}',
            headers=headers
        )
        assert response.status_code == 400
        assert (response.json()['detail']
                == 'Cannot remove active learning language. Set another language as active first.')

    async def test_delete_language_invalid_language_code_raises_422(
            self,
            client,
            test_user,
            get_auth_headers
    ):
        headers = get_auth_headers(test_user)
        response = await client.delete(
            url='/users/me/languages/xx',
            headers=headers
        )
        assert response.status_code == 422

    async def test_delete_language_unauthorized_raises_401(
            self,
            client
    ):
        response = await client.delete(url='/users/me/languages/en')
        assert response.status_code == 401
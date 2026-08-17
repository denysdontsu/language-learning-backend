# Standard library
import asyncio
import random
from datetime import datetime, UTC, timedelta

# Third-party
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# DB
from app.db.connection import async_session_maker

# Models
from app.models import User, Exercise, UserExerciseHistory, UserLevelLanguage

# Schemas
from app.schemas import (
    ExerciseTypeEnum,
    ExerciseStatusEnum,
    LanguageEnum,
    LanguageLevelEnum,
    UserRoleEnum,
)


# Helpers

def random_date(days_back: int = 90) -> datetime:
    """Return a random UTC datetime within the last N days."""
    offset = random.randint(0, days_back * 24 * 60 * 60)
    return datetime.now(UTC) - timedelta(seconds=offset)


def weighted_status() -> ExerciseStatusEnum:
    """Return status with realistic distribution: 60/25/15."""
    return random.choices(
        [ExerciseStatusEnum.CORRECT, ExerciseStatusEnum.INCORRECT, ExerciseStatusEnum.SKIP],
        weights=[60, 25, 15]
    )[0]


# Seed data

USERS = [
    {
        'email': 'admin@example.com',
        'name': 'Admin',
        'username': 'admin',
        'native_language': LanguageEnum.UK,
        'role': UserRoleEnum.ADMIN,
        'password': 'admin1234',
    },
    {
        'email': 'alice@example.com',
        'name': 'Alice',
        'username': 'alice',
        'native_language': LanguageEnum.UK,
        'role': UserRoleEnum.USER,
        'password': 'alice1234',
    },
    {
        'email': 'bob@example.com',
        'name': 'Bob',
        'username': 'bob',
        'native_language': LanguageEnum.EN,
        'role': UserRoleEnum.USER,
        'password': 'bob1234',
    },
    {
        'email': 'clara@example.com',
        'name': 'Clara',
        'username': 'clara',
        'native_language': LanguageEnum.DE,
        'role': UserRoleEnum.USER,
        'password': 'clara1234',
    },
]

# (question_text, correct_answer, topic, type, difficulty, q_lang, a_lang, options)
EXERCISES = [
    # A1 - Articles
    ('___ cat is on the table.', 'The', 'Articles', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A1, LanguageEnum.EN, LanguageEnum.EN, None),
    ('I have ___ apple.', 'an', 'Articles', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A1, LanguageEnum.EN, LanguageEnum.EN, None),
    ('She is ___ teacher.', 'a', 'Articles', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.A1, LanguageEnum.EN, LanguageEnum.EN, {'a': 'a', 'b': 'an', 'c': 'the', 'd': '-'}),
    ('___ sun rises in the east.', 'The', 'Articles', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A1, LanguageEnum.EN, LanguageEnum.EN, None),
    ('He has ___ dog.', 'a', 'Articles', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.A1, LanguageEnum.EN, LanguageEnum.EN, {'a': 'a', 'b': 'an', 'c': 'the', 'd': '-'}),

    # A1 - Vocabulary
    ('Кішка', 'Cat', 'Vocabulary', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.A1, LanguageEnum.UK, LanguageEnum.EN, None),
    ('Будинок', 'House', 'Vocabulary', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.A1, LanguageEnum.UK, LanguageEnum.EN, None),
    ('Вода', 'Water', 'Vocabulary', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.A1, LanguageEnum.UK, LanguageEnum.EN, {'a': 'Fire', 'b': 'Water', 'c': 'Earth', 'd': 'Air'}),
    ('Яблуко', 'Apple', 'Vocabulary', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.A1, LanguageEnum.UK, LanguageEnum.EN, None),
    ('Школа', 'School', 'Vocabulary', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.A1, LanguageEnum.UK, LanguageEnum.EN, None),

    # A2 - Prepositions
    ('She is sitting ___ the chair.', 'on', 'Prepositions', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, None),
    ('The book is ___ the table.', 'under', 'Prepositions', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, {'a': 'on', 'b': 'under', 'c': 'beside', 'd': 'above'}),
    ('He lives ___ London.', 'in', 'Prepositions', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, None),
    ('We arrived ___ Monday.', 'on', 'Prepositions', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, None),
    ('She was born ___ 1995.', 'in', 'Prepositions', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, {'a': 'at', 'b': 'on', 'c': 'in', 'd': 'by'}),

    # A2 - Tenses
    ('Він читав книгу вчора.', 'He was reading a book yesterday.', 'Tenses', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.A2, LanguageEnum.UK, LanguageEnum.EN, None),
    ('I ___ (go) to school every day.', 'go', 'Tenses', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, None),
    ('She ___ (watch) TV now.', 'is watching', 'Tenses', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, None),
    ('They ___ (play) football yesterday.', 'played', 'Tenses', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.A2, LanguageEnum.EN, LanguageEnum.EN, {'a': 'play', 'b': 'played', 'c': 'are playing', 'd': 'will play'}),
    ('Вона вже пообідала.', 'She has already had lunch.', 'Tenses', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.A2, LanguageEnum.UK, LanguageEnum.EN, None),

    # B1 - Grammar
    ('If I ___ rich, I would travel the world.', 'were', 'Grammar', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.B1, LanguageEnum.EN, LanguageEnum.EN, None),
    ('She said she ___ come later.', 'would', 'Grammar', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.B1, LanguageEnum.EN, LanguageEnum.EN, {'a': 'will', 'b': 'would', 'c': 'shall', 'd': 'should'}),
    ('Якби він знав правду, він би розповів нам.', 'If he had known the truth, he would have told us.', 'Grammar', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.B1, LanguageEnum.UK, LanguageEnum.EN, None),
    ('By the time she arrived, we ___ already left.', 'had', 'Grammar', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.B1, LanguageEnum.EN, LanguageEnum.EN, None),
    ('The report ___ submitted by Friday.', 'must be', 'Grammar', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.B1, LanguageEnum.EN, LanguageEnum.EN, {'a': 'must', 'b': 'must be', 'c': 'should', 'd': 'will'}),

    # B1 - Tenses
    ('I ___ here for three years.', 'have been living', 'Tenses', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.B1, LanguageEnum.EN, LanguageEnum.EN, None),
    ('Вони будуть будувати будинок наступного літа.', 'They will be building a house next summer.', 'Tenses', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.B1, LanguageEnum.UK, LanguageEnum.EN, None),
    ('She ___ (finish) the project before the deadline.', 'will have finished', 'Tenses', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.B1, LanguageEnum.EN, LanguageEnum.EN, {'a': 'finishes', 'b': 'will finish', 'c': 'will have finished', 'd': 'has finished'}),

    # B2 - Grammar
    ('Незважаючи на дощ, вони пішли на прогулянку.', 'Despite the rain, they went for a walk.', 'Grammar', ExerciseTypeEnum.SENTENCE_TRANSLATION, LanguageLevelEnum.B2, LanguageEnum.UK, LanguageEnum.EN, None),
    ('___ he study hard, he might pass the exam.', 'Should', 'Grammar', ExerciseTypeEnum.FILL_BLANK, LanguageLevelEnum.B2, LanguageEnum.EN, LanguageEnum.EN, None),
    ('The earlier you start, ___ you finish.', 'the sooner', 'Grammar', ExerciseTypeEnum.MULTIPLE_CHOICE, LanguageLevelEnum.B2, LanguageEnum.EN, LanguageEnum.EN, {'a': 'sooner', 'b': 'the sooner', 'c': 'more sooner', 'd': 'the more soon'}),
]

USER_LANGUAGES = [
    ('admin', LanguageEnum.EN, LanguageLevelEnum.B1),
    ('alice', LanguageEnum.EN, LanguageLevelEnum.B1),
    ('alice', LanguageEnum.DE, LanguageLevelEnum.A2),
    ('bob', LanguageEnum.UK, LanguageLevelEnum.A2),
    ('clara', LanguageEnum.EN, LanguageLevelEnum.B2),
]

HISTORY_PER_USER = 150


# Seed functions

async def seed_users(db: AsyncSession) -> dict[str, User]:
    """Create seed users. Returns dict username -> User."""
    from app.core.security import hash_password

    users = {}
    for data in USERS:
        user = User(
            email=data['email'],
            name=data['name'],
            username=data['username'],
            native_language=data['native_language'],
            role=data['role'],
            hashed_password=hash_password(data['password']),
            is_active=True,
        )
        db.add(user)
        users[data['username']] = user

    await db.flush()
    return users


async def seed_exercises(db: AsyncSession) -> list[Exercise]:
    """Create seed exercises. Returns list of Exercise."""
    exercises = []
    for (q_text, answer, topic, ex_type, level, q_lang, a_lang, options) in EXERCISES:
        exercise = Exercise(
            question_text=q_text,
            correct_answer=answer,
            topic=topic,
            type=ex_type,
            difficult_level=level,
            question_language=q_lang,
            answer_language=a_lang,
            options=options,
            is_active=True,
        )
        db.add(exercise)
        exercises.append(exercise)

    await db.flush()
    return exercises


async def seed_user_languages(
        db: AsyncSession,
        users: dict[str, User]
) -> None:
    """Assign learning languages to users and set active language."""
    for username, lang, level in USER_LANGUAGES:
        user = users[username]
        user_lang = UserLevelLanguage(
            user_id=user.id,
            language=lang,
            level=level,
        )
        db.add(user_lang)
        await db.flush()

        # Set first language as active if not set yet
        if user.active_learning_language_id is None:
            user.active_learning_language_id = user_lang.id


async def seed_history(
        db: AsyncSession,
        users: dict[str, User],
        exercises: list[Exercise],
) -> None:
    """Generate exercise history for non-admin users."""
    non_admin = [u for u in users.values() if u.role != UserRoleEnum.ADMIN]

    for user in non_admin:
        for _ in range(HISTORY_PER_USER):
            exercise = random.choice(exercises)
            status = weighted_status()

            record = UserExerciseHistory(
                user_id=user.id,
                exercise_id=exercise.id,
                status=status,
                user_answer=None if status == ExerciseStatusEnum.SKIP else (
                    exercise.correct_answer if status == ExerciseStatusEnum.CORRECT else 'wrong'
                ),
                time_spent_seconds=random.randint(5, 120),
                completed_at=random_date(days_back=90),
            )
            db.add(record)

    await db.flush()


# Entry point

async def seed() -> None:
    async with async_session_maker() as db:
        # Check if already seeded
        existing = await db.scalar(select(User))
        if existing:
            print('Database already seeded, skipping.')
            return

        print('Seeding users...')
        users = await seed_users(db)

        print('Seeding exercises...')
        exercises = await seed_exercises(db)

        print('Seeding user languages...')
        await seed_user_languages(db, users)

        print('Seeding exercise history...')
        await seed_history(db, users, exercises)

        await db.commit()
        print('Seed completed successfully.')


if __name__ == '__main__':
    asyncio.run(seed())
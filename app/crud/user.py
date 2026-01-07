from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserLevelLanguage
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateWithLanguage


async def get_user_by_id(
        db: AsyncSession,
        user_id: int
) -> User | None:
    """
    Get user by ID from database.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User | None: User object if found, None otherwise
    """
    return await db.get(User, user_id)


async def get_user_by_email(
        db: AsyncSession,
        email: str
) -> User | None:
    """
    Get user by email address.

    Args:
        db: Database session
        email: User email address

    Returns:
        User | None: User object if found, None otherwise
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)

    return result.scalars().one_or_none()


async def get_user_by_username(
        db: AsyncSession,
        username: str
) -> User | None:
    """
    Get user by username.

    Args:
        db: Database session
        username: Username to search for

    Returns:
        User | None: User object if found, None otherwise
    """
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)

    return result.scalars().one_or_none()


async def create_user(
        db: AsyncSession,
        user: UserCreate,
        hashed_password: str,
) -> User:
    """
    Create new user without active learning language.

    Used for simple registration flow where user selects
    learning language later.

    Args:
        db: Database session
        user: User creation data
        hashed_password: Pre-hashed password

    Returns:
        User: Created user object
    """
    new_user = User(
        email=user.email,
        name=user.name,
        username=user.username,
        native_language=user.native_language,
        hashed_password=hashed_password,
        active_learning_language_id = None
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def create_user_with_language(
        db: AsyncSession,
        user: UserCreateWithLanguage,
        hashed_password: str,
) -> User:
    """
    Create new user with active learning language.

    Used for complete registration flow. Creates user and associated
    language entry in a single transaction, then links them together.

    Transaction steps:
    1. Create user (with NULL active_learning_language_id)
    2. Flush to get user.id
    3. Create language entry
    4. Flush to get language.id
    5. Link user.active_learning_language_id to language.id
    6. Commit transaction

    Args:
        db: Database session
        user: User creation data with language info
        hashed_password: Pre-hashed password

    Returns:
        User: Created user object with active language set
    """
    # Create user
    new_user = User(
        email=user.email,
        name=user.name,
        username=user.username,
        native_language=user.native_language,
        hashed_password=hashed_password,
        active_learning_language_id=None
    )
    db.add(new_user)
    await db.flush()

    # Create learning language entry
    new_language = UserLevelLanguage(
        user_id=user.id,
        language=user.active_learning_language,
        level=user.active_language_level
    )
    db.add(new_language)
    await db.flush()

    # Link user to active language
    new_user.active_learning_language_id = new_language.id
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_active_language(
        db:AsyncSession,
        user: User,
        language_id: int
) -> User:
    """
    Update user's active learning language.

    Sets which language the user is currently learning.
    Does not validate if language exists - validation should
    be done in service layer.

    Args:
        db: Database session
        user: User object to update
        language_id: ID of UserLevelLanguage to set as active

    Returns:
        User: Updated user object
    """
    user.active_learning_language_id = language_id
    await db.commit()
    await db.refresh(user)
    return user
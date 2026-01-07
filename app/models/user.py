from sqlalchemy import Boolean, String, Text, CheckConstraint, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base
from app.db.column_types import bigint_pk, language, created_at


class User(Base):
    __tablename__ = 'users'

    # Primary key
    id: Mapped[bigint_pk]

    # Base info
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    native_language: Mapped[language]

    # Security
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default='user', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    created_at: Mapped[created_at]

    # Foreign keys
    active_learning_language_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            'user_level_languages.id',
            use_alter=True,
            name='fk_user_active_language'
        ),
        nullable=True)

    # Relationships with UserLevelLanguage
    learning_languages: Mapped[list['UserLevelLanguage']] = relationship(
        foreign_keys='UserLevelLanguage.user_id',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    active_learning_language: Mapped['UserLevelLanguage'] = relationship(
        'UserLevelLanguage',
        foreign_keys=[active_learning_language_id],
        viewonly=True
    )


    # Relationship with UserExerciseHistory
    exercise_history: Mapped[list['UserExerciseHistory']] = relationship(
        foreign_keys='UserExerciseHistory.user_id',
        back_populates='user',
        cascade= 'all, delete-orphan'
    )

    # Constraint
    __table_args__ = (
        CheckConstraint("email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
                        "check_email_format"),
    )


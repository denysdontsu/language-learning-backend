from sqlalchemy import Index
from sqlalchemy.orm import Mapped, relationship

from app.db.connection import Base
from app.db.column_types import bigint_pk, user_fk, language, level, created_at


class UserLevelLanguage(Base):
    __tablename__ = 'user_level_languages'

    # Primary key
    id: Mapped[bigint_pk]

    # Base info
    user_id: Mapped[user_fk]
    language: Mapped[language]
    level: Mapped[level]

    # Metadata
    created_at: Mapped[created_at]

    # Relationships
    user: Mapped['User'] = relationship(
        back_populates='learning_languages'
    )

    # Indexes
    __table_args__ = (
        Index('ix_user_language',
              'user_id',
              'language',
              unique=True),
    )
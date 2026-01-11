"""
Reusable column types for SQLAlchemy models.

Contains Annotated types for commonly used database column patterns:
- Primary keys (used in all tables)
- Foreign keys (standard references to users)
- Enum fields (language and proficiency level are used in multiple places)
- Timestamps (created_at for auditing)

Usage:
    from app.db.column_types import bigint_pk, language, created_at

    class MyModelOrm(Base):
        id: Mapped[bigint_pk]
        lang: Mapped[language]
        created_at: Mapped[created_at]
"""

from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime,ForeignKey, text, Enum as SQLEnum
from sqlalchemy.orm import mapped_column

from app.schemas.enums import LanguageEnum, LanguageLevelEnum

# Primary Keys
bigint_pk = Annotated[
    int,
    mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment='Surrogate key of the table'
    )
]

# Foreign Keys
user_fk = Annotated[
    int,
    mapped_column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        comment='Reference to user'
    )
]

# Enum fields
language = Annotated[
    LanguageEnum,
    mapped_column(
        SQLEnum(LanguageEnum, name='language'),
        nullable=False,
        comment='Language code in ISO 639-1" format'
    )
]

level = Annotated[
    LanguageLevelEnum,
    mapped_column(
        SQLEnum(LanguageLevelEnum, name='language_level'),
        nullable=False,
        comment='CEFR Language levels'
    )
]

# Timestamps
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        comment='Record creation date and time'
    )
]

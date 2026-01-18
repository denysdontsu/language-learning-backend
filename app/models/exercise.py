from sqlalchemy import String, Text, Boolean, Index, text, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.connection import Base
from app.db.column_types import bigint_pk, language, level, created_at
from app.schemas.enums import LanguageEnum, ExerciseTypeEnum


class Exercise(Base):
    __tablename__ = 'exercises'

    # Primary key
    id: Mapped[bigint_pk]

    # Basic info
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    difficult_level: Mapped[level]
    type: Mapped[ExerciseTypeEnum] = mapped_column(
        SQLEnum(
            ExerciseTypeEnum,
            name='exercise_type',
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Question
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_language: Mapped[language]

    # Answer
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_language: Mapped[language]

    # Translation (optional)
    question_translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_translation_language: Mapped[language | None] = mapped_column(
        SQLEnum(
            LanguageEnum,
            name='language',
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=True)

    # Metadata
    added_at: Mapped[created_at]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship with UserExerciseHistory
    history: Mapped[list['UserExerciseHistory']] = relationship(
        foreign_keys='UserExerciseHistory.exercise_id',
        back_populates='exercise'
    )

    # Constraint and index
    __table_args__ = (
        CheckConstraint(
            """
            (correct_answer_translation IS NULL AND answer_translation_language IS NULL) 
            OR 
            (correct_answer_translation IS NOT NULL AND answer_translation_language IS NOT NULL)
            """,
            name='check_translation_complete'
        ),
        Index('ix_exercises_active_topic_level',
              'topic',
              'difficult_level',
              postgresql_where=text('is_active=true')
              ),
    )
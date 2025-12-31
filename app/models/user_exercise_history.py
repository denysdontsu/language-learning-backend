from sqlalchemy import BigInteger, Boolean, Integer, Index, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base
from app.db.column_types import bigint_pk, user_fk, created_at


class UserExerciseHistory(Base):
    __tablename__ = 'user_exercise_history'

    # Primary key
    id: Mapped[bigint_pk]

    # Foreign key
    user_id: Mapped[user_fk]
    exercise_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('exercises.id', ondelete='RESTRICT'), nullable=False)

    # Base info
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata
    completed_at: Mapped[created_at]

    # Relationship with User
    user: Mapped['User'] = relationship(
        back_populates='exercise_history'
    )

    # Relationship with Exercise
    exercise: Mapped['Exercise'] = relationship(
        back_populates='history'
    )

    # Constraint and indexes
    __table_args__ = (
        Index('ix_user_history_completed',
              'user_id',
              'completed_at'),
        Index('ix_user_exercise',
              'user_id',
              'exercise_id'),
        CheckConstraint('time_spent_seconds >= 0',
                        name='positive_time'),
    )
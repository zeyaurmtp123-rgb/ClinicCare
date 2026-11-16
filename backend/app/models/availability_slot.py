from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index
)
from sqlalchemy.sql import func

from app.core.database import Base


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    # Unique ID for every availability slot
    id = Column(Integer, primary_key=True, index=True)

    # Which doctor owns this slot?
    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False
    )

    # When does the slot start?
    start_time = Column(DateTime, nullable=False)

    # When does the slot end?
    end_time = Column(DateTime, nullable=False)

    # When was this slot created?
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # End time must be later than start time
    __table_args__ = (
        CheckConstraint(
            "end_time > start_time",
            name="check_slot_time"
        ),
        Index(
            "ix_doctor_slot_start",
            "doctor_id",
            "start_time"
        )
    )
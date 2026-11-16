from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Enum,
    UniqueConstraint
)
from sqlalchemy.sql import func

from app.core.database import Base


# Appointment statuses
class AppointmentStatus(PyEnum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Appointment(Base):
    __tablename__ = "appointments"

    # Unique appointment ID
    id = Column(Integer, primary_key=True, index=True)

    # The currently booked slot
    slot_id = Column(
        Integer,
        ForeignKey("availability_slots.id"),
        nullable=True
    )

    # Patient who booked the appointment
    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    # Current appointment status
    status = Column(
        Enum(AppointmentStatus, name="appointment_status"),
        nullable=False,
        default=AppointmentStatus.BOOKED
    )

    # Previous slot retained when an appointment is cancelled
    cancelled_slot_id = Column(
        Integer,
        ForeignKey("availability_slots.id"),
        nullable=True
    )

    # Appointment creation time
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    # Last update time
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # A slot can belong to only one active appointment
    __table_args__ = (
        UniqueConstraint(
            "slot_id",
            name="uq_appointment_slot"
        ),
    )
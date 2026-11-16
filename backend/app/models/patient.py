from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    # Unique ID for every patient
    id = Column(Integer, primary_key=True, index=True)

    # Connect patient profile to the user account
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Patient's personal information
    name = Column(String(100), nullable=False)

    phone = Column(String(20), nullable=True)

    # Automatically save account creation time
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
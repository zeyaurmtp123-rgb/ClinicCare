from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    # Unique ID for every doctor
    id = Column(Integer, primary_key=True, index=True)

    # Connect doctor to their login account
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Doctor's personal and professional information
    name = Column(String(100), nullable=False)

    specialization = Column(String(100), nullable=False, index=True)

    # Automatically store account creation time
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
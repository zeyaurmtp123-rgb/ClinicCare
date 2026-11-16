
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


# User roles in our clinic system
class UserRole(PyEnum):
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"


# Users database table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(150), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(UserRole, name="user_role"), nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

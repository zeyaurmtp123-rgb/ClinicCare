
from datetime import date, datetime

from pydantic import BaseModel, Field


class DoctorSearchRequest(BaseModel):
    specialization: str = Field(
        min_length=2,
        max_length=100
    )

    appointment_date: date

class AvailableSlotResponse(BaseModel):
    slot_id: int
    start_time: datetime
    end_time: datetime


class DoctorSearchResponse(BaseModel):
    doctor_id: int
    name: str
    specialization: str
    available_slots: list[AvailableSlotResponse]

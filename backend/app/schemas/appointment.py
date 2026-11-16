from datetime import datetime

from pydantic import BaseModel, Field


class AppointmentBookingRequest(BaseModel):
    slot_id: int = Field(gt=0)


class AppointmentResponse(BaseModel):
    appointment_id: int
    slot_id: int
    patient_id: int
    status: str
    message: str


class MyAppointmentResponse(BaseModel):
    appointment_id: int
    slot_id: int | None
    doctor_name: str
    specialization: str
    start_time: datetime | None
    end_time: datetime | None
    status: str
class AppointmentRescheduleRequest(BaseModel):
    new_slot_id: int = Field(gt=0)
class DoctorAppointmentResponse(BaseModel):
    appointment_id: int
    patient_name: str
    patient_phone: str | None
    doctor_name: str
    start_time: datetime
    end_time: datetime
    status: str
class DoctorAppointmentStatusUpdate(BaseModel):
    status: str
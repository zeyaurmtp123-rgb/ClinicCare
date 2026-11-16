
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_patient
from app.models.user import User
from app.models.doctor import Doctor
from app.models.availability_slot import AvailabilitySlot
from app.models.appointment import Appointment, AppointmentStatus

from app.schemas.doctor_search import DoctorSearchRequest

router = APIRouter(
    prefix="/patients",
    tags=["Patient"]
)


@router.post("/search-doctors")
def search_doctors(
    search_data: DoctorSearchRequest,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    # Calculate the selected day's start and end time
    day_start = datetime.combine(
        search_data.appointment_date,
        time.min
    )

    day_end = day_start + timedelta(days=1)

    # Find doctors matching the specialization
    doctors = db.query(Doctor).filter(
        Doctor.specialization.ilike(
            search_data.specialization.strip()
        )
    ).all()

    results = []

    for doctor in doctors:

        # Find slots belonging to this doctor on the selected date
        slots = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.doctor_id == doctor.id,
            AvailabilitySlot.start_time >= day_start,
            AvailabilitySlot.start_time < day_end
        ).order_by(
            AvailabilitySlot.start_time
        ).all()

        available_slots = []

        for slot in slots:

            # Check whether this slot already has an active appointment
            existing_appointment = db.query(Appointment).filter(
                Appointment.slot_id == slot.id,
                Appointment.status.in_([
                    AppointmentStatus.BOOKED,
                    AppointmentStatus.COMPLETED,
                    AppointmentStatus.NO_SHOW
                ])
            ).first()

            if existing_appointment is None:
                available_slots.append({
                    "slot_id": slot.id,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time
                })

        # Include only doctors who have free slots
        if available_slots:
            results.append({
                "doctor_id": doctor.id,
                "name": doctor.name,
                "specialization": doctor.specialization,
                "available_slots": available_slots
            })

    return {
        "appointment_date": search_data.appointment_date,
        "doctors": results
    }

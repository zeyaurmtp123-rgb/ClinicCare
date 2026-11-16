
from datetime import datetime, timedelta, date, time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.dependencies import get_current_patient, get_current_doctor

from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.availability_slot import AvailabilitySlot
from app.models.appointment import Appointment, AppointmentStatus

from app.schemas.appointment import (
    AppointmentBookingRequest,
    AppointmentResponse,
    MyAppointmentResponse,
    AppointmentRescheduleRequest,
    DoctorAppointmentResponse,
    DoctorAppointmentStatusUpdate
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# 1. Book an appointment
@router.post(
    "/book",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
def book_appointment(
    booking_data: AppointmentBookingRequest,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == booking_data.slot_id
    ).with_for_update().first()

    if slot is None:
        raise HTTPException(status_code=404, detail="Availability slot not found")

    if slot.start_time <= datetime.now():
        raise HTTPException(status_code=400, detail="This appointment slot is in the past")

    existing_appointment = db.query(Appointment).filter(
        Appointment.slot_id == slot.id
    ).first()

    if existing_appointment:
        raise HTTPException(status_code=409, detail="This slot has already been booked")

    new_appointment = Appointment(
        slot_id=slot.id,
        patient_id=patient.id,
        status=AppointmentStatus.BOOKED
    )

    db.add(new_appointment)

    try:
        db.commit()
        db.refresh(new_appointment)

        return {
            "appointment_id": new_appointment.id,
            "slot_id": new_appointment.slot_id,
            "patient_id": new_appointment.patient_id,
            "status": new_appointment.status.value,
            "message": "Appointment booked successfully"
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This slot has already been booked")


# 2. Patient views their appointments
@router.get(
    "/my",
    response_model=list[MyAppointmentResponse]
)
def get_my_appointments(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(Appointment.created_at.desc()).all()

    results = []

    for appointment in appointments:
        history_slot_id = (
            appointment.slot_id
            if appointment.slot_id is not None
            else appointment.cancelled_slot_id
        )

        slot = None
        doctor = None

        if history_slot_id is not None:
            slot = db.query(AvailabilitySlot).filter(
                AvailabilitySlot.id == history_slot_id
            ).first()

        if slot is not None:
            doctor = db.query(Doctor).filter(
                Doctor.id == slot.doctor_id
            ).first()

        results.append({
            "appointment_id": appointment.id,
            "slot_id": history_slot_id,
            "doctor_name": doctor.name if doctor else "Unknown",
            "specialization": doctor.specialization if doctor else "Unknown",
            "start_time": slot.start_time if slot else None,
            "end_time": slot.end_time if slot else None,
            "status": appointment.status.value
        })

    return results


# 3. Patient cancels an appointment
@router.patch("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == patient.id
    ).with_for_update().first()

    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != AppointmentStatus.BOOKED:
        raise HTTPException(status_code=409, detail="Only booked appointments can be cancelled")

    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == appointment.slot_id
    ).with_for_update().first()

    if slot is None:
        raise HTTPException(status_code=404, detail="Appointment slot not found")

    cancellation_deadline = slot.start_time - timedelta(hours=2)

    if datetime.now() >= cancellation_deadline:
        raise HTTPException(
            status_code=400,
            detail="Cancellation is not allowed within 2 hours of the appointment"
        )

    appointment.cancelled_slot_id = slot.id
    appointment.slot_id = None
    appointment.status = AppointmentStatus.CANCELLED

    try:
        db.commit()

        return {
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment.id,
            "cancelled_slot_id": slot.id,
            "status": "CANCELLED"
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not cancel this appointment")


# 4. Patient reschedules an appointment
@router.patch("/{appointment_id}/reschedule")
def reschedule_appointment(
    appointment_id: int,
    reschedule_data: AppointmentRescheduleRequest,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == patient.id
    ).with_for_update().first()

    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != AppointmentStatus.BOOKED:
        raise HTTPException(status_code=409, detail="Only booked appointments can be rescheduled")

    old_slot_id = appointment.slot_id
    new_slot_id = reschedule_data.new_slot_id

    if old_slot_id is None:
        raise HTTPException(status_code=404, detail="Current appointment slot not found")

    if old_slot_id == new_slot_id:
        raise HTTPException(status_code=400, detail="Please select a different slot")

    slot_ids = sorted([old_slot_id, new_slot_id])
    locked_slots = {}

    for slot_id in slot_ids:
        slot = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == slot_id
        ).with_for_update().first()

        if slot is not None:
            locked_slots[slot_id] = slot

    old_slot = locked_slots.get(old_slot_id)
    new_slot = locked_slots.get(new_slot_id)

    if old_slot is None:
        raise HTTPException(status_code=404, detail="Current appointment slot not found")

    if new_slot is None:
        raise HTTPException(status_code=404, detail="New availability slot not found")

    if datetime.now() >= old_slot.start_time - timedelta(hours=2):
        raise HTTPException(
            status_code=400,
            detail="Rescheduling is not allowed within 2 hours of the appointment"
        )

    if new_slot.start_time <= datetime.now():
        raise HTTPException(status_code=400, detail="New slot is in the past")

    existing_appointment = db.query(Appointment).filter(
        Appointment.slot_id == new_slot.id
    ).first()

    if existing_appointment:
        raise HTTPException(status_code=409, detail="New slot has already been booked")

    appointment.slot_id = new_slot.id
    appointment.cancelled_slot_id = None

    try:
        db.commit()
        db.refresh(appointment)

        return {
            "message": "Appointment rescheduled successfully",
            "appointment_id": appointment.id,
            "old_slot_id": old_slot.id,
            "new_slot_id": new_slot.id,
            "status": appointment.status.value
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="New slot has already been booked")


# 5. Doctor views appointments: all, today, or upcoming
@router.get(
    "/doctor/my",
    response_model=list[DoctorAppointmentResponse]
)
def get_doctor_appointments(
    appointment_type: str = "all",
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    today = date.today()

    # COALESCE checks slot_id first.
    # If slot_id is NULL, it uses cancelled_slot_id.
    history_slot_id = func.coalesce(
        Appointment.slot_id,
        Appointment.cancelled_slot_id
    )

    query = db.query(Appointment).join(
        AvailabilitySlot,
        history_slot_id == AvailabilitySlot.id
    ).join(
        Patient,
        Appointment.patient_id == Patient.id
    ).filter(
        AvailabilitySlot.doctor_id == doctor.id
    )

    if appointment_type == "today":
        query = query.filter(
            AvailabilitySlot.start_time >= datetime.combine(today, time.min),
            AvailabilitySlot.start_time < datetime.combine(
                today + timedelta(days=1), time.min
            )
        )

    elif appointment_type == "upcoming":
        query = query.filter(
            AvailabilitySlot.start_time >= datetime.now()
        )

    elif appointment_type != "all":
        raise HTTPException(
            status_code=400,
            detail="Use today, upcoming, or all"
        )

    appointments = query.order_by(
        AvailabilitySlot.start_time
    ).all()

    results = []

    for appointment in appointments:
        # Get the active slot or the old slot of a cancelled appointment.
        appointment_slot_id = (
            appointment.slot_id
            if appointment.slot_id is not None
            else appointment.cancelled_slot_id
        )

        slot = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.id == appointment_slot_id
        ).first()

        patient = db.query(Patient).filter(
            Patient.id == appointment.patient_id
        ).first()

        results.append({
            "appointment_id": appointment.id,
            "patient_name": patient.name,
            "patient_phone": patient.phone,
            "doctor_name": doctor.name,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "status": appointment.status.value
        })

    return results


# 6. Doctor updates appointment status
@router.patch("/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    status_data: DoctorAppointmentStatusUpdate,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    if status_data.status not in ["COMPLETED", "NO_SHOW"]:
        raise HTTPException(
            status_code=400,
            detail="Status must be COMPLETED or NO_SHOW"
        )

    appointment = db.query(Appointment).join(
        AvailabilitySlot,
        Appointment.slot_id == AvailabilitySlot.id
    ).filter(
        Appointment.id == appointment_id,
        AvailabilitySlot.doctor_id == doctor.id
    ).with_for_update().first()

    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appointment.status != AppointmentStatus.BOOKED:
        raise HTTPException(
            status_code=409,
            detail="Only booked appointments can be updated"
        )

    appointment.status = AppointmentStatus(status_data.status)

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment status updated successfully",
        "appointment_id": appointment.id,
        "status": appointment.status.value
    }


# 7. Doctor weekly appointment report using raw SQL
@router.get("/doctor/weekly-report")
def get_weekly_appointment_report(
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    start_datetime = datetime.combine(week_start, time.min)
    end_datetime = start_datetime + timedelta(days=7)

    sql_query = text("""
        SELECT
            a.status AS status,
            COUNT(*) AS appointment_count
        FROM appointments a
        JOIN availability_slots s
            ON s.id = COALESCE(a.slot_id, a.cancelled_slot_id)
        WHERE s.doctor_id = :doctor_id
          AND s.start_time >= :week_start
          AND s.start_time < :week_end
        GROUP BY a.status
        ORDER BY a.status
    """)

    result = db.execute(
        sql_query,
        {
            "doctor_id": doctor.id,
            "week_start": start_datetime,
            "week_end": end_datetime
        }
    ).mappings().all()

    return {
        "doctor_name": doctor.name,
        "week_start": str(week_start),
        "week_end": str(week_start + timedelta(days=6)),
        "report": [
            {
                "status": row["status"],
                "appointment_count": row["appointment_count"]
            }
            for row in result
        ]
    }

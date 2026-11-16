
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from app.core.database import get_db
from app.core.dependencies import get_current_doctor
from app.models.user import User
from app.models.doctor import Doctor
from app.models.availability_slot import AvailabilitySlot
from app.models.appointment import Appointment
from app.schemas.availability import AvailabilitySlotCreate

router = APIRouter(
    prefix="/availability",
    tags=["Doctor Availability"]
)


# Create an availability slot
@router.post("/slots", status_code=status.HTTP_201_CREATED)
def create_availability_slot(
    slot_data: AvailabilitySlotCreate,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    # Find and lock the doctor's profile
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).with_for_update().first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    # Check for overlapping slots
    overlapping_slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.doctor_id == doctor.id,
        AvailabilitySlot.start_time < slot_data.end_time,
        AvailabilitySlot.end_time > slot_data.start_time
    ).first()

    if overlapping_slot:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This time overlaps with an existing slot"
        )

    # Create the new slot
    new_slot = AvailabilitySlot(
        doctor_id=doctor.id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time
    )

    db.add(new_slot)

    try:
        db.commit()
        db.refresh(new_slot)

        return {
            "message": "Availability slot created successfully",
            "slot_id": new_slot.id,
            "doctor_id": new_slot.doctor_id,
            "start_time": new_slot.start_time,
            "end_time": new_slot.end_time
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create this availability slot"
        )


# Delete an availability slot
@router.delete("/slots/{slot_id}")
def delete_availability_slot(
    slot_id: int,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    # Find the logged-in doctor's profile
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    if doctor is None:
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    # Find only the slot belonging to this doctor
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id,
        AvailabilitySlot.doctor_id == doctor.id
    ).with_for_update().first()

    if slot is None:
        raise HTTPException(
            status_code=404,
            detail="Availability slot not found"
        )

    # Check current and cancelled appointment history
    appointment = db.query(Appointment).filter(
        or_(
            Appointment.slot_id == slot.id,
            Appointment.cancelled_slot_id == slot.id
        )
    ).first()

    if appointment:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a slot linked to appointment history"
        )

    # Delete the slot
    db.delete(slot)
    db.commit()

    return {
        "message": "Availability slot deleted successfully",
        "slot_id": slot_id
    }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_doctor
from app.models.user import User
from app.models.doctor import Doctor

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.get("/")
def get_doctors():
    return {
        "message": "Doctor API is working",
        "doctors": []
    }


@router.get("/me")
def get_my_doctor_profile(
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    return {
        "doctor_id": doctor.id,
        "name": doctor.name,
        "specialization": doctor.specialization
    }
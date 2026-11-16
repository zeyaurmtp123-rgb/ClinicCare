
from pydantic import BaseModel, Field


# Schema for creating a doctor
class DoctorCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    specialization: str = Field(min_length=3, max_length=100)
    experience: int = Field(ge=0, le=60)


# Schema for displaying a doctor
class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    experience: int

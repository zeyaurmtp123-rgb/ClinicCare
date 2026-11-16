
from pydantic import BaseModel, EmailStr, Field, model_validator
from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: UserRole
    name: str = Field(min_length=3, max_length=100)
    specialization: str | None = Field(default=None, min_length=2, max_length=100)

    @model_validator(mode="after")
    def validate_specialization(self):
        if self.role == UserRole.DOCTOR and not self.specialization:
            raise ValueError("Specialization is required for doctors")
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

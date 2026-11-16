
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import doctor, auth, availability, patient, appointment

app = FastAPI(
    title="Clinic Appointment Booking System",
    description="API for managing clinic appointments",
    version="1.0.0"
)

# Allow Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect Doctor API
app.include_router(doctor.router)
app.include_router(auth.router)
app.include_router(availability.router)
app.include_router(patient.router)
app.include_router(appointment.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Clinic Appointment Booking System"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

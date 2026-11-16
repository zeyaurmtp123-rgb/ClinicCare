
# ClinicCare - Clinic Appointment Booking System

A web-based clinic appointment booking system that helps patients book appointments with doctors and helps doctors manage their availability and appointments.

## Features

- Patient and doctor registration and login
- Secure JWT authentication
- Password hashing using Argon2
- Doctor availability management
- Search doctors by specialization and date
- Book appointments
- Cancel and reschedule appointments
- Prevent double booking
- Prevent overlapping doctor slots
- Doctor appointment management
- Mark appointments as COMPLETED or NO_SHOW
- Weekly appointment reports
- Patient and doctor dashboards

## Technology Stack

### Backend
- Python
- FastAPI
- MySQL
- SQLAlchemy
- Pydantic
- JWT Authentication

### Frontend
- Next.js
- TypeScript
- React

### Testing and Database
- Pytest
- Alembic

## Project Structure

```text
ClinicAppointmentSystem/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── ER_Diagram.md
├── .gitignore
└── README.md
```

## Requirements

Install these software before running the project:

- Python 3.11 or above
- Node.js
- MySQL 8.4
- VS Code

## Backend Setup

Open a terminal:

```powershell
cd backend
```

Create and activate a virtual environment if you haven't already:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure your database credentials and JWT secret in `backend/.env`.

Run database migrations:

```powershell
alembic upgrade head
```

Start the backend server:

```powershell
python -m uvicorn app.main:app --reload
```

Backend URL:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

## Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the application:

http://localhost:3000

## Testing

Open a terminal in the backend directory and run:

```powershell
python -m pytest -v
```

The backend test suite passed 19 tests in the development environment.

## Security and Data Integrity

- Passwords are stored using secure password hashing.
- JWT is used for authentication.
- Role-based access is implemented for doctors and patients.
- Database constraints help prevent double booking.
- Appointment cancellation and rescheduling follow a two-hour restriction.
- Environment variables are kept in a private `.env` file.

## Author

Ziyaur Rahman

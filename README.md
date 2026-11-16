
# ClinicCare - Clinic Appointment Booking System

A web-based clinic appointment booking system that helps patients book appointments with doctors and helps doctors manage their availability and appointments.

## Features

- Patient and doctor registration and login
- Secure JWT authentication
- Password hashing
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
|
|-- backend/
|   |-- app/
|   |-- tests/
|   |-- alembic/
|   |-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |-- package.json
|
|-- README.md
```

## Requirements

Install these software before running the project:

- Python 3.11 or above
- Node.js
- MySQL 8.4
- VS Code

## Backend Setup

Open a terminal and run these commands:

```powershell
cd backend
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies if required:

```powershell
pip install -r requirements.txt
```

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

Open another terminal and run:

```powershell
cd frontend
```

Install frontend dependencies:

```powershell
npm install
```

Start the frontend:

```powershell
npm run dev
```

Open the application:

http://localhost:3000

## Testing

To run backend tests:

```powershell
cd backend
python -m pytest -v
```

The backend test suite has passed 19 tests in the development environment.

## Security and Data Integrity

- Passwords are stored using password hashing.
- JWT is used for authentication.
- Role-based access is implemented for doctors and patients.
- Database constraints help prevent double booking.
- Appointment cancellation and rescheduling follow a two-hour restriction.

## Author

Ziyaur Rahman

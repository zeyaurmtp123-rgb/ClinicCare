# ClinicCare – Clinic Appointment Booking System

ClinicCare is a web-based clinic appointment booking system that allows patients to search for doctors, book appointments, and manage their bookings. Doctors can manage their availability and appointments through their dashboard.

## Features

- Patient and doctor registration and login
- Secure JWT authentication
- Password hashing using Argon2
- Doctor availability management
- Search doctors by specialization and date
- Book appointments
- Cancel and reschedule appointments
- Prevent double booking
- Prevent overlapping doctor availability slots
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
- Argon2 Password Hashing

### Frontend
- Next.js
- React
- TypeScript

### Database and Testing
- MySQL
- Alembic
- Pytest

## Project Structure

```text
ClinicAppointmentSystem/
│
├── backend/
│   ├── app/
│   ├── tests/
│   ├── alembic/
│   ├── .env
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── ER_Diagram.md
├── .gitignore
└── README.md
```

## Requirements

Install the following software:

- Python 3.11 or above
- Node.js and npm
- MySQL 8.4
- Visual Studio Code

## Database Setup

1. Install and start MySQL Server.
2. Create a database named `clinic_db`.
3. Configure the database credentials in the backend `.env` file.
4. Run Alembic migrations to create the database tables.

```sql
CREATE DATABASE clinic_db;
```

## Environment Variables



Configure the following variables:

| Variable | Description |
|---|---|
| DB_USER | MySQL username |
| DB_PASSWORD | MySQL password |
| DB_HOST | MySQL host address |
| DB_PORT | MySQL port |
| DB_NAME | Database name |
| SECRET_KEY | Secret key for JWT authentication |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT token expiry time in minutes |

Example configuration:

```env
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=clinic_db
SECRET_KEY=your_secure_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```



## Backend Setup

Open a terminal in the project folder.

Navigate to the backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

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

API Documentation (Swagger):

http://127.0.0.1:8000/docs

## Frontend Setup

Open another terminal in the project folder.

Navigate to the frontend:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the frontend development server:

```powershell
npm run dev
```

Open the application:

http://localhost:3000

## Sample Credentials

The application supports patient and doctor registration.

Register a new patient or doctor through the registration page to create your own login credentials.

For evaluation, you can add your working test accounts below:

### Patient Account
- Email: zeyaurmtp123@gmail.com
- Password: Zaidi@123

### Doctor Account
- Email: doctortest@example.com
- Password: Zaidi@12345


## Testing

Run backend tests from the backend directory.

```powershell
python -m pytest -v
```

The backend test suite currently contains 19 test cases.

Latest test result:

- 19 tests passed
- 0 tests failed

## Security and Data Integrity

- Passwords are securely hashed using Argon2.
- JWT is used for user authentication.
- Role-based access control is implemented for doctors and patients.
- Database constraints help prevent duplicate bookings.
- Overlapping doctor availability slots are prevented.
- Appointment cancellation and rescheduling follow a two-hour restriction.
- Environment variables are stored in a private `.env` file.

## Database Schema

The database schema is documented in `ER_Diagram.md`.

It contains the following main tables:

1. Users
2. Doctors
3. Patients
4. Availability Slots
5. Appointments

The ER diagram shows primary keys, foreign keys, and relationships between the tables.

## Author

Ziyaur Rahman

## GitHub Repository

https://github.com/zeyaurmtp123-rgb/ClinicCare

# ClinicCare - Entity Relationship Diagram

This diagram shows the relationship between the main database tables.

## Database Tables

1. **Users** – Stores login details and user roles.
2. **Doctors** – Stores doctor information.
3. **Patients** – Stores patient information.
4. **AvailabilitySlots** – Stores available appointment slots for doctors.
5. **Appointments** – Stores patient appointments.

## ER Diagram

```mermaid
erDiagram
    USERS ||--o| DOCTORS : has
    USERS ||--o| PATIENTS : has
    DOCTORS ||--o{ AVAILABILITY_SLOTS : creates
    AVAILABILITY_SLOTS ||--o| APPOINTMENTS : booked_for
    PATIENTS ||--o{ APPOINTMENTS : books

    USERS {
        int user_id PK
        string name
        string email
        string hashed_password
        string role
    }

    DOCTORS {
        int doctor_id PK
        int user_id FK
        string name
        string specialization
    }

    PATIENTS {
        int patient_id PK
        int user_id FK
        string name
    }

    AVAILABILITY_SLOTS {
        int slot_id PK
        int doctor_id FK
        datetime start_time
        datetime end_time
    }

    APPOINTMENTS {
        int appointment_id PK
        int slot_id FK
        int patient_id FK
        string status
    }
```

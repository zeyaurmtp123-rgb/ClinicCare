
from datetime import datetime, timedelta


# HELPER 1: Register and login a doctor
def create_doctor_and_login(client, email, name):
    registration = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "DoctorTest@123",
            "role": "DOCTOR",
            "name": name,
            "specialization": "General"
        }
    )
    assert registration.status_code == 201, registration.text

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "DoctorTest@123"
        }
    )
    assert login.status_code == 200, login.text

    return {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }


# HELPER 2: Register and login a patient
def create_patient_and_login(client, email, name):
    registration = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "TestPassword@123",
            "role": "PATIENT",
            "name": name
        }
    )
    assert registration.status_code == 201, registration.text

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword@123"
        }
    )
    assert login.status_code == 200, login.text

    return {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }


# HELPER 3: Create a future availability slot
def create_slot(client, doctor_headers, hours_from_now):
    start_time = datetime.now() + timedelta(hours=hours_from_now)
    end_time = start_time + timedelta(minutes=30)

    response = client.post(
        "/availability/slots",
        headers=doctor_headers,
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )

    assert response.status_code == 201, response.text
    return response.json()["slot_id"]


# HELPER 4: Book a slot
def book_slot(client, patient_headers, slot_id):
    response = client.post(
        "/appointments/book",
        headers=patient_headers,
        json={"slot_id": slot_id}
    )

    assert response.status_code == 201, response.text
    return response.json()["appointment_id"]


# TEST 1: Prevent double booking
def test_patient_cannot_book_same_slot_twice(client):
    doctor_headers = create_doctor_and_login(
        client, "booking_doctor@example.com", "Booking Doctor"
    )
    slot_id = create_slot(client, doctor_headers, 48)

    patient_headers = create_patient_and_login(
        client, "booking_patient@example.com", "Booking Patient"
    )

    book_slot(client, patient_headers, slot_id)

    second_booking = client.post(
        "/appointments/book",
        headers=patient_headers,
        json={"slot_id": slot_id}
    )

    assert second_booking.status_code == 409


# TEST 2: Block cancellation within two hours
def test_patient_cannot_cancel_within_two_hours(client):
    doctor_headers = create_doctor_and_login(
        client, "cancel_doctor@example.com", "Cancel Doctor"
    )
    slot_id = create_slot(client, doctor_headers, 1)

    patient_headers = create_patient_and_login(
        client, "cancel_patient@example.com", "Cancel Patient"
    )

    appointment_id = book_slot(client, patient_headers, slot_id)

    cancellation = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=patient_headers
    )

    assert cancellation.status_code == 400, cancellation.text


# TEST 3: Allow cancellation more than two hours before
def test_patient_can_cancel_more_than_two_hours_before(client):
    doctor_headers = create_doctor_and_login(
        client, "free_cancel_doctor@example.com", "Free Cancel Doctor"
    )
    slot_id = create_slot(client, doctor_headers, 3)

    patient_headers = create_patient_and_login(
        client, "free_cancel_patient@example.com", "Free Cancel Patient"
    )

    appointment_id = book_slot(client, patient_headers, slot_id)

    cancellation = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=patient_headers
    )

    assert cancellation.status_code == 200, cancellation.text

    my_appointments = client.get(
        "/appointments/my",
        headers=patient_headers
    )

    assert my_appointments.status_code == 200

    appointment = next(
        item for item in my_appointments.json()
        if item["appointment_id"] == appointment_id
    )

    assert appointment["status"] == "CANCELLED"


# TEST 4: Allow another patient to book a cancelled slot
def test_cancelled_slot_can_be_booked_by_another_patient(client):
    doctor_headers = create_doctor_and_login(
        client, "reuse_doctor@example.com", "Reuse Doctor"
    )
    slot_id = create_slot(client, doctor_headers, 4)

    first_patient_headers = create_patient_and_login(
        client, "first_patient@example.com", "First Patient"
    )

    appointment_id = book_slot(
        client, first_patient_headers, slot_id
    )

    cancellation = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=first_patient_headers
    )

    assert cancellation.status_code == 200, cancellation.text

    second_patient_headers = create_patient_and_login(
        client, "second_patient@example.com", "Second Patient"
    )

    second_booking = client.post(
        "/appointments/book",
        headers=second_patient_headers,
        json={"slot_id": slot_id}
    )

    assert second_booking.status_code == 201, second_booking.text


# TEST 5: Allow patient to reschedule
def test_patient_can_reschedule_appointment(client):
    doctor_headers = create_doctor_and_login(
        client, "reschedule_doctor@example.com", "Reschedule Doctor"
    )

    old_slot_id = create_slot(client, doctor_headers, 48)
    new_slot_id = create_slot(client, doctor_headers, 72)

    patient_headers = create_patient_and_login(
        client, "reschedule_patient@example.com", "Reschedule Patient"
    )

    appointment_id = book_slot(
        client, patient_headers, old_slot_id
    )

    response = client.patch(
        f"/appointments/{appointment_id}/reschedule",
        headers=patient_headers,
        json={"new_slot_id": new_slot_id}
    )

    assert response.status_code == 200, response.text

    my_appointments = client.get(
        "/appointments/my",
        headers=patient_headers
    )

    assert my_appointments.status_code == 200

    appointment = next(
        item for item in my_appointments.json()
        if item["appointment_id"] == appointment_id
    )

    assert appointment["slot_id"] == new_slot_id
    assert appointment["status"] == "BOOKED"


# TEST 6: Prevent rescheduling to an already-booked slot
def test_patient_cannot_reschedule_to_booked_slot(client):
    doctor_headers = create_doctor_and_login(
        client, "conflict_doctor@example.com", "Conflict Doctor"
    )

    first_slot_id = create_slot(client, doctor_headers, 48)
    second_slot_id = create_slot(client, doctor_headers, 72)

    first_patient_headers = create_patient_and_login(
        client, "conflict_patient1@example.com", "Conflict Patient One"
    )

    book_slot(client, first_patient_headers, second_slot_id)

    second_patient_headers = create_patient_and_login(
        client, "conflict_patient2@example.com", "Conflict Patient Two"
    )

    appointment_id = book_slot(
        client, second_patient_headers, first_slot_id
    )

    response = client.patch(
        f"/appointments/{appointment_id}/reschedule",
        headers=second_patient_headers,
        json={"new_slot_id": second_slot_id}
    )

    assert response.status_code == 409, response.text

    my_appointments = client.get(
        "/appointments/my",
        headers=second_patient_headers
    )

    assert my_appointments.status_code == 200

    appointment = next(
        item for item in my_appointments.json()
        if item["appointment_id"] == appointment_id
    )

    assert appointment["slot_id"] == first_slot_id
    assert appointment["status"] == "BOOKED"


# TEST 7: Doctor can view and complete an appointment
def test_doctor_can_view_and_complete_appointment(client):
    doctor_headers = create_doctor_and_login(
        client, "manage_doctor@example.com", "Manage Doctor"
    )

    slot_id = create_slot(client, doctor_headers, 48)

    patient_headers = create_patient_and_login(
        client, "manage_patient@example.com", "Manage Patient"
    )

    appointment_id = book_slot(
        client, patient_headers, slot_id
    )

    doctor_appointments = client.get(
        "/appointments/doctor/my",
        headers=doctor_headers
    )

    assert doctor_appointments.status_code == 200
    assert any(
        item["appointment_id"] == appointment_id
        for item in doctor_appointments.json()
    )

    update_response = client.patch(
        f"/appointments/{appointment_id}/status",
        headers=doctor_headers,
        json={"status": "COMPLETED"}
    )

    assert update_response.status_code == 200, update_response.text

    updated_appointments = client.get(
        "/appointments/doctor/my",
        headers=doctor_headers
    )

    assert updated_appointments.status_code == 200

    appointment = next(
        item for item in updated_appointments.json()
        if item["appointment_id"] == appointment_id
    )

    assert appointment["status"] == "COMPLETED"


# TEST 8: Doctor cannot access another doctor's appointment
def test_doctor_cannot_access_another_doctors_appointment(client):
    doctor1_headers = create_doctor_and_login(
        client, "doctor_one@example.com", "Doctor One"
    )

    slot_id = create_slot(client, doctor1_headers, 48)

    patient_headers = create_patient_and_login(
        client, "security_patient@example.com", "Security Patient"
    )

    appointment_id = book_slot(
        client, patient_headers, slot_id
    )

    doctor2_headers = create_doctor_and_login(
        client, "doctor_two@example.com", "Doctor Two"
    )

    response = client.get(
        "/appointments/doctor/my",
        headers=doctor2_headers
    )

    assert response.status_code == 200
    assert all(
        item["appointment_id"] != appointment_id
        for item in response.json()
    )

    update_response = client.patch(
        f"/appointments/{appointment_id}/status",
        headers=doctor2_headers,
        json={"status": "COMPLETED"}
    )

    assert update_response.status_code == 404


# TEST 9: Doctor cannot create overlapping availability slots
def test_doctor_cannot_create_overlapping_slots(client):
    doctor_headers = create_doctor_and_login(
        client, "overlap_doctor@example.com", "Overlap Doctor"
    )

    start_time = datetime.now() + timedelta(hours=48)
    end_time = start_time + timedelta(minutes=30)

    first_slot = client.post(
        "/availability/slots",
        headers=doctor_headers,
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )

    assert first_slot.status_code == 201, first_slot.text

    overlapping_slot = client.post(
        "/availability/slots",
        headers=doctor_headers,
        json={
            "start_time": (
                start_time + timedelta(minutes=15)
            ).isoformat(),
            "end_time": (
                end_time + timedelta(minutes=15)
            ).isoformat()
        }
    )

    assert overlapping_slot.status_code == 409


# TEST 10: Doctor cannot delete a booked slot
def test_doctor_cannot_delete_booked_slot(client):
    doctor_headers = create_doctor_and_login(
        client, "delete_doctor@example.com", "Delete Doctor"
    )

    slot_id = create_slot(client, doctor_headers, 48)

    patient_headers = create_patient_and_login(
        client, "delete_patient@example.com", "Delete Patient"
    )

    book_slot(client, patient_headers, slot_id)

    response = client.delete(
        f"/availability/slots/{slot_id}",
        headers=doctor_headers
    )

    assert response.status_code == 409


# TEST 11: Doctor can delete an unused slot
def test_doctor_can_delete_free_slot(client):
    doctor_headers = create_doctor_and_login(
        client, "free_delete_doctor@example.com", "Free Delete Doctor"
    )

    slot_id = create_slot(client, doctor_headers, 48)

    response = client.delete(
        f"/availability/slots/{slot_id}",
        headers=doctor_headers
    )

    assert response.status_code == 200, response.text
    assert response.json()["slot_id"] == slot_id


# TEST 12: Patient can search doctors by specialization
def test_patient_can_search_doctors_by_specialization(client):
    doctor_headers = create_doctor_and_login(
        client, "search_doctor@example.com", "Search Doctor"
    )

    slot_id = create_slot(client, doctor_headers, 48)

    patient_headers = create_patient_and_login(
        client, "search_patient@example.com", "Search Patient"
    )

    search_date = (datetime.now() + timedelta(hours=48)).date()

    response = client.post(
        "/patients/search-doctors",
        headers=patient_headers,
        json={
            "specialization": "General",
            "appointment_date": search_date.isoformat()
        }
    )

    assert response.status_code == 200, response.text

    doctors = response.json()["doctors"]

    matching_doctor = next(
        doctor for doctor in doctors
        if doctor["name"] == "Search Doctor"
    )

    assert matching_doctor["specialization"] == "General"
    assert any(
        slot["slot_id"] == slot_id
        for slot in matching_doctor["available_slots"]
    )


# TEST 13: Doctor can view cancelled appointments in history
def test_doctor_can_view_cancelled_appointment(client):
    doctor_headers = create_doctor_and_login(
        client,
        "cancel_history_doctor@example.com",
        "Dr. History"
    )

    patient_headers = create_patient_and_login(
        client,
        "cancel_history_patient@example.com",
        "History Patient"
    )

    # Create a slot sufficiently far in the future
    slot_id = create_slot(client, doctor_headers, 72)

    # Patient books the slot
    appointment_id = book_slot(
        client, patient_headers, slot_id
    )

    # Patient cancels the appointment
    cancellation = client.patch(
        f"/appointments/{appointment_id}/cancel",
        headers=patient_headers
    )

    assert cancellation.status_code == 200, cancellation.text

    # Doctor views appointment history
    history_response = client.get(
        "/appointments/doctor/my?appointment_type=all",
        headers=doctor_headers
    )

    assert history_response.status_code == 200, history_response.text

    cancelled_appointments = [
        appointment
        for appointment in history_response.json()
        if appointment["appointment_id"] == appointment_id
    ]

    assert len(cancelled_appointments) == 1
    assert cancelled_appointments[0]["status"] == "CANCELLED"


# TEST 14: Upcoming appointments include future appointments today
def test_doctor_upcoming_includes_later_today_appointment(client):
    doctor_headers = create_doctor_and_login(
        client,
        "upcoming_today_doctor@example.com",
        "Upcoming Today Doctor"
    )

    patient_headers = create_patient_and_login(
        client,
        "upcoming_today_patient@example.com",
        "Upcoming Today Patient"
    )

    # Create an appointment one hour from now
    slot_id = create_slot(client, doctor_headers, 1)

    appointment_id = book_slot(
        client, patient_headers, slot_id
    )

    # Ask for upcoming appointments
    response = client.get(
        "/appointments/doctor/my?appointment_type=upcoming",
        headers=doctor_headers
    )

    assert response.status_code == 200, response.text

    upcoming_appointments = response.json()

    assert any(
        appointment["appointment_id"] == appointment_id
        for appointment in upcoming_appointments
    )


def test_patient_registration(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "pytest_patient@example.com",
            "password": "TestPassword@123",
            "role": "PATIENT",
            "name": "Pytest Patient"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Registration successful"


def test_patient_login(client):
    client.post(
        "/auth/register",
        json={
            "email": "login_patient@example.com",
            "password": "TestPassword@123",
            "role": "PATIENT",
            "name": "Login Patient"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login_patient@example.com",
            "password": "TestPassword@123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_doctor_registration_requires_specialization(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "doctor_missing_spec@example.com",
            "password": "TestPassword@123",
            "role": "DOCTOR",
            "name": "Dr. Missing"
        }
    )

    assert response.status_code == 422


def test_doctor_registration_saves_specialization(client):
    registration_response = client.post(
        "/auth/register",
        json={
            "email": "cardiology@example.com",
            "password": "TestPassword@123",
            "role": "DOCTOR",
            "name": "Dr. Sharma",
            "specialization": "Cardiology"
        }
    )

    assert registration_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "cardiology@example.com",
            "password": "TestPassword@123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    profile_response = client.get(
        "/doctors/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert profile_response.status_code == 200
    assert profile_response.json()["specialization"] == "Cardiology"

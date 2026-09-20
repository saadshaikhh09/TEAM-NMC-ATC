from uuid import UUID


DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def login_demo(client):
    response = client.post(
        "/auth/login", json={"email": "demo@atc.local", "password": "DemoPass!2026"}
    )
    assert response.status_code == 200
    return client

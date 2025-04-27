import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code == 302

def test_monitoring(client):
    c = client
    c.set_cookie("id", "3fdb239b-c661-4152-a895-1f8e3abfe4c4")
    response = c.get('/monitoring/')
    assert response.status_code == 200

def test_requests(client):
    c = client
    c.set_cookie("id", "3fdb239b-c661-4152-a895-1f8e3abfe4c4")
    response = c.get('/requests/')
    print(response.data)
    assert response.status_code == 200

def test_requests_creation(client):
    c = client
    c.set_cookie("id", "3fdb239b-c661-4152-a895-1f8e3abfe4c4")
    response = client.get('/requests/creation')
    assert response.status_code == 200

def test_processing(client):
    c = client
    c.set_cookie("id", "3fdb239b-c661-4152-a895-1f8e3abfe4c4")
    c.set_cookie("role", "scrypt:32768:8:1$UuJaPyXuPZtPpr1G$6d88847488ab5dc0e20cd8eef68ca96cc8f4962693f0f1a83ee068116536cda67f89e7ac8272534fdcbb8c3abc1dc7ad238a6ebf28f4771e3d5bdd52685224df")
    response = client.get('/processing/approval')
    assert response.status_code == 200

def test_passage_reports(client):
    c = client
    c.set_cookie("id", "3fdb239b-c661-4152-a895-1f8e3abfe4c4")
    c.set_cookie("role", "scrypt:32768:8:1$UuJaPyXuPZtPpr1G$6d88847488ab5dc0e20cd8eef68ca96cc8f4962693f0f1a83ee068116536cda67f89e7ac8272534fdcbb8c3abc1dc7ad238a6ebf28f4771e3d5bdd52685224df")
    response = client.get('/passages/')
    print(response.data)
    assert response.status_code == 200
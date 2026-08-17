import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .factories import MasterFactory, ServiceFactory
from .forms import ApplicationForm
from .models import Application
from datetime import date, time
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

def test_appointment_model_creation():
    master = MasterFactory()
    service = ServiceFactory()

    appointment = Application.objects.create(
        client_name="Роман",
        client_phone="+375291112233",
        master=master,
        service=service,
        appointment_date=date(2026, 8, 20),
        appointment_time=time(12, 0)
    )

    assert appointment.client_name == "Роман"
    assert Application.objects.count() == 1

def test_appointment_form_invalid():

    form_data = {
        "client_name": "Роман",
        "client_phone": "",
        "appointment_date": ""
    }
    form = ApplicationForm(data=form_data)
    assert form.is_valid() is False
    assert "client_phone" in form.errors

def test_homepage_view(client):
    url = reverse("index")
    response = client.get(url)
    assert response.status_code  == 200

def test_servises_api_list():
    client = APIClient()

    User = get_user_model()
    test_user = User.objects.create_user(username="test_api_client", password="password123")

    client.force_authenticate(user=test_user)   

    ServiceFactory(name="Педикюр")

    url = "/api/services/"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) >= 1


import pytest as pytest
from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth.models import User

from django.test import Client
from django.test import TestCase

from oauth_project.settings import INSTALLED_APPS




@pytest.mark.urls('oauth_project.urls')
def test_localhost(client):
  response = client.get('http://127.0.0.1:8000/')
  assert response.status_code == 200


def test_admin_url(client):
  response = client.get('http://127.0.0.1:8000/admin/')
  assert response['location'] == '/admin/login/?next=/admin/'

def test_logout_url(client):
  response = client.get('http://127.0.0.1:8000/logout')
  assert response['location'] == '/login/'


def test_admin_url(client):
  response = client.get('http://127.0.0.1:8000/register/')
  assert response.status_code == 200
@pytest.mark.django_db
def test_user_count():
    assert User.objects.count() == 0



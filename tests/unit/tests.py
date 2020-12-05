import pytest
import listjj
import os
import logging
from django.contrib.auth.models import User, Group
from app.models import *
from django.urls import reverse
from django.core.management import call_command

APP_PATH = os.path.dirname(listjj.__file__)
TEST_PATH = APP_PATH+'/../tests/unit'
logging.basicConfig(level=logging.INFO, filename=APP_PATH + 'logging.log')


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', TEST_PATH + '/fixture.json')

@pytest.mark.django_db
def test_user_create():
    User.objects.create_user('username', 'username@test.com', 'password')
    assert User.objects.count() == 2  # 1 created + one from fixture

@pytest.mark.django_db
def test_views_without_auth(client):
    url_names = ['login', 'register',]
    for url_name in url_names:
        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == 200

@pytest.mark.django_db
def test_superuser_has_no_access(admin_client):
    '''Superuser does not have access to page, because he does not belong to group'''
    url = reverse('index')
    response = admin_client.get(url)
    assert response.status_code == 403

@pytest.mark.django_db
def test_group_exists():
    '''Group should bo loaded from json fixtures'''
    group = Group.objects.get(pk=2)
    assert group.name == "accessGroup"  # from json fixture

@pytest.mark.django_db
def test_auth_views(client):
    user = User.objects.get(username="test_user")
    client.login(username=user.username, password='test_password')
    url_names = ['index', 'modify_categories',]
    for url_name in url_names:
        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == 200

@pytest.mark.django_db
def test_add_note(client):
    user = User.objects.get(username="test_user")
    client.login(username=user.username, password='test_password')
    url = reverse('add_note')
    data = {'value': 1, 'category': 33, 'description': 'test note'}
    response = client.post(url, data=data, headers={})

    journal = Journal.objects.filter(login=user)[0]
    assert journal.login.username == 'test_user'
    assert journal.description == 'test note'
    assert journal.value == 1.0
    assert journal.category.category == 'test_category'

    assert response.status_code == 200
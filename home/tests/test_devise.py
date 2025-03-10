from django.test import TestCase
from django.test import Client

from django.urls.base import reverse

from django.contrib.auth import get_user_model
User = get_user_model()

USER_NAME = "test"
PASSWD = "test"
EMAIL = "test@domain.net"

class DeviseTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username=USER_NAME, password=PASSWD, email=EMAIL)

    def test_set_devise(self):
        self.client.get(reverse('index'))
        for devise in ('TND', 'EUR', 'USD', 'GBP'):
            response = self.client.post(reverse('set_devise'), {'devise': devise, 'next': reverse('index')})
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('index'))


    def test_set_devise_without_next(self):
        self.client.get(reverse('index'))
        response = self.client.post(reverse('set_devise'), {'devise': 'TND', 'next': ''})
        self.assertEqual(response.status_code, 404)

    def test_set_devise_notfound(self):
        self.client.get(reverse('index'))
        response = self.client.post(reverse('set_devise'), {'devise': 'NZD', 'next': reverse('index')})
        self.assertEqual(response.status_code, 404)


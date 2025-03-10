from django.test import TestCase
from django.test import Client

from django.urls.base import reverse

from django.contrib.auth import get_user_model
User = get_user_model()

USER_NAME = "test"
PASSWD = "test"
EMAIL = "test@domain.net"

class LanguageTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username=USER_NAME, password=PASSWD, email=EMAIL)

    def test_set_language_ar(self):
        self.client.get(reverse('index'))
        response = self.client.post(reverse('set_language'), {'language': 'ar', 'next': reverse('index')})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        str_cookie = "Set-Cookie: django_language=%s; Path=/" % 'ar'
        self.assertEqual(str(self.client.cookies['django_language']), str_cookie)

    def test_set_language_fr(self):
        self.client.get(reverse('index'))
        response = self.client.post(reverse('set_language'), {'language': 'fr', 'next': reverse('index')})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        str_cookie = "Set-Cookie: django_language=%s; Path=/" % 'fr'
        self.assertEqual(str(self.client.cookies['django_language']), str_cookie)

    def test_set_language_en(self):
        self.client.get(reverse('index'))
        response = self.client.post(reverse('set_language'), {'language': 'en', 'next': reverse('index')})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        str_cookie = "Set-Cookie: django_language=%s; Path=/" % 'en'
        self.assertEqual(str(self.client.cookies['django_language']), str_cookie)

    def test_set_language_not_found(self):
        self.client.get(reverse('index'))
        response = self.client.post(reverse('set_language'), {'language': 'de', 'next': reverse('index')})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        str_cookie = "Set-Cookie: django_language=de; Path=/"
        self.assertEqual(str(self.client.cookies['django_language']), str_cookie)


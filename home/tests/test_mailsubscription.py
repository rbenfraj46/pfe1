from django.test import TestCase
from django.test import Client

from django.urls.base import reverse

from django.contrib.auth import get_user_model

from home.models import MailSubscription

User = get_user_model()

USER_NAME = "test"
PASSWD = "test"
EMAIL = "test@domain.net"

class MailSubscriptionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username=USER_NAME, password=PASSWD,
                                 email=EMAIL, is_active=True,
                                 is_mail_verified=True)

    def test_subscribe(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response,
                            "Newsletter Signup",
                            status_code=200)
        response = self.client.post(reverse('newsletter'), {})

        self.assertEqual(response.url, reverse('login')[1:] + '?next=' + reverse('newsletter'))
        self.client.get(reverse('login'))
        self.client.post(reverse('login'), {'username': USER_NAME, 'password': PASSWD})
        response = self.client.get(reverse('index'))
        self.assertContains(response,
                            "Newsletter Signup",
                            status_code=200)

        response = self.client.post(reverse('newsletter'), {})
        print('respense: ', response.content)
        self.assertNotContains(response,
                               "Newsletter Signup",
                               status_code=302)
        self.assertEqual(response.url, reverse('index'))


    def test_subscription_whith_login(self):
        sub = MailSubscription.objects.filter(user=self.user).count()
        self.assertEqual(sub, 0)
        self.client.post(reverse('login'), {'username': USER_NAME, 'password': PASSWD})
        response = self.client.get(reverse('index'))
        self.assertContains(response,
                            "Newsletter Signup",
                            status_code=200)
        response = self.client.post(reverse('newsletter'), {})

        self.assertNotContains(response,
                            "Newsletter Signup",
                            status_code=302)
        self.assertEqual(response.url, reverse('index'))
        sub = MailSubscription.objects.filter(user=self.user).count()
        self.assertEqual(sub, 1)

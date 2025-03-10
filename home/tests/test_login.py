from django.test import TestCase
from django.test import Client

from django.test.client import RequestFactory
from django.urls.base import reverse
from django.core import mail
from django.conf import settings

from faker import Faker

from django.contrib.auth import get_user_model
User = get_user_model()

USER_NAME = "test"
PASSWD = "test"
EMAIL = "test@domain.net"

class LoginTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        User.objects.create_user(username=USER_NAME, password=PASSWD, email=EMAIL)

    def test_login_success_email_not_verified(self):
        """test sucess login"""
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        payload = {
            'username': USER_NAME,
            'password': PASSWD
            }
        request = c.post(reverse('login'), payload)
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, reverse('mail_not_confirmed'))

    def test_login_success_different_case(self):
        """test sucess login"""
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        payload = {
            'username': USER_NAME.upper(),
            'password': PASSWD
            }
        response = c.post(reverse('login'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail_not_confirmed'))
        c.post(reverse('logout'))
        payload = {
            'username': USER_NAME,
            'password': PASSWD
            }
        response = c.post(reverse('login'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail_not_confirmed'))

    def test_login_success_with_email(self):
        """test sucess login"""
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        payload = {
            'username': EMAIL,
            'password': PASSWD
            }
        response = c.post(reverse('login'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail_not_confirmed'))


    def test_login_fail(self):
        """test sucess login"""
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        payload = {
            'username': USER_NAME,
            'password': "errror_passwd"
            }
        request = c.post(reverse('login'), payload)
        self.assertEqual(request.status_code, 200)


    def test_login_captcha(self):
        """test sucess login"""
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        payload = {
            'username': USER_NAME,
            'password': "errror_passwd"
            }
        for i in range(2):
            response = c.post(reverse('login'), payload)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'name="captcha_1"', status_code=200)
        response = c.post(reverse('login'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="captcha_1"', status_code=200)

    def test_login_success_resend_email_verified(self):
        """test sucess login"""
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        payload = {
            'username': USER_NAME,
            'password': PASSWD
            }
        request = c.post(reverse('login'), payload)
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, reverse('mail_not_confirmed'))


class ChangePasswordTestCase(TestCase):
    fake = Faker()

    def setUp(self):
        self.TEST_PASSWORD = self.fake.password()
        self.TEST_USERNAME = self.fake.user_name()
        user = User.objects.create_user(username=self.TEST_USERNAME, password=self.TEST_PASSWORD)
        user.is_mail_verified = True
        user.save()

    def test_change_password_success(self):
        c = Client()
        c.get(reverse('login'))
        request = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        new_pass = self.fake.password()
        response = c.post(reverse('password_change'),
                         {'old_password': self.TEST_PASSWORD,
                          'new_password1': new_pass,
                          'new_password2': new_pass})
        print(response.content)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('password_change_done'))
        c.get(reverse('logout'))
        c.get(reverse('login'))
        request = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': new_pass})
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, settings.LOGIN_REDIRECT_URL)


    def test_change_password_fail_old_error(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        new_pass = self.fake.password()
        response = c.post(reverse('password_change'),
                         {'old_password': self.fake.password(),
                          'new_password1': new_pass,
                          'new_password2': new_pass})
        print(response.content)
        self.assertContains(response,
                            'Your old password was entered incorrectly. Please enter it again.',
                            status_code=200)

    def test_change_password_fail_numeric_passwd(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        new_pass = self.fake.random_number(8)
        response = c.post(reverse('password_change'),
                         {'old_password': self.TEST_PASSWORD,
                          'new_password1': new_pass,
                          'new_password2': new_pass})
        print(response.content)
        self.assertContains(response,
                            'This password is entirely numeric.',
                            status_code=200)

    def test_change_password_fail_short_passwd(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        new_pass = ''.join(self.fake.random_letters(4))
        response = c.post(reverse('password_change'),
                         {'old_password': self.TEST_PASSWORD,
                          'new_password1': new_pass,
                          'new_password2': new_pass})
        print(response.content)
        self.assertContains(response,
                            'This password is too short. It must contain at least 8 characters.',
                            status_code=200)

    def test_change_password_fail_short_common(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        new_pass = 'azerty123'
        response = c.post(reverse('password_change'),
                         {'old_password': self.TEST_PASSWORD,
                          'new_password1': new_pass,
                          'new_password2': new_pass})
        print(response.content)
        self.assertContains(response,
                            'This password is too common.',
                            status_code=200)

    def test_change_password_fail_missmatch(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        response = c.post(reverse('password_change'),
                         {'old_password': self.TEST_PASSWORD,
                          'new_password1': self.fake.password(),
                          'new_password2': self.fake.password()})
        print(response.content)
        self.assertContains(response,
                            "The two password fields didn",
                            status_code=200)

    def test_change_password_fail_like_username(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('password_change'))
        new_pass = self.TEST_USERNAME + str(self.fake.random_int(4))
        response = c.post(reverse('password_change'),
                         {'old_password': self.TEST_PASSWORD,
                          'new_password1': new_pass,
                          'new_password2': new_pass})
        print(response.content)
        self.assertContains(response,
                            "The password is too similar to the username.",
                            status_code=200)


    def test_login_page_after_get_logged(self):
        c = Client()
        c.get(reverse('login'))
        response = c.post(reverse('login'), {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
        c.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)


    def test_login_page_after_next(self):
        c = Client()
        response = c.get(reverse('agences'))
        self.assertEqual(response.status_code, 302)
        redirect_link = reverse('login')+"?next="+reverse('agences')
        self.assertEqual("/"+response.url, redirect_link)
        response = c.post(redirect_link, {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('agences'))


    def test_login_page_after_next_extern(self):
        c = Client()
        redirect_link = reverse('login')+"?next="+"http://example.com/"
        response = c.post(redirect_link, {'username': self.TEST_USERNAME, 'password': self.TEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)




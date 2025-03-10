import time
from django.conf import settings
from django.urls.base import reverse

from django.test import TestCase
from django.test import Client
from django.test.client import RequestFactory
from django.core import mail

from faker import Faker

from django.contrib.auth import get_user_model
User = get_user_model()

USER_NAME = "TeSt"
PASSWD = "test"

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        User.objects.create_user(username=USER_NAME, password=PASSWD)
        settings.SEND_CONFIRMATION_MAIL = True

    def test_registration_success(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('registration'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        passwd = fake.password()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }
        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

    def test_registration_fail_on_missing_field(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        passwd = fake.password()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }
        for key, value in payload.items():
            missed_data = {}
            for kkey in payload.keys():
                if key == kkey:
                    continue
                missed_data[kkey] = payload[kkey]

            response = c.post(reverse('registration'), missed_data)
            self.assertEqual(response.status_code, 200)
            #self.assertEqual(response.url, reverse('index'))

    def test_registration_fail_on_empty_field(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('login'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        passwd = fake.password()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }
        for key, value in payload.items():
            missed_data = {}
            for kkey in payload.keys():
                if key == kkey:
                    missed_data[kkey] = ""
                    continue
                missed_data[kkey] = payload[kkey]

            response = c.post(reverse('registration'), missed_data)
            self.assertEqual(response.status_code, 200)
            #self.assertEqual(response.url, reverse('index'))

    def test_registration_fail_on_diff_passwd_field(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('login'))

        payload = {
            'username': fake.user_name(),
            'password1': fake.password(),
            'password2': fake.password(),
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }

        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.url, reverse('index'))

    def test_registration_fail_on_error_mail_field(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('login'))
        passwd = fake.password()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.last_name(),
            'accept_term': 'on'
            }

        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.url, reverse('index'))


    def test_registration_fail_on_duplicate_mail_field(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('login'))
        passwd = fake.password()
        email = fake.email()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': email,
            'accept_term': 'on'
            }

        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        payload['username'] = fake.user_name()

        c.get(reverse('login'))
        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.url, reverse('index'))

    def test_registration_fail_on_duplicate_username_field(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('login'))
        passwd = fake.password()

        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }

        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

        payload['email'] = fake.email()
        c.get(reverse('login'))
        response = c.post(reverse('registration'), payload)
        self.assertEqual(response.status_code, 200)
        #self.assertEqual(response.url, reverse('index'))

    def test_registration_validate_mail_and_login(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('registration'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        passwd = fake.password()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }
        response = self.client.post(reverse('registration'), payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        # mail testing
        #time.sleep(3)
        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]
        body = sent_mail.body
        self.assertEqual(sent_mail.from_email, settings.NO_REPLY_EMAIL_ADRESS)
        self.assertEqual(sent_mail.to, [payload['email']])
        self.assertEqual(sent_mail.subject, 'Activate your account.')
        self.assertTrue("Please click on the link to confirm your registration," in sent_mail.body)
        link = ''
        # test that login doesnt pass until we verify the mail.
        payload_login = {'username': payload['username'], 'password': payload['password1']}
        response = c.post(reverse('login'), payload_login)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail_not_confirmed'))

        for line in body.split('\n'):
            if 'http://testserver' in line:
                link = line
                break
        self.client.get(link)
        response = c.post(reverse('login'), payload_login)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)


    def test_registration_validate_resend_mail_and_login(self):
        """test sucess login"""
        fake = Faker()
        c = Client()
        c.get(reverse('registration'))
        #c.login(request=None, username=USER_NAME, password=PASSWD)
        passwd = fake.password()
        payload = {
            'username': fake.user_name(),
            'password1': passwd,
            'password2': passwd,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'accept_term': 'on'
            }
        response = self.client.post(reverse('registration'), payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

        # test that login doesnt pass until we verify the mail.
        payload_login = {'username': payload['username'], 'password': payload['password1']}
        response = c.post(reverse('login'), payload_login)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail_not_confirmed'))


        nbr_mail = 1
        #check that inbox is empty
        self.assertEqual(len(mail.outbox), nbr_mail)

        c.get(reverse('mail_not_confirmed'))
        response = c.post(reverse('mail_not_confirmed'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

        # check confirmation mail is sent
        self.assertEqual(len(mail.outbox), nbr_mail + 1)
        sent_mail = mail.outbox[nbr_mail]
        body = sent_mail.body
        self.assertEqual(sent_mail.from_email, settings.NO_REPLY_EMAIL_ADRESS)
        self.assertEqual(sent_mail.to, [payload['email']])
        self.assertEqual(sent_mail.subject, 'Activate your account.')
        self.assertTrue("Please click on the link to confirm your registration," in sent_mail.body)
        link = ''

        payload = payload_login
        # test that login doesnt pass until we verify the mail.
        response = c.post(reverse('login'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('mail_not_confirmed'))

        for line in body.split('\n'):
            if 'http://testserver' in line:
                link = line
                break
        self.client.get(link)
        response = c.post(reverse('login'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)



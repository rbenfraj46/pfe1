import os
import sys
import json
import logging

from io import StringIO
from django.utils import timezone

from django.core.management import call_command
from django.test import TestCase
from django.conf import settings
from unittest import mock
from unittest.mock import patch
import responses

from home.models import Devise



currency_json = ''.join(open(os.path.dirname(os.path.realpath(__file__)) + "/fixtures/currencies.json").readlines())

URL= "https://freecurrencyapi.net/api/v2/latest?apikey=%s&base_currency=%s" % (settings.FREECURRENCYAPI_TOKEN, settings.DEFAULT_CURRENCY)

main_logger = logging.getLogger("")

class SyncCurrencyCommand(TestCase):
    SIMULATION_MSG = "This is only simulation. Database will not be affected."

    def call_command(self, *args, **kwargs):
        out = StringIO()
        _stderr = StringIO()
        sys.stdout = out
        sys.stderr = _stderr
        call_command(
            "sync_currency",
            *args,
            stdout=out,
            stderr=_stderr,
            **kwargs,
        )
        return out.getvalue() + _stderr.getvalue()

    @responses.activate
    def test_dry_run_200(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command("--dry")
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertIn(self.SIMULATION_MSG, out)
        self.assertIn("This is dry mode: in store mode Currency EUR will be updated with value", out)

    @responses.activate
    def test_dry_run_404(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=404))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command("--dry")
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertIn(self.SIMULATION_MSG, out)
        self.assertIn(" Could not retrieve currency USD", out)

    @responses.activate
    def test_dry_run_USD(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command(["--dry", "--currency", "USD"])
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertIn(self.SIMULATION_MSG, out)
        self.assertIn("This is dry mode: in store mode Currency USD will be updated with value", out)
        self.assertNotIn("This is dry mode: in store mode Currency EUR will be updated with value", out)


    @responses.activate
    def test_dry_run_ALL(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command(["--dry", "--currency", "all"])
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertIn(self.SIMULATION_MSG, out)
        self.assertIn("This is dry mode: in store mode Currency USD will be updated with value", out)
        self.assertIn("This is dry mode: in store mode Currency EUR will be updated with value", out)
        self.assertIn("In store mode Inactive Currency TND with value 1 will be updated", out)
        self.assertIn("In store mode Missing Currency JPY with value 39.597489 will be added as inactive", out)


    @responses.activate
    def test_run_404(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=404))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertIn(" Could not retrieve currency USD", out)


    @responses.activate
    def test_run_200(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 3)
        self.assertIn("Update Currency USD with value" , out)
        self.assertIn("Update Currency EUR with value", out)

    @responses.activate
    def test_run_USD(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        out = self.call_command(["--currency", "USD"])
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 1)
        self.assertIn("Update Currency USD with value", out)
        self.assertNotIn("Update Currency EUR with value", out)

    @responses.activate
    #@mock.patch('sys.stderr', ret_value=StringIO())
    def test_run_NoCurrency(self):
        out = ''
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        with patch('sys.stdout', new=StringIO()) as capture_out:
            with patch('sys.stderr', new=StringIO()) as capture:
                with patch.object(main_logger , "error") as mock_log2:
                    with self.assertRaises(SystemExit) as cm:
                        self.call_command(["--currency", "USDZZ"])
        out = capture.getvalue() + capture_out.getvalue()
        self.assertEqual(cm.exception.code, 1)
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertNotIn("Update Currency USD with value", out)
        mock_log2.assert_called_once_with('No such currency "USDZZ"')


    @responses.activate
    def test_run_ALL(self):
        responses.add(
            responses.Response(method='GET',url=URL,
                               json=json.loads(currency_json),
                               status=200))

        before_command = timezone.now()
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 0)
        self.assertEqual(len(Devise.objects.filter(is_active=True)), 4)
        out = self.call_command(["--currency", "all"])
        currencies = Devise.objects.filter(last_updated__gte=before_command)
        self.assertEqual(len(currencies), 140)
        self.assertEqual(len(Devise.objects.filter(is_active=True)), 4)

        self.assertIn("Update Currency USD with value" , out)
        self.assertIn("Update Currency EUR with value", out)

        self.assertIn("Add missing Currency JPY with value 39.597489 as inactive", out)
        self.assertIn("Add missing Currency IDR with value 4943.403666 as inactive", out)

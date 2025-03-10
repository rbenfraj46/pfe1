from django import forms
from django.forms.fields import EmailField
from django.utils.translation import gettext_lazy as _

from home.models import Devise

from utils import lazy_discover_foreign_id_choices


class DeviseForm(forms.Form):

    devise = forms.CharField(max_length=255, required=True, label=_('Devise'),
                             widget=forms.Select(
                                 choices=lazy_discover_foreign_id_choices(Devise, is_active=True)))
    next = forms.CharField(max_length=4096, required=True, label=_('Next'))

class NewsLetterSubscription(forms.Form):
    email = EmailField(max_length=255, required=False, label=_('Email'))

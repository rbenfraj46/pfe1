from django import forms
from captcha.fields import CaptchaField
from django.forms.fields import CharField
from django.forms.fields import EmailField

from django.utils.translation import gettext_lazy as _


class AxesLoginForm(forms.Form):
    username = CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class AxesLoginCaptchaForm(AxesLoginForm):
    captcha = CaptchaField()


class ResetPasswordForm(forms.Form):

    email = EmailField(max_length=255, required=True, label=_('Email'))

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {'required': _('The field ') + field.label + _(' is required')}

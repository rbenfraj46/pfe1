from django.forms.fields import CharField
from django.forms.fields import EmailField
from django.forms.fields import BooleanField
from django.contrib.auth.forms import UserCreationForm

from django.utils.translation import gettext_lazy as _


from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(UserCreationForm):
    error_css_class = 'registration_error'

    username = CharField(max_length=150, required=True, label=_('Username'))
    accept_term = BooleanField(required=True, label=_('Accept Terms'))
    email = EmailField(max_length=255, required=True, label=_('Email'))
    first_name = CharField(max_length=150, required=True, label=_('First Name'))
    last_name = CharField(max_length=150, required=True, label=_('Last Name'))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {'required': _('The field ') + field.label + _(' is required')}

    def save(self, commit=True):
        user = super().save(commit=False)

        user.is_active = True
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user

    class Meta(UserCreationForm.Meta):
        model = User
        # fields = ("username",)
        # field_classes = {'username': UsernameField}

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            msg = _("This email is already in use.")
            self.add_error('email', msg)
        return email.lower()

    def clean_username(self):
        return self.cleaned_data.get("username").lower()

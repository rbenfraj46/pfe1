from django import forms
from django.forms.fields import CharField
from django.forms.fields import EmailField
from django.forms.fields import BooleanField
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import fromstr

from home.models import Agences

User = get_user_model()


class AgencesForm(forms.ModelForm):
    accept_term = BooleanField(required=True, label=_('Accept Terms'))
    lon = CharField(required=False, label="")
    lat = CharField(required=False, label="")

    class Meta:
        model = Agences
        fields = "__all__"
        exclude = ["creator", "creation_date", "update_date", "is_mail_verified", "is_active", "location"]

    def __init__(self, *args, **kwargs):
        super(AgencesForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages = {'required': _('The field ') + field.label + _(' is required')}

    def save(self, commit=True):
        agences = super().save(commit=False)
        if not agences.location and self.data.get('lon', '') and self.data.get('lat', ''):
            latitude = self.data.get('lat', '')
            longitude = self.data.get('lon', '')
            agences.location = fromstr(
                    f'POINT({longitude} {latitude})', srid=4326
                )
        agences.is_mail_verified = False
        agences.is_active = False
        if commit:
            agences.save()
        return agences


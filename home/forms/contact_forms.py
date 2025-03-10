from django import forms
from django.utils.translation import gettext_lazy as _

from home.models import Contact


class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'
        exclude = ['is_read', 'user', 'created', 'updated']

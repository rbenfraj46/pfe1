from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cars.models import CarModel, Brand, AgencyCar
from django.conf import settings
import re


class PictureWidget(forms.widgets.Widget):
    def render(self, name, value, *args, attrs=None, **kwargs):
        return mark_safe("""<img src="%s" alt=""/>""" % value)


class CarModelAdminForm(forms.ModelForm):
    image = forms.ImageField(widget=PictureWidget, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs['instance']
        self.initial['image'] = get_image_link(instance)


    class Meta:
        model = CarModel
        fields = [f.name for f in CarModel._meta.fields]
        fields.remove('created')
        fields.remove('updated')
        fields.append('image')


class BrandAdminForm(forms.ModelForm):
    image = forms.ImageField(widget=PictureWidget, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs['instance']
        self.initial['image'] = get_image_link(instance)


    class Meta:
        model = Brand
        fields = [f.name for f in Brand._meta.fields]
        fields.append('image')


def get_image_link(instance):
    if getattr(instance, 'brand', ''):
        brand = instance.brand.name
    else:
        brand = ''

    path = settings.MEDIA_URL + settings.CAR_DOWNLOAD_FOLDER + brand
    path = path + "/%s" % instance.img_hash

    return path.replace('//', '/')


class AgencyCarForm(forms.ModelForm):
    class Meta:
        model = AgencyCar
        fields = [
            'brand', 'car_model', 'gear_type', 'image', 'fuel_policy',
            'security_deposit', 'minimum_license_age', 'price_per_day',
            'available', 'with_driver', 'driver_name', 'driver_phone',
            'driver_license_number', 'driver_experience_years', 'driver_languages'
        ]
        widgets = {
            'driver_languages': forms.TextInput(attrs={'placeholder': _('Ex: French, English, Arabic')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs du chauffeur conditionnels
        self.fields['driver_name'].required = False
        self.fields['driver_phone'].required = False
        self.fields['driver_license_number'].required = False
        self.fields['driver_experience_years'].required = False
        self.fields['driver_languages'].required = False

    def clean(self):
        cleaned_data = super().clean()
        with_driver = cleaned_data.get('with_driver')
        
        if with_driver:
            # Valider les champs obligatoires pour une voiture avec chauffeur
            required_fields = ['driver_name', 'driver_phone', 'driver_license_number', 'driver_experience_years']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, _('This field is required for cars with driver'))
            
            # Valider l'expérience minimale du chauffeur
            experience_years = cleaned_data.get('driver_experience_years')
            if experience_years is not None and experience_years < 1:
                self.add_error('driver_experience_years', _('Driver must have at least 1 year of experience'))

        return cleaned_data



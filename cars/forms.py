from django import forms
from django.utils.safestring import mark_safe

from cars.models import CarModel
from cars.models import Brand
from django.conf import settings


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



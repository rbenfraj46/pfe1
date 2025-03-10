from django.contrib import admin

from cars.models import Brand
from cars.models import GearType
from cars.models import CarModel
from cars.models import Transmission

from cars.forms import CarModelAdminForm
from cars.forms import BrandAdminForm
# Register your models here.


class BrandAdmin(admin.ModelAdmin):
    form = BrandAdminForm
    model = Brand
    list_display = [f.name for f in Brand._meta.fields]
admin.site.register(Brand, BrandAdmin)


class GearTypeAdmin(admin.ModelAdmin):
    model = GearType
    list_display = [f.name for f in GearType._meta.fields]
admin.site.register(GearType, GearTypeAdmin)


class TransmissionAdmin(admin.ModelAdmin):
    model = Transmission
    list_display = [f.name for f in Transmission._meta.fields]
admin.site.register(Transmission, TransmissionAdmin)


class CarAdmin(admin.ModelAdmin):
    form = CarModelAdminForm
    model = CarModel
    list_display = [f.name for f in CarModel._meta.fields]
admin.site.register(CarModel, CarAdmin)




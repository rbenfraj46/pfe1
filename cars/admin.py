from django.contrib import admin

from cars.models import Brand
from cars.models import GearType
from cars.models import CarModel
from cars.models import Transmission
from cars.models import AgencyCar   
from cars.models import CarUnavailability
from cars.forms import CarModelAdminForm
from cars.forms import BrandAdminForm
from .models import CarModelRequest


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


class AgencyCarAdmin(admin.ModelAdmin):
    list_display = [f.name for f in AgencyCar._meta.fields]

admin.site.register(AgencyCar, AgencyCarAdmin)


@admin.register(CarUnavailability)
class CarUnavailabilityAdmin(admin.ModelAdmin):
    list_display = ('car', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('car__brand__name', 'car__car_model__name')


@admin.register(CarModelRequest)
class CarModelRequestAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'model_name', 'status', 'requested_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('brand_name', 'model_name', 'requested_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'approved':
            brand, _ = Brand.objects.get_or_create(
                name=obj.brand_name,
                defaults={'is_active': True}
            )
            CarModel.objects.create(
                name=obj.model_name,
                description=obj.description,
                brand=brand,
                is_active=True
            )
        super().save_model(request, obj, form, change)




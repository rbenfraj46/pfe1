from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.db import transaction

from cars.models import Brand, GearType, CarModel, Transmission, AgencyCar, CarUnavailability
from cars.forms import CarModelAdminForm, BrandAdminForm
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

    class Media:
        js = [static('admin/js/confirm_approval.js')]
        css = {
            'all': [static('admin/css/confirm_approval.css')]
        }

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'approved':
            # Sauvegarder d'abord le statut
            super().save_model(request, obj, form, change)
            
            if not request.POST.get('confirm_approval'):
                self.message_user(
                    request,
                    mark_safe(
                        '<div class="popup">'
                        '<p>Make sure you have added the new car model</p>'
                        '<form method="POST" id="confirmation-form">'
                        '<input type="hidden" name="confirm_approval" value="true">'
                        f'<input type="hidden" name="object_id" value="{obj.id}">'
                        '<button type="submit" id="confirm-approval-btn">Confirm</button>'
                        '</form>'
                        '</div>'
                    ),
                    level='warning'
                )
                return
            
            try:
                with transaction.atomic():
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
                    self.message_user(request, 'Car model created successfully')
            except Exception as e:
                self.message_user(request, f'Error creating car model: {str(e)}', level='error')
        else:
            super().save_model(request, obj, form, change)




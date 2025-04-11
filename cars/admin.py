from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
import logging

from cars.models import (
    Brand, GearType, CarModel, Transmission, 
    AgencyCar, CarUnavailability, CarModelRequest,
    CarReservation
)
from cars.forms import CarModelAdminForm, BrandAdminForm

logger = logging.getLogger(__name__)

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

@admin.register(CarReservation)
class CarReservationAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'start_date', 'end_date', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'start_date')
    search_fields = ('car__brand__name', 'car__car_model__name', 'user__username', 'user__email')
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_obj = CarReservation.objects.get(pk=obj.pk)
            old_status = old_obj.status
            
        super().save_model(request, obj, form, change)
        
        # Envoi des notifications si le statut a changé
        if change and old_status != obj.status:
            if obj.status == 'approved':
                subject = _('Your car rental request has been approved')
                message = _('''Your rental request has been approved:
                    Car: {car}
                    From: {start}
                    To: {end}
                    Total Price: {price}
                    
                    Please proceed with the payment of the security deposit to confirm your reservation.
                ''').format(
                    car=obj.car,
                    start=obj.start_date,
                    end=obj.end_date,
                    price=obj.total_price
                )
            elif obj.status == 'rejected':
                subject = _('Your car rental request has been rejected')
                message = _('''Unfortunately, your rental request has been rejected:
                    Car: {car}
                    From: {start}
                    To: {end}
                    
                    Reason: {reason}
                    
                    Please feel free to try another date or contact us for more information.
                ''').format(
                    car=obj.car,
                    start=obj.start_date,
                    end=obj.end_date,
                    reason=obj.rejection_reason or _('No specific reason provided')
                )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.user.email],
                    fail_silently=True
                )
            except Exception as e:
                messages.error(request, _('Failed to send notification email to customer'))
                logger.error(f"Failed to send email to customer: {str(e)}")
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['approved', 'rejected', 'cancelled']:
            return self.readonly_fields + ('car', 'user', 'start_date', 'end_date', 'total_price')
        return self.readonly_fields




from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.db import transaction
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
import logging

from cars.models import (
    Brand, GearType, CarModel, Transmission, 
    AgencyCar, CarUnavailability, CarModelRequest,
    CarReservation, TransferBooking
)
from cars.forms import CarModelAdminForm, BrandAdminForm

logger = logging.getLogger(__name__)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    form = BrandAdminForm
    list_display = ('name', 'description', 'is_active', 'order_key', 'get_image')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order_key', 'name')
    list_editable = ('is_active', 'order_key')
    
    def get_image(self, obj):
        if obj.img_hash and obj.img_extension:
            return format_html('<img src="/media/{}.{}" style="max-height: 50px;" />', 
                             obj.img_hash, obj.img_extension)
        return "-"
    get_image.short_description = _("Logo")

@admin.register(GearType)
class GearTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order_key')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order_key', 'name')
    list_editable = ('is_active', 'order_key')

@admin.register(Transmission)
class TransmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'order_key')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order_key', 'name')
    list_editable = ('is_active', 'order_key')

@admin.register(CarModel)
class CarAdmin(admin.ModelAdmin):
    form = CarModelAdminForm
    list_display = ('name', 'brand', 'category', 'energy', 'gear_type', 'transmission', 'is_active')
    list_filter = ('is_active', 'brand', 'category', 'energy', 'gear_type', 'transmission')
    search_fields = ('name', 'brand__name', 'description')
    ordering = ('brand', 'name')
    list_editable = ('is_active',)
    readonly_fields = ('created', 'updated')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'brand', 'is_active', ('img_hash', 'img_extension'))
        }),
        (_('Technical Details'), {
            'fields': (
                'category',
                ('cylinder', 'horse_power'),
                ('doors_nbr', 'place_nbr'),
                'energy',
                ('gear_type', 'gear_nbr', 'transmission'),
                'max_speed'
            )
        }),
        (_('Consumption'), {
            'fields': ('urban_consumption', 'extra_urban_consumption', 'mixte_consumption')
        }),
        (_('Dimensions'), {
            'fields': ('length', 'width', 'height', 'trunk_volume')
        }),
        (_('Other'), {
            'fields': ('air_conditioner', 'order_key', 'created', 'updated')
        })
    )

@admin.register(AgencyCar)
class AgencyCarAdmin(admin.ModelAdmin):
    list_display = ('get_car_info', 'agence', 'price_per_day', 'is_active', 'available', 'with_driver', 'for_transfer', 'get_driver_info', 'get_transfer_info', 'get_car_image')
    list_filter = ('is_active', 'available', 'with_driver', 'for_transfer', 'agence', 'brand', 'gear_type')
    search_fields = ('brand__name', 'car_model__name', 'agence__agency_name', 'driver_name', 'driver_phone')
    ordering = ('-created',)
    list_editable = ('is_active', 'available', 'price_per_day')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('agence', 'brand', 'car_model', 'gear_type', 'image')
        }),
        (_('Pricing and Availability'), {
            'fields': ('price_per_day', 'security_deposit', 'minimum_license_age', 'fuel_policy', 'is_active', 'available')
        }),
        (_('Driver Information'), {
            'fields': ('with_driver', 'driver_name', 'driver_phone', 'driver_license_number', 'driver_experience_years', 'driver_languages'),
            'classes': ('driver-info',),
            'description': _('Configure driver information for cars with chauffeur service.')
        }),
        (_('Transfer Service'), {
            'fields': ('for_transfer', 'price_per_km', 'price_per_hour', 'max_passengers', 'max_luggage_pieces', 'max_luggage_weight'),
            'classes': ('transfer-info',),
            'description': _('Configure transfer service information for this vehicle.')
        })
    )

    def get_car_info(self, obj):
        return f"{obj.brand} {obj.car_model}" if obj.brand and obj.car_model else "-"
    get_car_info.short_description = _("Car")

    def get_driver_info(self, obj):
        if obj.with_driver and obj.driver_name:
            return f"{obj.driver_name} ({obj.driver_experience_years} {_('years exp.')})"
        return "-"
    get_driver_info.short_description = _("Driver")

    def get_transfer_info(self, obj):
        if obj.for_transfer:
            info = []
            if obj.price_per_km:
                info.append(f"{obj.price_per_km} TND/km")
            if obj.price_per_hour:
                info.append(f"{obj.price_per_hour} TND/h")
            if obj.max_passengers:
                info.append(f"{obj.max_passengers} {_('passengers')}")
            return " • ".join(info) if info else _("Configured")
        return "-"
    get_transfer_info.short_description = _("Transfer Service")

    def get_car_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"
    get_car_image.short_description = _("Image")

    class Media:
        js = [
            'admin/js/driver_fields.js',
            'admin/js/transfer_fields.js'
        ]
        css = {
            'all': [
                'admin/css/driver_fields.css',
                'admin/css/transfer_fields.css'
            ]
        }

@admin.register(CarUnavailability)
class CarUnavailabilityAdmin(admin.ModelAdmin):
    list_display = ('car', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'car__brand')
    search_fields = ('car__brand__name', 'car__car_model__name')
    ordering = ('start_date',)
    raw_id_fields = ('car',)

@admin.register(CarModelRequest)
class CarModelRequestAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'model_name', 'status', 'requested_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('brand_name', 'model_name', 'requested_by__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

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
    list_display = (
        'get_car_info', 
        'user', 
        'start_date', 
        'end_date', 
        'total_price', 
        'status', 
        'deposit_paid',
        'created_at',
        'get_agency'
    )
    list_filter = (
        'status', 
        'deposit_paid', 
        'created_at', 
        'start_date',
        'car__agence',
        'car__brand'
    )
    search_fields = (
        'car__brand__name', 
        'car__car_model__name',
        'car__agence__agency_name',
        'user__username', 
        'user__email',
        'notes'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    
    fieldsets = (
        (_('Reservation Details'), {
            'fields': ('car', 'user', 'start_date', 'end_date', 'total_price')
        }),
        (_('Status Information'), {
            'fields': ('status', 'deposit_paid', 'rejection_reason')
        }),
        (_('Additional Information'), {
            'fields': ('notes', 'created_at', 'updated_at')
        })
    )
    
    def get_car_info(self, obj):
        return f"{obj.car.brand} {obj.car.car_model}" if obj.car else "-"
    get_car_info.short_description = _("Car")
    
    def get_agency(self, obj):
        return obj.car.agence.agency_name if obj.car and obj.car.agence else "-"
    get_agency.short_description = _("Agency")
    
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
            return self.readonly_fields + ('car', 'user', 'start_date', 'end_date')
        return self.readonly_fields

@admin.register(TransferBooking)
class TransferBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'user', 'pickup_date', 'pricing_type', 'total_price', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'pricing_type', 'vehicle__agence')
    search_fields = ('user__username', 'user__email', 'pickup_address', 'dropoff_address', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('vehicle', 'user', 'pickup_date', 'status')
        }),
        (_('Locations'), {
            'fields': (
                'pickup_location', 'pickup_address',
                'dropoff_location', 'dropoff_address'
            )
        }),
        (_('Booking Details'), {
            'fields': (
                'pricing_type', 'distance', 'duration_hours',
                'passengers_count', 'luggage_pieces', 'luggage_weight',
                'notes'
            )
        }),
        (_('Payment Information'), {
            'fields': (
                'total_price', 'payment_status', 'amount_paid',
                'last_payment_date'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # En mode édition
            return self.readonly_fields + ('vehicle', 'user', 'pickup_date', 'pricing_type')
        return self.readonly_fields


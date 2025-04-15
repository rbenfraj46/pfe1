from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from home.models import (
    User, Devise, UserPreference, City, Delegation, 
    State, Contact, Agences, MailSubscription, AgencyPermission
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 
        'is_active', 'is_mail_verified', 'date_joined'
    )
    list_filter = ('is_staff', 'is_active', 'is_mail_verified', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        (_('Verification'), {
            'fields': ('is_mail_verified',)
        })
    )

@admin.register(Devise)
class DeviseAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'coefficient', 'unit', 'is_active', 'last_updated')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order_key', 'name')
    list_editable = ('is_active', 'coefficient', 'unit')
    readonly_fields = ('last_updated',)

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'devise')
    list_filter = ('devise',)
    search_fields = ('user__username', 'user__email', 'devise__name')
    raw_id_fields = ('user',)

@admin.register(State)
class StateAdmin(OSMGeoAdmin):
    list_display = ('name', 'order_key', 'get_position')
    search_fields = ('name',)
    ordering = ('order_key', 'name')
    
    def get_position(self, obj):
        if obj.position:
            return format_html('Lat: {}, Lng: {}', obj.position.y, obj.position.x)
        return '-'
    get_position.short_description = _('Position')

@admin.register(Delegation)
class DelegationAdmin(OSMGeoAdmin):
    list_display = ('name', 'state', 'order_key', 'get_position')
    list_filter = ('state',)
    search_fields = ('name', 'state__name')
    ordering = ('state', 'order_key', 'name')
    
    def get_position(self, obj):
        if obj.position:
            return format_html('Lat: {}, Lng: {}', obj.position.y, obj.position.x)
        return '-'
    get_position.short_description = _('Position')

@admin.register(City)
class CityAdmin(OSMGeoAdmin):
    list_display = ('name', 'delegation', 'zipcode', 'get_position')
    list_filter = ('delegation__state', 'delegation')
    search_fields = ('name', 'zipcode', 'delegation__name')
    ordering = ('delegation', 'name')
    
    def get_position(self, obj):
        if obj.position:
            return format_html('Lat: {}, Lng: {}', obj.position.y, obj.position.x)
        return '-'
    get_position.short_description = _('Position')

@admin.register(Agences)
class AgenceAdmin(OSMGeoAdmin):
    list_display = ('agency_name', 'commercial_name', 'email', 'phone_number', 
                   'is_active', 'is_mail_verified', 'is_auto', 'auto_approve_rental', 'creation_date')
    list_filter = ('is_active', 'is_mail_verified', 'is_auto', 'auto_approve_rental', 'governorate')
    search_fields = ('agency_name', 'commercial_name', 'email', 'phone_number', 
                    'tax_number', 'ceo_name')
    readonly_fields = ('creation_date', 'update_date')
    ordering = ('-creation_date',)
    list_editable = ('is_active', 'is_mail_verified', 'is_auto', 'auto_approve_rental')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'agency_name', 'commercial_name', 'tax_number',
                ('is_active', 'is_mail_verified', 'is_auto', 'auto_approve_rental')
            )
        }),
        (_('Contact Information'), {
            'fields': (
                'email', 'phone_number',
                'ceo_name', 'ceo_phone_number'
            )
        }),
        (_('Location'), {
            'fields': (
                'adress_agency',
                ('governorate', 'delegation', 'city'),
                'zipcode',
                'location'
            )
        }),
        (_('Additional Information'), {
            'fields': (
                'logo',
                'creator',
                ('creation_date', 'update_date')
            ),
            'classes': ('collapse',)
        })
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created', 'user')
    list_filter = ('is_read', 'created')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created', 'updated')
    ordering = ('-created',)
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = _("Mark selected messages as read")
    
    actions = ['mark_as_read']

@admin.register(MailSubscription)
class MailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'subscription_date', 'unsubscription_date',
                   'is_promo_used', 'promo_value')
    list_filter = ('is_active', 'is_promo_used', 'subscription_date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('subscription_date', 'unsubscription_date')
    ordering = ('-subscription_date',)
    raw_id_fields = ('user',)

@admin.register(AgencyPermission)
class AgencyPermissionAdmin(admin.ModelAdmin):
    list_display = ('agency', 'user', 'permission', 'granted_by', 'granted_at')
    list_filter = ('permission', 'granted_at', 'agency')
    search_fields = ('agency__agency_name', 'user__username', 'user__email')
    raw_id_fields = ('user', 'agency', 'granted_by')
    ordering = ('-granted_at',)
    
    readonly_fields = ('granted_at',)

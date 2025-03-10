from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.gis.admin import OSMGeoAdmin

from home.models import User
from home.models import Devise
from home.models import UserPreference
from home.models import City
from home.models import Delegation
from home.models import State
from home.models import Contact
from home.models import Agences
from home.models import MailSubscription


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active',
        'is_mail_verified',
        )

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('is_mail_verified',)
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('is_mail_verified',)
        })
    )


admin.site.register(User, CustomUserAdmin)


class DeviseAdmin(admin.ModelAdmin):
    model = Devise
    list_display = [f.name for f in Devise._meta.fields]
admin.site.register(Devise, DeviseAdmin)


class UserPreferenceAdmin(admin.ModelAdmin):
    model = UserPreference
    list_display = [f.name for f in UserPreference._meta.fields]

admin.site.register(UserPreference, UserPreferenceAdmin)


class StateAdmin(OSMGeoAdmin):
    list_display = ("name", "position")
admin.site.register(State, StateAdmin)

class DelegationAdmin(OSMGeoAdmin):
    model = Delegation
    list_display = ("name", "state", "position")

admin.site.register(Delegation, DelegationAdmin)


class CityAdmin(OSMGeoAdmin):
    model = City
    list_display = ("name", "delegation", "zipcode", "position")

admin.site.register(City, CityAdmin)

admin.site.register(Agences)

class ContactAdmin(admin.ModelAdmin):
    model = Contact
    list_display = ("name", "subject", "is_read", "created", "user")
admin.site.register(Contact, ContactAdmin)

class MailSubscriptonAdmin(admin.ModelAdmin):
    model = MailSubscription
    list_display = [f.name for f in MailSubscription._meta.fields]
admin.site.register(MailSubscription, MailSubscriptonAdmin)

# class AgenceAdmin(admin.ModelAdmin):
#     model = Agences
#     list_display = [f.name for f in Agences._meta.fields]
#
# admin.site.register(Agences, AgenceAdmin)

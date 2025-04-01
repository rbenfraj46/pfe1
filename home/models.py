from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from cars.models import GearType  
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.timezone import now

RIGHTS_NAME = {
    'agence': 'AGENCE',
    }

RIGHTS_TYPE = {
    'read': 'r',
    'write': 'w',
    }


class User(AbstractUser):
    is_mail_verified = models.BooleanField(default=False, verbose_name=_("Is The Mail Verified"))
    email = models.EmailField(_('email address'), blank=False,
                              max_length=255,
                              null=True, unique=True)
    @property
    def has_newsletter_subscription(self):
        subscription = MailSubscription.objects.filter(user=self).first()
        if subscription:
            return True
        else:
            return False


class Devise(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    value = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)
    coefficient = models.FloatField(default=1)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    order_key = models.IntegerField(null=True)
    unit = models.IntegerField(default=1)

    def __str__(self):
        return self.name + " (" + str(self.value) + ")"

    class Meta:
        db_table = "currency"

class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_("User"), null=True)
    devise = models.ForeignKey(Devise, on_delete=models.SET_NULL, verbose_name=_("Devise"), null=True)
    class Meta:
        db_table = "user_preference"


class State(models.Model):
    name = models.CharField(max_length=100)
    order_key = models.IntegerField(null=True)
    position = gis_models.PointField()

    @property
    def geom(self):
        return self.position

    @property
    def title(self):
        return self.name

    @property
    def description(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("states")
        db_table = "state"


class Delegation(models.Model):
    name = models.CharField(max_length=100)
    order_key = models.IntegerField(null=True)
    position = gis_models.PointField()
    state = models.ForeignKey(State, on_delete=models.SET_NULL, verbose_name=_("State"), null=True)

    @property
    def geom(self):
        return self.position

    def __str__(self):
        return self.name

    class Meta:
        db_table = "delegation"


class City(models.Model):
    name = models.CharField(max_length=100)
    zipcode = models.IntegerField(null=True)
    order_key = models.IntegerField(null=True)
    position = gis_models.PointField()
    delegation = models.ForeignKey(Delegation, on_delete=models.SET_NULL, verbose_name=_("Delegation"), null=True)

    @property
    def geom(self):
        return self.position

    class Meta:
        verbose_name_plural = _("cities")
        db_table = "city"


class Agences(models.Model):
    agency_name = models.CharField(max_length=4096, verbose_name=_('Agency Name'))
    commercial_name = models.CharField(max_length=4096, verbose_name=_('Agency Name'), null=True, blank=True)
    ceo_name = models.CharField(max_length=4096, verbose_name=_('CEO Name'), null=True, blank=True)
    ceo_phone_number= models.CharField(max_length=200, verbose_name=_('CEO Phone'), null=True, blank=True)

    tax_number = models.CharField(max_length=150, verbose_name=_('Tax registration Number'), null=False, unique=True)
    adress_agency = models.CharField(max_length=4096, verbose_name=_('Address'))
    governorate = models.CharField(max_length=200, verbose_name=_('Governorate'), null=True)
    city = models.CharField(max_length=200, verbose_name=_('City'), null=True)
    delegation = models.CharField(max_length=200, verbose_name=_('Delegation'),null=True)
    email = models.EmailField(_('email address'), max_length=255, null=False, unique=True)
    phone_number= models.CharField(max_length=200, verbose_name=_('Phone'))
    creation_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    is_mail_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_auto = models.BooleanField(default=False, verbose_name=_('Auto Activate Cars'))
    zipcode = models.CharField(max_length=150, verbose_name=_('CEO Name'), null=True)
    logo = models.ImageField(upload_to="logo",null=True, blank=True)

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_("Creator"), null=True)

    location = gis_models.PointField(null=True)

    @property
    def geom(self):
        return self.location

    class Meta :
        db_table= 'agence'


class RightsAccess(models.Model):
    name = models.CharField(max_length=4096, verbose_name=_('Field'))
    acess_id = models.IntegerField(null=True, blank=True)
    access_type = models.CharField(max_length=4096, verbose_name=_('Access Type'), null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_("User"), null=True)

    class Meta :
        db_table= 'rights_access'


class Contact(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('User Name'))
    email = models.EmailField(_('email address'), blank=True, max_length=255, null=True)
    phone = models.CharField(max_length=255, verbose_name=_('User Phone'), null=True, blank=True)
    subject = models.CharField(max_length=255, verbose_name=_('Subject'), null=True, blank=True)
    message = models.CharField(max_length=255, verbose_name=_('Message'), null=True, blank=True)

    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_("User"), null=True)

    class Meta :
        db_table= 'contact'


class MailSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_("User"), null=True)
    subscription_date = models.DateTimeField(auto_now=True, verbose_name=_("Subscripted At"))
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    unsubscription_date = models.DateTimeField(blank=True, null=True, verbose_name=_("UnSubscripted At"))
    promo_value = models.FloatField(default=0, verbose_name=_("Promotion price"))
    is_promo_used = models.BooleanField(verbose_name=_("Is Promotion Used"), default=False)

    class Meta :
        db_table= 'mail_subscription'

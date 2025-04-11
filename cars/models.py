from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.contrib.gis.db import models as gis_models


class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    img_hash = models.CharField(max_length=64, null=True, blank=True)
    img_extension = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    order_key = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "car_brand"


class GearType(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    order_key = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "gear_type"


class Transmission(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    order_key = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "transmission"


class CarModel(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Model Name"))
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Model Description"))
    img_hash = models.CharField(max_length=64, null=True, blank=True)
    img_extension = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, verbose_name=_("Brand"), null=True)

    air_conditioner = models.CharField(max_length=255, verbose_name=_("Air Conditioner"), null=True, blank=True)
    category = models.CharField(max_length=255, verbose_name=_("Category"), null=True, blank=True)

    cylinder = models.FloatField(verbose_name=_("Engine Cylinder"), null=True, blank=True)
    horse_power = models.FloatField(verbose_name=_("Horse Power"), null=True, blank=True)

    doors_nbr = models.IntegerField(verbose_name=_("Door Number"), null=True, blank=True)
    place_nbr = models.IntegerField(verbose_name=_("Place Number"), null=True, blank=True)
    energy = models.CharField(max_length=255, verbose_name=_("Energy"), null=True, blank=True)

    extra_urban_consumption = models.FloatField(verbose_name=_("Extra Urban Consumption"), null=True, blank=True)
    urban_consumption = models.FloatField(verbose_name=_("Urban Consumption"), null=True, blank=True)
    mixte_consumption = models.FloatField(verbose_name=_("Mixte Consumption"), null=True, blank=True)

    gear_type = models.CharField(max_length=255, verbose_name=_("Gear Type"),
                                 null=True, blank=True)
    gear_nbr = models.IntegerField(verbose_name=_("Gear Number"), null=True, blank=True)
    transmission = models.CharField(max_length=255, verbose_name=_("Transmission"),
                                    null=True, blank=True)

    max_speed = models.IntegerField(verbose_name=_("Max Speed"), null=True, blank=True)


    length = models.FloatField(verbose_name=_("Car Length"), null=True, blank=True)
    width = models.FloatField(verbose_name=_("Car Width"), null=True, blank=True)
    height = models.FloatField(verbose_name=_("Car Height"), null=True, blank=True)
    trunk_volume = models.IntegerField(verbose_name=_("Trunk Volume"), null=True, blank=True)


    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))
    order_key = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "car_model"

class AgencyCar(models.Model):
    agence = models.ForeignKey('home.Agences', on_delete=models.SET_NULL, null=True)  # Référence à l'agence
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True)
    gear_type = models.ForeignKey(GearType, on_delete=models.SET_NULL, verbose_name=_("Gear Type"), null=True)  # Add gear_type field

    image = models.ImageField(upload_to='cars', null=True, blank=True)
    fuel_policy = models.CharField(max_length=255)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_license_age = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def is_available(self, start_date, end_date):
        overlapping = self.unavailability_periods.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()
        return not overlapping

    def save(self, *args, **kwargs):
        if not self.image and self.car_model and self.car_model.img_hash and self.car_model.img_extension:
            self.image = f"media/{self.car_model.img_hash}.{self.car_model.img_extension}"
        super().save(*args, **kwargs)

class CarUnavailability(models.Model):
    car = models.ForeignKey(AgencyCar, on_delete=models.CASCADE, related_name="unavailability_periods")
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))

    class Meta:
        db_table = "car_unavailability"
        verbose_name = _("Car Unavailability")
        verbose_name_plural = _("Car Unavailability")

    def __str__(self):
        return f"{self.car} unavailable from {self.start_date} to {self.end_date}"

    def clean(self):
        if isinstance(self.start_date, str):
            try:
                self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(_('Invalid start date format'))

        if isinstance(self.end_date, str):
            try:
                self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(_('Invalid end date format'))

        current_date = timezone.now().date()
        
        if self.start_date < current_date:
            raise ValidationError(_('Start date cannot be in the past'))
        
        if self.end_date <= self.start_date:
            raise ValidationError(_('End date must be after start date'))
        
        overlapping = CarUnavailability.objects.filter(
            car=self.car,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)
        
        if overlapping.exists():
            raise ValidationError(_('This period overlaps with an existing unavailability period'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class CarModelRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )
    
    brand_name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "car_model_request"
        verbose_name = _("Car Model Request")
        verbose_name_plural = _("Car Model Requests")

    def __str__(self):
        return f"{self.brand_name} - {self.model_name}"

class CarReservation(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    )

    car = models.ForeignKey(AgencyCar, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    notes = models.TextField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(null=True, blank=True)
    deposit_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'car_reservation'
        verbose_name = _("Car Reservation")
        verbose_name_plural = _("Car Reservations")

    def __str__(self):
        return f"{self.user.username} - {self.car} ({self.start_date} to {self.end_date})"

    def clean(self):
        if isinstance(self.start_date, str):
            try:
                self.start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(_('Invalid start date format'))

        if isinstance(self.end_date, str):
            try:
                self.end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(_('Invalid end date format'))

        if self.start_date < timezone.now().date():
            raise ValidationError(_('Start date cannot be in the past'))
        
        if self.end_date <= self.start_date:
            raise ValidationError(_('End date must be after start date'))

        # Vérifier les chevauchements
        overlapping = CarReservation.objects.filter(
            car=self.car,
            status='approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(_('This period overlaps with an existing reservation'))

    def save(self, *args, **kwargs):
        if not self.total_price:
            # Calculer le prix total basé sur le nombre de jours
            days = (self.end_date - self.start_date).days
            self.total_price = self.car.price_per_day * days

        self.clean()
        super().save(*args, **kwargs)

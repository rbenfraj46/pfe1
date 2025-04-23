from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.contrib.gis.db import models as gis_models
import logging

logger = logging.getLogger(__name__)

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

    def calculate_total_price(self, start_date, end_date):
        """Calculer le prix total pour une période donnée"""
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return None
            
        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return None
            
        if start_date and end_date and end_date > start_date:
            days = (end_date - start_date).days
            total = self.price_per_day * days
            return {
                'days': days,
                'price_per_day': float(self.price_per_day),
                'security_deposit': float(self.security_deposit),
                'total_price': float(total)
            }
        return None

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
        ('ongoing', _('Ongoing')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('rejected', _('Rejected')),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', _('Unpaid')),
        ('partial', _('Partially Paid')),
        ('full', _('Fully Paid')),
        ('refunded', _('Refunded')),
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
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='unpaid'
    )
    amount_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    last_payment_date = models.DateTimeField(null=True, blank=True)

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

        # Check for overlapping reservations
        overlapping = CarReservation.objects.filter(
            car=self.car,
            status='approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(_('This period overlaps with an existing approved reservation'))

        # Check if car is unavailable during this period
        if self.car.unavailability_periods.filter(
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).exists():
            raise ValidationError(_('The car is marked as unavailable during this period'))

    def save(self, *args, **kwargs):
        if not self.total_price:
            # Calculate total price based on the number of days
            days = (self.end_date - self.start_date).days
            self.total_price = self.car.price_per_day * days

        # Store old status if this is an update
        old_status = None
        if self.pk:
            old_obj = CarReservation.objects.get(pk=self.pk)
            old_status = old_obj.status

        self.clean()
        super().save(*args, **kwargs)

        # Send notifications if status has changed
        if old_status and old_status != self.status:
            try:
                from home.mail_util import send_car_rental_notification
                
                if self.status == 'approved':
                    send_car_rental_notification(self, 'approved')
                elif self.status == 'cancelled':
                    send_car_rental_notification(
                        self, 
                        'cancelled', 
                        cancellation_reason=getattr(self, 'cancellation_reason', None)
                    )
            except Exception as e:
                logger.error(f"Failed to send reservation notification email: {str(e)}")

    def request_status_change(self, requested_status, reason, requested_by):
        """Request a status change based on agency's auto-approve setting"""
        if self.car.agence.auto_approve_rental:
            # Auto-approve the change
            self.status = requested_status
            self.save()
            
            # Create an auto-approved status change record
            status_change = RentalStatusChange.objects.create(
                reservation=self,
                requested_by=requested_by,
                reviewed_by=requested_by,
                requested_status=requested_status,
                reason=reason,
                status='approved'
            )
        else:
            # Create a pending status change request
            status_change = RentalStatusChange.objects.create(
                reservation=self,
                requested_by=requested_by,
                requested_status=requested_status,
                reason=reason
            )

        return status_change

    def update_status(self, requested_status, reason, requested_by):
        """
        Met à jour le statut de la réservation selon le mode de l'agence :
        - Si l'agence est en mode auto, le statut est mis à jour immédiatement.
        - Sinon, la demande est bloquée et une notification (log ou email) est envoyée à l'admin.
        """
        if int(self.car.agence.auto_approve_rental) == 1:
            old_status = self.status
            self.status = requested_status
            self.save()
            from home.mail_util import send_car_rental_notification
            if requested_status == 'approved':
                send_car_rental_notification(self, 'approved')
            elif requested_status == 'cancelled':
                send_car_rental_notification(self, 'cancelled', cancellation_reason=reason)
            return True
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Demande de changement de statut pour réservation {self.id} à '{requested_status}' par {requested_by.email}. Raison: {reason}")
            # TODO: envoyer un email à l'admin si besoin
            raise PermissionError("Seul un administrateur peut valider ce changement de statut pour cette agence.")

    def update_payment_status(self, amount_paid):
        """Update payment status based on amount paid"""
        self.amount_paid = amount_paid
        self.last_payment_date = timezone.now()
        
        if amount_paid >= self.total_price:
            self.payment_status = 'full'
            if self.status == 'approved':
                self.status = 'ongoing'
        elif amount_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'
        
        self.save()

    def auto_complete(self):
        """Automatically check and update status to completed if conditions are met"""
        if (self.status == 'ongoing' and 
            self.payment_status in ['full', 'partial'] and 
            timezone.now().date() > self.end_date):
            self.status = 'completed'
            self.save()
            return True
        return False

    def can_transition_to(self, new_status):
        """Check if status transition is valid"""
        valid_transitions = {
            'pending': ['approved', 'rejected', 'cancelled'],
            'approved': ['ongoing', 'cancelled'],
            'ongoing': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': [],
            'rejected': []
        }
        return new_status in valid_transitions.get(self.status, [])
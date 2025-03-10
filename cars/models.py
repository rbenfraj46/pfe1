from django.db import models
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    img_hash = models.CharField(max_length=32, null=True, blank=True)
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
    img_hash = models.CharField(max_length=32, null=True, blank=True)
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

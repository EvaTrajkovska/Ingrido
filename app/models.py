from django.contrib.auth.models import User
from django.db import models


class Buyer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)

    def __str__(self):
        return f' {self.name}  {self.surname} '


class Staff(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)


class NutrientsChart(models.Model):
    energy = models.IntegerField(null=True, blank=True)
    calories = models.IntegerField(null=True, blank=True)
    fat = models.IntegerField(null=True, blank=True)
    saturated_fat = models.IntegerField(null=True, blank=True)
    carbs = models.IntegerField(null=True, blank=True)
    sugar = models.IntegerField(null=True, blank=True)
    fiber = models.IntegerField(null=True, blank=True)
    protein = models.IntegerField(null=True, blank=True)
    cholesterol = models.IntegerField(null=True, blank=True)
    sodium = models.IntegerField(null=True, blank=True)
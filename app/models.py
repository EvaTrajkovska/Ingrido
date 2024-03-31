import datetime

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


class Ingredient(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class NotIncluded(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class Menu(models.Model):
    name = models.CharField(max_length=255)
    img = models.ImageField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    subheading = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=255, null=True, blank=True)
    allergens = models.CharField(max_length=255, null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    total_time = models.IntegerField(null=True, blank=True)
    pic = models.ImageField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class RecipeMenu(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f' {self.recipe}  {self.menu} '


class Cart(models.Model):
    pass


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)
    shipping_time_start = models.TimeField(default=datetime.time(15, 00))
    shipping_time_end = models.TimeField(default=datetime.time(19, 00))

    def __str__(self):
        return self.address

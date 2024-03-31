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
    owner = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    sum = models.FloatField(null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.transaction_id)

    @property
    def get_cart_total(self):
        cart_items = self.cartitem_set.all()
        total = sum([item.get_total for item in cart_items])
        return total

    @property
    def get_cart_items(self):
        cart_items = self.cartitem_set.all()
        return cart_items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.recipe.price * self.quantity
        return total


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

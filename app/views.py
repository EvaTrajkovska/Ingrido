import json
from django.http import JsonResponse
from django.shortcuts import render
from django.template.defaulttags import register
from .models import *


def menu(request):
    menuId = request.session['menuId']
    menu = Menu.objects.get(id=menuId)
    qs = RecipeMenu.objects.filter(menu_id=menuId).all()
    context = {"recipes": qs, "menu": menu}
    return render(request, "Menu.html", context)


def go_to_detailed_view_menu(request):
    data = json.loads(request.body)
    menuId = data['menuId']
    request.session['menuId'] = menuId
    return JsonResponse("Got to detail page", safe=False)


def insertRecipe(request):
    if not request.user.is_superuser:
        return render(request, 'AccessDenied.html')

    @register.filter(name='split')
    def split(value):
        return value.split(',')

    if request.method == 'POST':
        data = request.POST
        pic = request.FILES.get('picture')
        menuN = data['hid-menu']

        ingredients = data['hid-ingredient']
        nots = data['hid-not']

        ingredients_list = split(ingredients)
        print(ingredients_list)

        nots_list = split(nots)
        print(nots_list)

        for i in ingredients_list:
            print(i)

        for i in nots_list:
            print(i)

        recipe = Recipe.objects.create(
            name=data['heading'],
            subheading=data['subheading'],
            description=data['desc'],
            difficulty=data['difficulty'],
            allergens=data['allergens'],
            total_time=data['total_time'],
            tags=data['tags'],
            price=data['price'],
            pic=pic
        )

        menu = Menu.objects.get(name=menuN)
        RecipeMenu.objects.create(
            menu=menu,
            recipe=recipe
        )

        for i in ingredients_list:
            ing = Ingredient.objects.get(name=i)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredients=ing
            )

        for i in nots_list:
            ni = NotIncluded.objects.get(name=i)
            RecipeNotIncluded.objects.create(
                recipe=recipe,
                other=ni
            )

        nutri_table = NutrientsChart.objects.create(
            energy=data['energy'],
            calories=data['calories'],
            fat=data['fat'],
            saturated_fat=data['saturated_fat'],
            carbs=data['carbs'],
            sugar=data['sugar'],
            protein=data['protein'],
            cholesterol=data['cholesterol'],
            sodium=data['sodium'],
        )

        RecipeNutrientsChart.objects.create(
            recipe=recipe,
            nutrients_chart=nutri_table
        )

    notIncluded = NotIncluded.objects.all()
    ingredients = Ingredient.objects.all()
    menus = Menu.objects.all()

    context = {"notIncl": notIncluded, "ingredients": ingredients, "menus": menus}
    return render(request, "InsertRecipe.html", context=context)

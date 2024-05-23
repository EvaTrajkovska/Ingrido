import json
import stripe

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import BuyerLoginForm, UserRegisterForm
from .models import *
from django.views.decorators.http import require_POST


def home(request):
    qs = Menu.objects.all()
    context = {"menus": qs, }
    return render(request, "HomePage.html", context)


def about_us(request):
    return render(request, "AboutUsPage.html")


def how_it_works(request):
    return render(request, "HowItWorks.html")


def menus(request):
    qs = Menu.objects.all()
    context = {"menus": qs, }
    return render(request, "MenusList.html", context)


def cart(request):
    if request.user.is_authenticated:
        owner = request.user.buyer
        order, created = Cart.objects.get_or_create(owner=owner, complete=False)
        items = order.cartitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}
    return render(request, "cart/cart.html", context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.buyer
        order, created = Cart.objects.get_or_create(owner=customer, complete=False)
        items = order.cartitem_set.all()

        # Fetch the latest shipping address if it exists
        shipping_address = ShippingAddress.objects.filter(customer=customer).last()

        if shipping_address:
            shipping_data = {
                'address': shipping_address.address,
                'city': shipping_address.city,
                'country': shipping_address.country,
                'zipcode': shipping_address.zipcode,
                'shipping_time_start': shipping_address.shipping_time_start,
                'shipping_time_end': shipping_address.shipping_time_end,
            }
        else:
            shipping_data = {}

        # Cart Total Price
        total = str(order.get_cart_total).replace('.', '')

        # Stripe Intent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=total,
            currency='usd',
            metadata={'customerid': customer.id}
        )
        client_secret = intent.client_secret

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        shipping_data = {}
        client_secret = None

    context = {'customer': customer, 'items': items, 'order': order, 'shipping_data': shipping_data,
               'client_secret': client_secret, 'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY}
    return render(request, "cart/checkout.html", context)


def menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    qs = RecipeMenu.objects.filter(menu_id=menu_id).all()
    context = {"recipes": qs, "menu": menu}
    return render(request, "Menu.html", context)


def go_to_detailed_view(request):
    data = json.loads(request.body)
    productId = data['productId']
    request.session['productId'] = productId
    return JsonResponse("Got to detail page", safe=False)


def go_to_detailed_view_menu(request):
    data = json.loads(request.body)
    menuId = data['menuId']
    request.session['menuId'] = menuId
    return JsonResponse("Got to detail page", safe=False)


def detailedView(request):
    productId = request.session['productId']
    product = Recipe.objects.get(id=productId)
    ingr = RecipeIngredient.objects.filter(recipe=product).all()
    nots = RecipeNotIncluded.objects.filter(recipe=product).all()
    nc = RecipeNutrientsChart.objects.get(recipe=product)
    context = {'product': product, 'ingredients': ingr, 'nots': nots, 'chart': nc}
    return render(request, 'DetailedViewPage.html', context)


def insertRecipe(request):
    if not request.user.is_superuser:
        return render(request, 'AccessDeniedPage.html')

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


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    request.session['productId'] = productId
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.buyer
    product = Recipe.objects.get(id=productId)
    order, created = Cart.objects.get_or_create(owner=customer, complete=False)

    orderItem, created = CartItem.objects.get_or_create(cart=order, recipe=product)

    if action == 'add':
        print('Added')
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        print('Removed')
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


# @csrf_exempt
def processOrder(request):
    data = json.loads(request.body)
    transaction_id = data['form']['client_secret']

    if request.user.is_authenticated:
        customer = request.user.buyer
        order, created = Cart.objects.get_or_create(owner=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        order.sum = total
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            country=data['shipping']['country'],
            zipcode=data['shipping']['zipcode'],
            shipping_time_start=data['shipping']['shipping_time_start'],
            shipping_time_end=data['shipping']['shipping_time_end'],

        )

    return JsonResponse('Payment submitted..', safe=False)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        print(e)
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        Cart.objects.filter(transaction_id=event.data.object.client_secret).update(complete=True)
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)


@require_POST
def delete_cart_item(request):
    try:
        data = json.loads(request.body)
        productId = data['productId']
        request.session['productId'] = productId
        action = data['action']
        print('Action:', action)
        print('Product:', productId)

        customer = request.user.buyer
        product = Recipe.objects.get(id=productId)
        order, created = Cart.objects.get_or_create(owner=customer, complete=False)

        orderItem, created = CartItem.objects.get_or_create(cart=order, recipe=product)

        if action == 'delete':
            print('Deleted')
            orderItem.delete()

        cart_item = CartItem.objects.get(id=productId)
        cart_item.delete()

        return JsonResponse({'message': 'Cart item deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def userProfile(request):
    if request.user.is_authenticated:
        customer = request.user.buyer
        # Fetch the latest shipping address if it exists
        shipping_address = ShippingAddress.objects.filter(customer=customer).last()

        if shipping_address:
            shipping_data = {
                'address': shipping_address.address,
                'city': shipping_address.city,
                'country': shipping_address.country,
                'zipcode': shipping_address.zipcode,
                'shipping_time_start': shipping_address.shipping_time_start,
                'shipping_time_end': shipping_address.shipping_time_end,
            }
        else:
            shipping_data = {}

    context = {'customer': customer, 'shipping_data': shipping_data}
    return render(request, "UserProfile.html", context)


def success(request):
    return render(request, "cart/PaymentSuccess.html")


def successfully_added_menu(request):
    return render(request, "SuccessfullyAddedMenu.html")


def successfully_edited_menu(request):
    return render(request, "SuccessfullyEditedMenu.html")


def meal_successfully_added(request):
    return render(request, 'MealSuccessfullyAdded.html')


def meal_successfully_edited(request):
    return render(request, 'MealSuccessfullyEdited.html')


def login_view(request):
    if request.method == 'POST':
        form = BuyerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Welcome, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect username or password')
        else:
            messages.error(request, 'Incorrect username or password')
    else:
        form = BuyerLoginForm()
    return render(request, 'LogIn.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Buyer.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                surname=form.cleaned_data.get('surname'),
                address=form.cleaned_data.get('address'),
                city=form.cleaned_data.get('city'),
                country=form.cleaned_data.get('country'),
                zipcode=form.cleaned_data.get('zipcode')
            )
            username = form.cleaned_data.get('username')
            if (form.cleaned_data.get('address') != "" and
                    form.cleaned_data.get('city') != "" and
                    form.cleaned_data.get('country') != "" and
                    form.cleaned_data.get('zipcode') != ""):
                ShippingAddress.objects.create(
                    customer=user.buyer,
                    address=form.cleaned_data.get('address'),
                    city=form.cleaned_data.get('city'),
                    country=form.cleaned_data.get('country'),
                    zipcode=form.cleaned_data.get('zipcode')
                )

            messages.success(request, f'Your account has been created! You are now able to log in')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'Register.html', {'form': form})


@login_required
@staff_member_required
def add_menu(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        img = request.FILES.get('img')
        if name and img:
            menu = Menu.objects.create(name=name, img=img)
            return redirect('successfullyAddedMenu')
        else:
            error_message = "Please fill in all required fields."
            return render(request, 'add_menu.html', {'error_message': error_message})
    else:
        return render(request, 'AddMenu.html')


@login_required
@staff_member_required
def edit_menu(request, menu_id):
    menu = get_object_or_404(Menu, pk=menu_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        img = request.FILES.get('img')
        if name:
            menu.name = name
            if img:
                menu.img = img
            menu.save()
            return redirect('successfullyEditedMenu')
        else:
            error_message = "Please fill in all required fields."
            return render(request, 'EditMenu.html', {'menu': menu, 'error_message': error_message})
    else:
        return render(request, 'EditMenu.html', {'menu': menu})


@login_required
@staff_member_required
def delete_menu(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)

    if request.method == "POST":
        menu.delete()
        messages.success(request, "Menu deleted successfully.")
        return redirect('menus')

    return render(request, 'ConfirmMenuDelete.html', {'menu': menu})


@login_required
@staff_member_required
def add_recipe(request, menu_id):
    if not request.user.is_superuser:
        return render(request, 'AccessDeniedPage.html')

    def split(value):
        return value.split(',')

    if request.method == 'POST':
        data = request.POST
        pic = request.FILES.get('picture')

        ingredients = data['hid-ingredient']
        nots = data['hid-not']

        ingredients_list = split(ingredients)
        nots_list = split(nots)

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

        menu = Menu.objects.get(id=menu_id)
        RecipeMenu.objects.create(
            menu=menu,
            recipe=recipe
        )

        for ingredient_name in ingredients_list:
            ingredient = Ingredient.objects.get(name=ingredient_name)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredients=ingredient
            )

        for not_name in nots_list:
            not_included = NotIncluded.objects.get(name=not_name)
            RecipeNotIncluded.objects.create(
                recipe=recipe,
                other=not_included
            )

        nutrient_chart = NutrientsChart.objects.create(
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
            nutrients_chart=nutrient_chart
        )

        return redirect('mealSuccessfullyAdded')

    notIncluded = NotIncluded.objects.all()
    ingredients = Ingredient.objects.all()

    context = {"notIncl": notIncluded, "ingredients": ingredients}
    return render(request, "AddRecipe.html", context=context)


@login_required
@staff_member_required
def edit_recipe(request, recipe_id):
    if not request.user.is_superuser:
        return render(request, 'AccessDeniedPage.html')

    def split(value):
        return value.split(',')

    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe_nutrients_chart = RecipeNutrientsChart.objects.filter(recipe=recipe).first()

    if request.method == 'POST':
        data = request.POST
        pic = request.FILES.get('picture')

        ingredients = data['hid-ingredient']
        nots = data['hid-not']

        ingredients_list = split(ingredients)
        nots_list = split(nots)

        recipe.name = data['heading']
        recipe.subheading = data['subheading']
        recipe.description = data['desc']
        recipe.difficulty = data['difficulty']
        recipe.allergens = data['allergens']
        recipe.total_time = data['total_time']
        recipe.tags = data['tags']
        recipe.price = data['price']

        if pic:
            recipe.pic = pic

        recipe.save()

        menu_id = data.get('menu_id')

        if menu_id:
            menu = Menu.objects.get(id=menu_id)
            recipe_menu, created = RecipeMenu.objects.get_or_create(recipe=recipe)
            recipe_menu.menu = menu
            recipe_menu.save()

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        for ingredient_name in ingredients_list:
            ingredient = Ingredient.objects.get(name=ingredient_name)
            RecipeIngredient.objects.create(recipe=recipe, ingredients=ingredient)

        RecipeNotIncluded.objects.filter(recipe=recipe).delete()
        for not_name in nots_list:
            not_included = NotIncluded.objects.get(name=not_name)
            RecipeNotIncluded.objects.create(recipe=recipe, other=not_included)

        if recipe_nutrients_chart:
            recipe_nutrients_chart.nutrients_chart.energy = data['energy']
            recipe_nutrients_chart.nutrients_chart.calories = data['calories']
            recipe_nutrients_chart.nutrients_chart.fat = data['fat']
            recipe_nutrients_chart.nutrients_chart.saturated_fat = data['saturated_fat']
            recipe_nutrients_chart.nutrients_chart.carbs = data['carbs']
            recipe_nutrients_chart.nutrients_chart.sugar = data['sugar']
            recipe_nutrients_chart.nutrients_chart.fiber = data['fiber']
            recipe_nutrients_chart.nutrients_chart.protein = data['protein']
            recipe_nutrients_chart.nutrients_chart.cholesterol = data['cholesterol']
            recipe_nutrients_chart.nutrients_chart.sodium = data['sodium']
            recipe_nutrients_chart.nutrients_chart.save()

        return redirect('mealSuccessfullyEdited')

    notIncluded = NotIncluded.objects.all()
    ingredients = Ingredient.objects.all()
    menus = Menu.objects.all()

    context = {"notIncl": notIncluded, "ingredients": ingredients, "menus": menus, "recipe": recipe, "recipe_nutrients_chart": recipe_nutrients_chart.nutrients_chart if recipe_nutrients_chart else None}
    return render(request, "EditRecipe.html", context=context)


@login_required
@staff_member_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    menu_instance = recipe.menus.first()

    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted successfully.")
        if menu_instance:
            return redirect('menu', menu_id=menu_instance.id)
        else:
            return redirect('menus')

    return render(request, 'ConfirmRecipeDelete.html',
                  {'recipe': recipe, 'menu_id': menu_instance.id if menu_instance else None})

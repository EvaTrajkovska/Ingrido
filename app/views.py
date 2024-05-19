import json
import stripe

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import BuyerLoginForm
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

    context = {'customer': customer, 'items': items, 'order': order, 'shipping_data': shipping_data, 'client_secret': client_secret, 'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY}
    return render(request, "cart/checkout.html", context)


def menu(request):
    menuId = request.session['menuId']
    menu = Menu.objects.get(id=menuId)
    qs = RecipeMenu.objects.filter(menu_id=menuId).all()
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
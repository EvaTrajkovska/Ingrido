"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path
from app.views import *

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('home/', home, name="home"),
                  path('', home, name="home"),
                  path('menu/', menu, name="menu"),
                  path('menus/', menus, name="menus"),
                  path('about_us/', about_us, name="about_us"),
                  path('how_it_works/', how_it_works, name='how_it_works'),
                  path('cart/', cart, name="cart"),
                  path('checkout/', checkout, name="checkout"),
                  path('go_to_detailed_view/', go_to_detailed_view, name="go_to_detailed_view"),
                  path('detailedView/', detailedView, name="detailedView"),
                  path('updateItem/', updateItem, name='updateItem'),
                  path('go_to_detailed_view_menu/', go_to_detailed_view_menu, name="go_to_detailed_view_menu"),
                  path('process_order/', processOrder, name='processOrder'),
                  path('webhook/', stripe_webhook),
                  path('insert_recipe/', insertRecipe, name='insertRecipe'),
                  path('success/', success, name='paymentSuccessful'),
                  path('successfully_added_menu/', successfully_added_menu, name='successfullyAddedMenu'),
                  path('deleteCartItem/', delete_cart_item, name='delete_cart_item'),
                  path('userProfile/', userProfile, name='userProfile'),
                  path('login/', login_view, name='login_view')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

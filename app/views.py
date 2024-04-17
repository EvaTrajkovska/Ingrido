from django.shortcuts import render

from app.models import Menu, RecipeMenu


# Create your views here.

def menu(request):
    menuId = request.session['menuId']
    menu = Menu.objects.get(id=menuId)
    qs = RecipeMenu.objects.filter(menu_id=menuId).all()
    context = {"recipes": qs, "menu": menu}
    return render(request, "Menu.html", context)

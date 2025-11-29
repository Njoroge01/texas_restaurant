from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from .models import Ingredient

def inventory_dashboard(request):
    ingredients = Ingredient.objects.all().order_by("name")
    return render(request, "inventory/dashboard.html", {"ingredients": ingredients})

def update_stock(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    
    if request.method == "POST":
        change = int(request.POST.get("change_stock", 0))
        ingredient.current_stock = F("current_stock") + change
        ingredient.save(update_fields=["current_stock"])
        ingredient.refresh_from_db()  # update after F() operation

    return redirect("inventory_dashboard")

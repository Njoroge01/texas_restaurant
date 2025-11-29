# orders/views_customer.py
from django.shortcuts import render
from menu.models import MenuItem

def customer_menu(request, table_number):
    items = MenuItem.objects.all().order_by('category__name')

    return render(request, "orders/customer_menu.html", {
        "items": items,
        "table_number": table_number,
    })
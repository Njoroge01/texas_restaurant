from django.urls import path
from .views import inventory_dashboard, update_stock

urlpatterns = [
    path('', inventory_dashboard, name="inventory_dashboard"),
    path('update/<int:ingredient_id>/', update_stock, name="update_stock"),
]

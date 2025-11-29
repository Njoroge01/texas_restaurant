from django.contrib import admin
from django.utils.html import format_html
from .models import Ingredient, MenuItemIngredient, StockTransaction

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'colored_stock_level', 'unit', 'reorder_level', 'stock_alert')
    list_filter = ('unit',)

    def colored_stock_level(self, obj):
        qty = float(obj.quantity_in_stock or 0)
        unit = obj.unit

        if qty <= 0:
            color = 'gray'
        elif qty <= float(obj.reorder_level):
            color = 'red'
        elif qty <= float(obj.reorder_level) * 2:
            color = 'orange'
        else:
            color = 'green'

        return format_html('<b style="color:{};">{} {}</b>', color, qty, unit)

    colored_stock_level.short_description = "Stock Level"

    def stock_alert(self, obj):
        qty = float(obj.quantity_in_stock or 0)

        if qty <= 0:
            return format_html('<span style="color: red; font-weight:bold;">OUT OF STOCK!</span>')
        elif qty <= float(obj.reorder_level):
            return format_html('<span style="color: orange; font-weight:bold;">LOW STOCK!</span>')
        else:
            return format_html('<span style="color: green;">OK</span>')

    stock_alert.short_description = "Alert"


@admin.register(MenuItemIngredient)
class MenuItemIngredientAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'ingredient', 'quantity_required')


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'transaction_type', 'date')
    list_filter = ('transaction_type', 'date')

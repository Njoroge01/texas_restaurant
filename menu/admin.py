from decimal import Decimal
from django.contrib import admin
from django.utils.html import format_html
from .models import MenuItem, Category


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'cost_price', 'profit_colored', 'category','stock','is_available',)
    search_fields = ('name',)
    list_filter = ('category',)
    list_editable= ('stock', 'is_available',)
    
    def profit_colored(self, obj):
        """Profit = Selling Price – Cost Price"""
        try:
            selling = Decimal(str(obj.price))
            cost = Decimal(str(obj.cost_price))
        except Exception:
            return "-"

        profit_value = selling - cost
        color = "green" if profit_value > 0 else "red"
        profit_str = f"{profit_value:.2f}"

        return format_html(
            '<b><span style="color:{};">KSh {}</span></b>',
            color,
            profit_str
        )

    profit_colored.short_description = "Profit"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    def has_delete_permission(self, request, obj=None):
      return request.user.groups.filter(name="Manager").exists()
 
from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from .models import Order, OrderItem
from menu.models import MenuItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'customer_name', 'table_number', 'waiter',
        'colored_status', 'total', 'payment_method',
        'paid_amount', 'is_paid', 'created_at',
        'print_receipt_button',
    )

    list_filter = ('status', 'is_paid', 'payment_method')
    search_fields = ('customer_name',)

    readonly_fields = ('subtotal', 'tax', 'total', 'created_at', 'print_receipt_button')

    fieldsets = (
        ("Order Info", {
            'fields': ('customer_name', 'table_number', 'waiter', 'status')
        }),
        ("Payment", {
            'fields': ('payment_method', 'paid_amount', 'is_paid')
        }),
        ("Totals", {
            'fields': ('subtotal', 'tax', 'total', 'created_at'),
        }),
        ("Receipt", {
            'fields': ('print_receipt_button',),
        }),
    )

    inlines = [OrderItemInline]

    def colored_status(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'cancelled': 'red'
        }
        return format_html(
            '<b><span style="color: {};">{}</span></b>',
            colors.get(obj.status, 'gray'),
            obj.status.capitalize()
        )
    colored_status.short_description = "Status"

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name="Manager").exists()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        subtotal = Decimal('0.00')
        for item in obj.items.all():
            item.price = item.menu_item.price
            item.save()
            subtotal += item.price * item.quantity

        obj.subtotal = subtotal
        obj.tax = obj.subtotal * Decimal('0.16')
        obj.total = obj.subtotal + obj.tax - obj.discount

        # ✅ Auto mark as paid if fully settled
        if obj.paid_amount >= obj.total:
            obj.is_paid = True
            obj.status = 'completed'
        else:
            obj.is_paid = False

        obj.save()

    def print_receipt_button(self, obj):
        if not obj.id:
            return "-"
        return format_html(
            '<a class="button" href="/orders/{}/receipt/" target="_blank">🧾 Print</a>',
            obj.id
        )
    print_receipt_button.short_description = "Receipt"

from django.contrib import admin

from django.contrib import admin
from .models import Table

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'status')
    list_editable = ('status',)

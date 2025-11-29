from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice


@admin.action(description="Mark selected invoices as Paid")
def mark_as_paid(modeladmin, request, queryset):
    queryset.update(status='Paid', paid=True)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'payment_method', 'date_issued', 'colored_status', 'view_receipt_link')
    list_filter = ('status', 'payment_method', 'date_issued')
    actions = [mark_as_paid]
    search_fields = ('invoice_number', 'order__customer__name')

    def colored_status(self, obj):
        """Display color-coded invoice status."""
        color_map = {
            'Paid': '#16a34a',       # green
            'Unpaid': '#facc15',     # yellow
            'Cancelled': '#dc2626',  # red
        }
        color = color_map.get(obj.status, 'gray')
        return format_html(
            f'<span style="color:white; background-color:{color}; padding:3px 8px; '
            f'border-radius:6px; font-weight:bold;">{obj.status}</span>'
        )
    colored_status.short_description = "Status"

    def view_receipt_link(self, obj):
        return format_html(
            '<a href="/billing/receipt/{}/" target="_blank" '
            'style="background-color:#2563eb; color:white; padding:4px 8px; '
            'border-radius:6px; text-decoration:none;">🧾 View</a>',
            obj.id
        )
    view_receipt_link.short_description = "Receipt"

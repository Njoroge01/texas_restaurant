from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'payment_method', 'date_issued', 'status', 'total_amount')
    list_filter = ('status', 'payment_method', 'date_issued')
    search_fields = ('invoice_number', 'order__customer__name')

    change_list_template = "admin/billing/invoice_summary.html"

    def changelist_view(self, request, extra_context=None):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        filter_period = request.GET.get('period', 'all')

        if filter_period == 'today':
            invoices = Invoice.objects.filter(date_issued__date=today)
        elif filter_period == 'week':
            invoices = Invoice.objects.filter(date_issued__date__gte=start_of_week)
        elif filter_period == 'month':
            invoices = Invoice.objects.filter(date_issued__date__gte=start_of_month)
        else:
            invoices = Invoice.objects.all()

        paid_count = invoices.filter(status='Paid').count()
        unpaid_count = invoices.filter(status='Unpaid').count()
        cancelled_count = invoices.filter(status='Cancelled').count()
        total_revenue = invoices.filter(status='Paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        extra_context = extra_context or {}
        extra_context['summary'] = {
            'paid_count': paid_count,
            'unpaid_count': unpaid_count,
            'cancelled_count': cancelled_count,
            'total_revenue': total_revenue,
        }
        extra_context['filter_period'] = filter_period

        return super().changelist_view(request, extra_context=extra_context)

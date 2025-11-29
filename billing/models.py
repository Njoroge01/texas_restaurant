from django.db import models
from orders.models import Order


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    date_issued = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Mobile Money', 'Mobile Money'),
    ])
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.invoice_number} for {self.order}"

    def total_amount(self):
        return self.order.total_amount

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Mobile Money', 'Mobile Money'),
    ]

    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    date_issued = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unpaid')  # ✅ added field
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.invoice_number} for {self.order}"

    def total_amount(self):
        return self.order.total_amount

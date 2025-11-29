from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from menu.models import MenuItem
class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Table {self.number} ({self.status})"



class Order(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    table_number = models.PositiveIntegerField(null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    waiter = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_orders'
    )

    customer_name = models.CharField(max_length=255, blank=True, null=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHODS, blank=True, null=True
    )
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id or 'new'}"

    def mark_as_paid(self, method=None, amount=None):
        """Marks an order as paid and completed from POS"""
        self.is_paid = True
        self.status = 'completed'
       
        if method:
            self.payment_method = method
        if amount:
            self.paid_amount = Decimal(amount)
        self.save()

        if self.table:
           self.table.status = "available"
           self.table.save()


    @property
    def total_amount(self):
        """Calculate total directly from items (used before saving to DB)"""
        return sum((item.item_total for item in self.items.all()), Decimal('0.00'))

    def update_totals(self):
        """Recalculate subtotal, tax, and total from OrderItems"""
        subtotal = sum(item.item_total for item in self.items.all())
        tax = subtotal * Decimal('0.16')  # ✅ configurable later
        total = subtotal + tax - self.discount

        self.subtotal = subtotal
        self.tax = tax
        self.total = total
        self.save()


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    item_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if self.menu_item and (not self.price or self.price == Decimal('0.00')):
            self.price = self.menu_item.price
        super().save(*args, **kwargs)
        self.order.update_totals()  # ✅ auto-recalculate totals

    @property
    def item_total(self):
        return (self.quantity or 0) * (self.price or 0)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

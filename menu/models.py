from django.db import models
from decimal import Decimal
class Category(models.Model):
    """Menu categories like Drinks, Main Course, Starters, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name




class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='menu_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)


    @property
    def profit(self):
        """Calculated automatically: selling price - cost price"""
        return self.price - self.cost_price

    def __str__(self):
        return self.name

    def unavailable_reason(self):
      missing = []
      for mi in self.ingredients.all():
        if mi.ingredient.current_stock < mi.required_quantity:
            missing.append(mi.ingredient.name)
      return ", ".join(missing) if missing else "Unknown"


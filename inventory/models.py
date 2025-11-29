from django.db import models
from menu.models import MenuItem


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=50, help_text="e.g. kg, L, pcs")
    quantity_in_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} {self.unit})"


class MenuItemIngredient(models.Model):
    """Link ingredients to menu items (e.g. 0.5 kg of chicken per dish)."""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('menu_item', 'ingredient')

    def __str__(self):
        return f"{self.menu_item.name} needs {self.quantity_required} {self.ingredient.unit} {self.ingredient.name}"


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Automatically update ingredient quantity on save."""
        if self.pk is None:  # only adjust on first save
            if self.transaction_type == 'IN':
                self.ingredient.quantity_in_stock += self.quantity
            elif self.transaction_type == 'OUT':
                self.ingredient.quantity_in_stock -= self.quantity
            self.ingredient.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.quantity} {self.ingredient.unit} {self.ingredient.name}"

from django.db import models
from menu.models import MenuItem  # make sure this import works


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    quantity_in_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, help_text="e.g. kg, L, pcs")
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=5)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level


class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity_required} {self.ingredient.unit} of {self.ingredient.name} for {self.menu_item.name}"


class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('ADD', 'Added'),
        ('REMOVE', 'Removed'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.ingredient.unit} of {self.ingredient.name}"

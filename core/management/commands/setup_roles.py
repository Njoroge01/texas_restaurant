from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps

class Command(BaseCommand):
    help = "Setup default staff roles with permissions"

    def handle(self, *args, **kwargs):
        roles = {
            "Manager": {
                "permissions": Permission.objects.all(),
            },
            "Cashier": {
                "permissions": [
                    "add_order", "change_order", "view_order",
                    "add_orderitem", "change_orderitem", "view_orderitem",
                ]
            },
            "Waiter": {
                "permissions": [
                    "add_order", "view_order",
                ]
            },
            "Kitchen": {
                "permissions": [
                    "view_order", "change_order",
                ]
            }
        }

        for role_name, data in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            group.permissions.clear()
            for perm in data["permissions"]:
                if isinstance(perm, str):
                    app_label, codename = perm.split("_", 1)
                    perm_obj = Permission.objects.filter(codename=perm).first()
                else:
                    perm_obj = perm
                if perm_obj:
                    group.permissions.add(perm_obj)

        self.stdout.write(self.style.SUCCESS("✅ Roles and permissions configured successfully!"))

from django.http import JsonResponse
from menu.models import MenuItem

def get_item_price(request, item_id):
    try:
        item = MenuItem.objects.get(id=item_id)
        return JsonResponse({"price": float(item.price)})
    except MenuItem.DoesNotExist:
        return JsonResponse({"price": 0})

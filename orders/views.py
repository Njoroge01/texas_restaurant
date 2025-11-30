import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.utils.timezone import localdate, now
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.urls import reverse
from django.views.decorators.http import require_POST

from menu.models import MenuItem
from .models import Order, OrderItem


from itertools import groupby

# ✅ POS View - Group items by category in backend
def pos_view(request, table_id=None):
    table = None
    if table_id:
        table = get_object_or_404(Table, id=table_id)

    # Prevent ordering on an already occupied table
    if table and table.status != "available":
        return HttpResponse("❌ This table is currently occupied. Please choose another table.")

    # ✅ Order menu items by category name for grouping cleanly
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category').order_by('category__name')

    # ✅ Group by category in Python
    grouped_items = {}
    for category, items in groupby(menu_items, key=lambda m: m.category):
        grouped_items[category] = list(items)

    return render(request, 'orders/pos.html', {
        'grouped_items': grouped_items,
        'table': table,
    })


@csrf_exempt
@require_POST
def submit_order(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    table_id = request.GET.get("table_id")
    table = get_object_or_404(Table, id=table_id)

    customer_name = data.get("customerName", "")
    items = data.get("items", [])
    subtotal = Decimal(data.get("subtotal", 0))
    tax = Decimal(data.get("tax", 0))
    discount = Decimal(data.get("discount", 0))
    total = Decimal(data.get("total", 0))

    if not items:
        return JsonResponse({"success": False, "error": "Cart is empty"})

    # ✅ Create the order
    order = Order.objects.create(
        table=table,
        table_number=table.number,
        waiter=request.user if request.user.is_authenticated else None,
        customer_name=customer_name,
        subtotal=subtotal,
        tax=tax,
        discount=discount,
        total=total,
        status="pending",
        is_paid=False,
    )

    # ✅ Add items to the order
    for item in items:
        menu_item = MenuItem.objects.get(id=item["id"])
        OrderItem.objects.create(
            order=order,
            item=menu_item,
            quantity=item["quantity"],
            price=menu_item.price
        )

    # ✅ Recalculate totals after items added
    order.update_totals()

    # ✅ Mark table as OCCUPIED
    table.status = "occupied"
    table.save()

    return JsonResponse({
        "success": True,
        "order_id": order.id,
        "order_url": reverse("orders:receipt", args=[order.id]),
    })

def update_item_availability():
    for menu_item in MenuItem.objects.all():
        ingredients = menu_item.menuitemingredient_set.all()

        # If ANY ingredient doesn't have enough stock → unavailable
        if any(ing.ingredient.stock <= 0 for ing in ingredients):
            menu_item.is_available = False
        else:
            menu_item.is_available = True

        menu_item.save()



# ✅ Price Lookup API
def get_price(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return JsonResponse({"price": float(item.price)})


# ✅ Receipt Page
def receipt_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/receipt.html", {"order": order})


# ✅ Print Receipt (PDF)
def print_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{order.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Texas Restaurant")
    y -= 20
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Order #{order.id}")
    y -= 25

    for item in items:
        pdf.drawString(50, y, item.menu_item.name[:35])
        pdf.drawString(350, y, str(item.quantity))
        pdf.drawString(400, y, f"{item.price:.2f}")
        pdf.drawString(460, y, f"{item.item_total:.2f}")
        y -= 15

    y -= 15
    pdf.drawString(50, y, f"Total KES: {order.total:.2f}")

    pdf.save()
    return response


# ✅ Staff-only decorator
def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


# ===============================
# ✅ Kitchen Display
# ===============================
@login_required
@staff_required
def kitchen_display(request):
    pending_orders = Order.objects.filter(status="pending").order_by("-created_at")
    in_progress_orders = Order.objects.filter(status="in_progress").order_by("-created_at")
    ready_orders = Order.objects.filter(status="ready").order_by("-created_at")

    return render(request, "orders/kitchen_display.html", {
        "pending_orders": pending_orders,
        "in_progress_orders": in_progress_orders,
        "ready_orders": ready_orders,
    })



def kitchen_data(request):
    pending = Order.objects.filter(status="pending").order_by("-created_at")
    in_progress = Order.objects.filter(status="in_progress").order_by("-created_at")
    ready = Order.objects.filter(status="ready").order_by("-created_at")

    def serialize(order):
        return {
            "id": order.id,
            "customer_name": order.customer_name,
            "table_number": order.table_number,
            "total": str(order.total),
        }

    return JsonResponse({
        "pending": [serialize(o) for o in pending],
        "in_progress": [serialize(o) for o in in_progress],
        "ready": [serialize(o) for o in ready],
    })


@csrf_exempt
def advance_status(request, pk):
    order = get_object_or_404(Order, pk=pk)

    next_state = {
        "pending": "in_progress",
        "in_progress": "ready",
        "ready": "completed",
    }
    order.status = next_state.get(order.status, "pending")
    order.save(update_fields=["status"])

    return JsonResponse({"success": True, "new_status": order.status})

@csrf_exempt
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")

    if new_status not in ["pending", "in_progress", "ready"]:
        return JsonResponse({"success": False, "error": "Invalid status"})

    order.status = new_status
    order.save()

    return JsonResponse({"success": True})

def daily_sales_report(request):
    today = localdate()

    orders_today = Order.objects.filter(
    created_at__date=today,
    status="completed",
    is_paid=True
)


    total_orders = orders_today.count()
    total_revenue = orders_today.aggregate(
        total=Sum("paid_amount")  # ✅ use paid revenue
    )["total"] or 0

    payment_summary = orders_today.values(
        "payment_method"
    ).annotate(
        total=Sum("paid_amount"),
        count=Count("id"),
    )

    avg_order_value = total_revenue / total_orders if total_orders else 0

    return render(request, "orders/daily_sales.html", {
        "orders_today": orders_today,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_order_value": round(avg_order_value, 2),
        "payment_summary": payment_summary,
        "today": today,
    })

from .models import Table
from django.shortcuts import render
def customer_table_select(request):
    tables = Table.objects.filter(status="available").order_by("number")
    return render(request, "orders/select_table.html", {"tables": tables})

from .models import Order, OrderItem, Table, MenuItem
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Table, Order, OrderItem, MenuItem


import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Order, OrderItem, MenuItem, Table

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json
from .models import Order, OrderItem, Table, MenuItem

@csrf_exempt
def submit_order(request):
    """Handles POS order submission and assigns items to the kitchen system."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # ✅ Step 1: Decode JSON body safely
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    # ✅ Step 2: Get table info
    table_id = request.GET.get("table_id")
    if not table_id:
        return JsonResponse({"error": "Missing table_id parameter"}, status=400)

    table = get_object_or_404(Table, id=table_id)

    # ✅ Step 3: Create Order
    try:
        order = Order.objects.create(
            table=table,
            table_number=table.number,
            customer_name=data.get("customerName", "Walk-in"),
            subtotal=Decimal(data.get("subtotal", 0)),
            tax=Decimal(data.get("tax", 0)),
            discount=Decimal(data.get("discount", 0)),
            total=Decimal(data.get("total", 0)),
            status="pending",
            is_paid=False,  # Ensures daily report separation
        )
    except Exception as e:
        return JsonResponse({"error": f"Failed to create order: {str(e)}"}, status=500)

    # ✅ Step 4: Add order items
    items = data.get("items", [])
    if not items:
        order.delete()  # cleanup empty order
        return JsonResponse({"error": "No items in cart"}, status=400)

    for item_data in items:
        try:
            menu_item = MenuItem.objects.get(id=item_data["id"])
            quantity = int(item_data.get("quantity", 1))
        except (MenuItem.DoesNotExist, KeyError, ValueError):
            continue  # skip malformed item data

        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=quantity,
            price=Decimal(menu_item.price)
        )

    # ✅ Step 5: Update Table status
    table.status = "occupied"
    table.save()

    # ✅ Step 6: Send response
    return JsonResponse({
        "success": True,
        "order_id": order.id,
        "message": f"Order #{order.id} submitted successfully!"
    })







@csrf_exempt
def submit_payment(request, order_id):
    """Marks an order as paid and frees up the table."""
    order = get_object_or_404(Order, id=order_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    payment_method = data.get("payment_method", "cash")

    # ✅ Update order
    order.payment_method = payment_method
    order.is_paid = True
    order.status = "completed"
    order.paid_amount = order.total
    order.save()

    # ✅ Release table
    if order.table:
        order.table.status = "available"
        order.table.save()

    return JsonResponse({
        "success": True,
        "message": f"Payment successful for Order #{order.id} via {payment_method}"
    })







from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Order, Table

# ✅ Payment System
from django.views.decorators.csrf import csrf_exempt
import json

def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/payment.html", {"order": order})


@csrf_exempt
def submit_payment(request, order_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})

    order = get_object_or_404(Order, id=order_id)

    import json
    data = json.loads(request.body)
    payment_method = data.get("payment_method")

    if not payment_method:
        return JsonResponse({"success": False, "error": "No payment method provided"})

    # ✅ Update payment + status
    order.payment_method = payment_method
    order.status = "paid"  # ✅ IMPORTANT FOR SALES REPORT
    order.paid_amount = order.total  # ✅ mark revenue as paid
    order.save()

    return JsonResponse({
        "success": True,
        "receipt_url": reverse("orders:receipt", args=[order.id])
    })



from django.shortcuts import render

# existing imports and views here...

def orders_list(request):
    return render(request, "orders/orders_list.html")


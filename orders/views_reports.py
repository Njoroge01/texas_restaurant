from django.shortcuts import render
from django.utils.timezone import localdate
from decimal import Decimal
from .models import Order  # ✅ Single correct import

def daily_sales_report(request):
    today = localdate()

    # ✅ Filter orders: Completed + Paid
    orders_today = Order.objects.filter(
        created_at__date=today,
        status="completed",
        is_paid=True
    )

    # ✅ Calculations
    total_orders = orders_today.count()
    total_revenue = sum(o.total for o in orders_today)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # ✅ Payment method summary
    payments = {}
    for order in orders_today:
        method = order.payment_method or "Unknown"
        if method not in payments:
            payments[method] = {"count": 0, "total": Decimal("0.00")}
        payments[method]["count"] += 1
        payments[method]["total"] += order.total

    # ✅ Debug output to terminal
    print("\n✅ DEBUG — Orders Today:")
    print(orders_today.values_list(
        "id", "created_at", "status", "is_paid", "payment_method"
    ))
    print("Total:", total_revenue, "Orders:", total_orders)

    return render(request, "orders/daily_sales.html", {
        "orders_today": orders_today,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "payments": payments,
        "today": today,
    })
from django.shortcuts import render
from django.utils.timezone import localdate
from orders.models import Order

def daily_sales_report(request):
    today = localdate()
    orders_today = Order.objects.filter(status="paid", created_at__date=today)

    total_orders = orders_today.count()
    total_revenue = sum(o.total for o in orders_today) if total_orders > 0 else 0
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0

    # group payment breakdown
    payments = {}
    for order in orders_today:
        method = order.payment_method or "unknown"
        if method not in payments:
            payments[method] = {"count": 0, "total": 0}
        payments[method]["count"] += 1
        payments[method]["total"] += order.total

    context = {
        "orders_today": orders_today,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "payments": payments,
        "today": today
    }

    return render(request, "orders/daily_sales.html", context)

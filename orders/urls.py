from django.urls import path
from .views import (
    pos_view, submit_order, get_price, receipt_view, print_receipt,
    kitchen_display, kitchen_data, advance_status, customer_table_select,
    update_order_status, payment_view, submit_payment, orders_list, 
)
from .views_ajax import get_item_price
from .views_reports import daily_sales_report
from .views_customer import customer_menu

app_name = 'orders'

urlpatterns = [
    # Kitchen
    path("kitchen/", kitchen_display, name="kitchen_display"),
    path("kitchen/data/", kitchen_data, name="kitchen_data"),
    path("kitchen/order/<int:pk>/advance/", advance_status, name="advance_status"),

    # Customer menu
    path("menu/<int:table_number>/", customer_menu, name="customer_menu"),

    # POS System
    path("tables/", customer_table_select, name="select_table"),
    path("pos/", pos_view, name="pos"),
    path("pos/<int:table_id>/", pos_view, name="pos_with_table"),
    path("submit-order/", submit_order, name="submit_order"),

    # Item price API
    path("get-price/<int:item_id>/", get_price, name="get_price"),
    path("api/item-price/<int:item_id>/", get_item_price, name="item_price"),

    # Receipt
    path('receipt/<int:order_id>/', receipt_view, name='receipt'),
    path("print/<int:order_id>/", print_receipt, name="print_receipt"),

    # Daily Sales
    path("reports/daily-sales/", daily_sales_report, name="daily_sales"),

    # Payment
    path("pay/<int:order_id>/", payment_view, name="order_payment"),
    path("pay/<int:order_id>/submit/", submit_payment, name="submit_payment"),

    # orders/urls.py
path("list/", orders_list, name="orders_list"),
]

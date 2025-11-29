from django.urls import path
from . import views

urlpatterns = [
    path('receipt/<int:invoice_id>/', views.view_receipt, name='view_receipt'),
    path('receipt/<int:invoice_id>/pdf/', views.download_receipt, name='download_receipt'),

]

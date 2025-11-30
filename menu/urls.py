from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("", views.home, name="home"),  # homepage
    path("list/", views.menu_list, name="menu_list"),
]

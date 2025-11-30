from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'menu/home.html')

def menu_list(request):
    return HttpResponse("Menu will be listed here")

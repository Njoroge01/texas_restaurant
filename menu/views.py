from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'menu/home.html')

def menu_list(request):
    return HttpResponse("Menu will be listed here")

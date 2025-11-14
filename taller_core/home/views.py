# taller_core/home/views.py
from django.shortcuts import render

def welcome_page(request):
    """
    Vista para la página de bienvenida que se muestra antes del login.
    """
    return render(request, "home/welcome_page.html")

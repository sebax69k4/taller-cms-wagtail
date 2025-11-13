# taller_core/gestion/urls.py

from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    path('asignar/', views.asignar_trabajo, name='asignar_trabajo'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
]

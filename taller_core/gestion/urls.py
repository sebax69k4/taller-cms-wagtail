# taller_core/gestion/urls.py

from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_view, name='dashboard'),
    
    # UC-001: Registrar Cliente
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/registrar/', views.registrar_cliente, name='registrar_cliente'),
    
    # UC-002: Registrar Vehículo
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/registrar/', views.registrar_vehiculo, name='registrar_vehiculo'),
    
    # HU003: Lista y detalle de órdenes
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    
    # UC-004: Asignar Técnico (HU002)
    path('asignar/', views.asignar_trabajo, name='asignar_trabajo'),
    
    # HU002: Ver disponibilidad
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    
    # UC-006: Actualizar Estado
    path('ordenes/<int:pk>/estado/', views.actualizar_estado_orden, name='actualizar_estado'),
    
    # UC-007: Generar Factura (Pendiente)
    path('ordenes/<int:pk>/factura/', views.generar_factura, name='generar_factura'),

        # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal (redirige según rol)
    path('', views.mi_dashboard, name='dashboard'),
    
    # Listas
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    
    # HU002
    path('asignar/', views.asignar_trabajo, name='asignar_trabajo'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    
    # API
    path('ordenes/<int:pk>/estado/', views.actualizar_estado_orden, name='actualizar_estado'),
]

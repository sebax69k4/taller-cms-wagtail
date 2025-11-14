# taller_core/gestion/urls.py
from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal (redirige según rol)
    path('', views.mi_dashboard, name='dashboard'),
    
    # UC-001 & UC-002: Listas y registros
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/registrar/', views.registrar_vehiculo, name='registrar_vehiculo'),
    
    # HU003: Lista y detalle de órdenes
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    
    # HU002: Asignación y Disponibilidad
    path('asignar/', views.asignar_trabajo, name='asignar_trabajo'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    
    # API y Acciones
    path('ordenes/<int:pk>/estado/', views.actualizar_estado_orden, name='actualizar_estado'),
    path('ordenes/<int:pk>/factura/', views.generar_factura, name='generar_factura'),
]

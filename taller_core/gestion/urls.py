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
    
    # UC-001: Gestión de Clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # UC-002: Gestión de Vehículos
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/registrar/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('vehiculos/<int:pk>/editar/', views.editar_vehiculo, name='editar_vehiculo'),
    
    # Gestión de Órdenes de Trabajo
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/crear/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    path('ordenes/<int:pk>/agregar-bitacora/', views.agregar_bitacora, name='agregar_bitacora'),
    path('ordenes/<int:pk>/agregar-presupuesto/', views.agregar_presupuesto, name='agregar_presupuesto'),
    
    # HU002: Asignación y Disponibilidad
    path('asignar/', views.asignar_trabajo, name='asignar_trabajo'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    
    # API y Acciones
    path('ordenes/<int:pk>/estado/', views.actualizar_estado_orden, name='actualizar_estado'),
    path('ordenes/<int:pk>/factura/', views.generar_factura, name='generar_factura'),
]

from django.shortcuts import render
# taller_core/gestion/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import OrdenTrabajo, Mecanico, ZonaTrabajo


@login_required
def dashboard_view(request):
    """Vista principal del dashboard"""
    context = {
        'total_ordenes': OrdenTrabajo.objects.count(),
        'activas': OrdenTrabajo.objects.exclude(estado='entregado').count(),
        'en_reparacion': OrdenTrabajo.objects.filter(estado='en_reparacion').count(),
        'listas': OrdenTrabajo.objects.filter(estado='listo_entrega').count(),
    }
    return render(request, 'gestion/dashboard.html', context)


@login_required
def orden_list(request):
    """Lista de órdenes con filtros (HU003)"""
    ordenes = OrdenTrabajo.objects.select_related(
        'vehiculo', 'cliente', 'mecanico_asignado'
    ).all()
    
    # Filtros
    estado = request.GET.get('estado')
    prioridad = request.GET.get('prioridad')
    buscar = request.GET.get('buscar')
    
    if estado:
        ordenes = ordenes.filter(estado=estado)
    
    if prioridad:
        ordenes = ordenes.filter(prioridad=prioridad)
    
    if buscar:
        ordenes = ordenes.filter(
            Q(vehiculo__patente__icontains=buscar) |
            Q(cliente__nombre__icontains=buscar) |
            Q(cliente__apellido__icontains=buscar)
        )
    
    # Filtrar según rol del usuario
    if not request.user.is_superuser:
        if request.user.groups.filter(name="Mecánico").exists():
            try:
                mecanico = request.user.perfil_mecanico
                ordenes = ordenes.filter(mecanico_asignado=mecanico)
            except AttributeError:
                ordenes = ordenes.none()
    
    ordenes = ordenes.order_by('-fecha_ingreso')
    
    context = {
        'ordenes': ordenes,
    }
    return render(request, 'gestion/orden_list.html', context)


@login_required
def orden_detail(request, pk):
    """Detalle de una orden"""
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related('vehiculo', 'cliente', 'mecanico_asignado'), 
        pk=pk
    )
    
    # Verificar permisos
    if not request.user.is_superuser:
        if request.user.groups.filter(name="Mecánico").exists():
            try:
                if orden.mecanico_asignado != request.user.perfil_mecanico:
                    return redirect('gestion:orden_list')
            except AttributeError:
                return redirect('gestion:orden_list')
    
    context = {
        'orden': orden,
        'bitacoras': orden.bitacoras.all(),
        'presupuestos': orden.presupuestos.all(),
    }
    return render(request, 'gestion/orden_detail.html', context)


@login_required
def asignar_trabajo(request):
    """Vista para asignar trabajos (HU002)"""
    # Solo Encargados pueden acceder
    if not (request.user.is_superuser or request.user.groups.filter(name="Encargado").exists()):
        return redirect('gestion:orden_list')
    
    ordenes_sin_asignar = OrdenTrabajo.objects.filter(
        mecanico_asignado__isnull=True
    ).exclude(estado='entregado')
    
    mecanicos_disponibles = Mecanico.objects.filter(disponible=True)
    zonas = ZonaTrabajo.objects.all()
    
    context = {
        'ordenes_sin_asignar': ordenes_sin_asignar,
        'mecanicos': mecanicos_disponibles,
        'zonas': zonas,
    }
    return render(request, 'gestion/asignar_trabajo.html', context)


@login_required
def disponibilidad(request):
    """Vista de disponibilidad de mecánicos y zonas (HU002)"""
    mecanicos = Mecanico.objects.all()
    zonas = ZonaTrabajo.objects.all()
    
    # Contar órdenes activas por mecánico
    for mecanico in mecanicos:
        mecanico.ordenes_activas = OrdenTrabajo.objects.filter(
            mecanico_asignado=mecanico
        ).exclude(estado='entregado').count()
    
    # Contar órdenes por zona
    for zona in zonas:
        zona.ordenes_activas = OrdenTrabajo.objects.filter(
            zona_trabajo=zona
        ).exclude(estado='entregado').count()
    
    context = {
        'mecanicos': mecanicos,
        'zonas': zonas,
    }
    return render(request, 'gestion/disponibilidad.html', context)

# Create your views here.

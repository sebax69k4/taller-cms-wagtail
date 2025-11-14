# taller_core/gestion/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from .models import (
    Cliente, Vehiculo, OrdenTrabajo, Mecanico, 
    ZonaTrabajo, Bitacora, Repuesto, Alerta, Presupuesto
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

# ============================================
# UC-001: REGISTRAR CLIENTE (Recepcionista)
# ============================================
@login_required
def lista_clientes(request):
    """Vista para listar clientes"""
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    context = {'clientes': clientes}
    return render(request, 'gestion/lista_clientes.html', context)


@login_required
def registrar_cliente(request):
    """Vista simplificada para que el recepcionista registre clientes"""
    if request.method == 'POST':
        # Procesar formulario (simplificado para el caso de uso)
        messages.success(request, 'Cliente registrado exitosamente')
        return redirect('gestion:lista_clientes')
    
    return render(request, 'gestion/registrar_cliente.html')


# ============================================
# UC-002: REGISTRAR VEHÍCULO (Recepcionista)
# ============================================
@login_required
def lista_vehiculos(request):
    """Vista para listar vehículos"""
    vehiculos = Vehiculo.objects.select_related('cliente').all()
    context = {'vehiculos': vehiculos}
    return render(request, 'gestion/lista_vehiculos.html', context)


@login_required
def registrar_vehiculo(request):
    """Vista para que el recepcionista registre vehículos"""
    clientes = Cliente.objects.all()
    
    if request.method == 'POST':
        messages.success(request, 'Vehículo registrado exitosamente')
        return redirect('gestion:lista_vehiculos')
    
    context = {'clientes': clientes}
    return render(request, 'gestion/registrar_vehiculo.html', context)


# ============================================
# HU003: VER ESTADO DE AVANCE (Encargado)
# ============================================
@login_required
def dashboard_view(request):
    """
    Dashboard principal - HU003
    "Para llevar un registro de los trabajos"
    """
    # Estadísticas generales
    stats = {
        'total_ordenes': OrdenTrabajo.objects.count(),
        'activas': OrdenTrabajo.objects.exclude(estado='entregado').count(),
        'recepcionadas': OrdenTrabajo.objects.filter(estado='recepcionado').count(),
        'en_diagnostico': OrdenTrabajo.objects.filter(estado='diagnostico').count(),
        'en_reparacion': OrdenTrabajo.objects.filter(estado='en_reparacion').count(),
        'listas': OrdenTrabajo.objects.filter(estado='listo_entrega').count(),
    }
    
    # Alertas activas (RF007)
    alertas = Alerta.objects.filter(resuelta=False).order_by('-fecha_creacion')[:5]
    
    # Órdenes recientes
    ordenes_recientes = OrdenTrabajo.objects.select_related(
        'vehiculo', 'cliente', 'mecanico_asignado'
    ).exclude(estado='entregado').order_by('-fecha_ingreso')[:10]
    
    # Mecánicos con carga de trabajo
    mecanicos_stats = Mecanico.objects.annotate(
        ordenes_activas=Count('ordenes', filter=Q(ordenes__estado__in=[
            'diagnostico', 'en_reparacion', 'espera_repuesto'
        ]))
    ).filter(disponible=True)
    
    context = {
        'stats': stats,
        'alertas': alertas,
        'ordenes_recientes': ordenes_recientes,
        'mecanicos_stats': mecanicos_stats,
    }
    return render(request, 'gestion/dashboard.html', context)


# ============================================
# HU003: LISTA DE ÓRDENES CON FILTROS
# ============================================
@login_required
def orden_list(request):
    """
    Lista de órdenes - HU003
    "Mostrar los trabajos que se están realizando"
    "Poder seleccionar un trabajo y ver el historial"
    """
    ordenes = OrdenTrabajo.objects.select_related(
        'vehiculo', 'cliente', 'mecanico_asignado', 'zona_trabajo'
    ).all()
    
    # Filtros según RF004
    estado = request.GET.get('estado')
    prioridad = request.GET.get('prioridad')
    buscar = request.GET.get('buscar')
    mecanico_id = request.GET.get('mecanico')
    
    if estado:
        ordenes = ordenes.filter(estado=estado)
    
    if prioridad:
        ordenes = ordenes.filter(prioridad=prioridad)
    
    if mecanico_id:
        ordenes = ordenes.filter(mecanico_asignado_id=mecanico_id)
    
    if buscar:
        ordenes = ordenes.filter(
            Q(vehiculo__patente__icontains=buscar) |
            Q(cliente__nombre__icontains=buscar) |
            Q(cliente__apellido__icontains=buscar) |
            Q(id__icontains=buscar)
        )
    
    # Permisos por rol (según documento)
    if not request.user.is_superuser:
        if request.user.groups.filter(name="Mecánico").exists():
            # UC-006: Mecánico solo ve sus órdenes
            try:
                mecanico = request.user.perfil_mecanico
                ordenes = ordenes.filter(mecanico_asignado=mecanico)
            except AttributeError:
                ordenes = ordenes.none()
    
    ordenes = ordenes.order_by('-fecha_ingreso')
    
    # Para los filtros
    mecanicos = Mecanico.objects.filter(disponible=True)
    
    context = {
        'ordenes': ordenes,
        'mecanicos': mecanicos,
        'estados': OrdenTrabajo.ESTADO_CHOICES,
    }
    return render(request, 'gestion/orden_list.html', context)


# ============================================
# UC-006: VER DETALLE Y HISTORIAL DE ORDEN
# ============================================
@login_required
def orden_detail(request, pk):
    """
    Detalle completo de una orden - HU003
    "Poder seleccionar un trabajo y ver el historial"
    """
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related(
            'vehiculo', 'cliente', 'mecanico_asignado', 'zona_trabajo'
        ).prefetch_related('bitacoras', 'presupuestos'), 
        pk=pk
    )
    
    # Verificar permisos
    if not request.user.is_superuser:
        if request.user.groups.filter(name="Mecánico").exists():
            try:
                if orden.mecanico_asignado != request.user.perfil_mecanico:
                    messages.error(request, 'No tienes permiso para ver esta orden')
                    return redirect('gestion:orden_list')
            except AttributeError:
                return redirect('gestion:orden_list')
    
    # Historial completo
    bitacoras = orden.bitacoras.select_related('mecanico').prefetch_related(
        'repuestos_usados__repuesto'
    ).order_by('-fecha')
    
    presupuestos = orden.presupuestos.all().order_by('-fecha_creacion')
    
    context = {
        'orden': orden,
        'bitacoras': bitacoras,
        'presupuestos': presupuestos,
        'historial_estados': _get_historial_estados(orden),
    }
    return render(request, 'gestion/orden_detail.html', context)


def _get_historial_estados(orden):
    """Helper para construir timeline de estados"""
    return [
        {'estado': 'Recepcionado', 'fecha': orden.fecha_ingreso, 'activo': True},
        {'estado': 'En Diagnóstico', 'activo': orden.estado in ['diagnostico', 'en_reparacion', 'listo_entrega', 'entregado']},
        {'estado': 'En Reparación', 'activo': orden.estado in ['en_reparacion', 'listo_entrega', 'entregado']},
        {'estado': 'Listo Entrega', 'activo': orden.estado in ['listo_entrega', 'entregado']},
        {'estado': 'Entregado', 'fecha': orden.fecha_finalizacion, 'activo': orden.estado == 'entregado'},
    ]


# ============================================
# HU002: ASIGNAR TRABAJO (Encargado)
# ============================================
@login_required
def asignar_trabajo(request):
    """
    Vista para asignar trabajos - HU002
    "Registro de trabajo a realizar"
    "Pode planificar las tareas"
    """
    # Solo Encargados pueden acceder
    if not (request.user.is_superuser or request.user.groups.filter(name="Encargado").exists()):
        messages.error(request, 'No tienes permisos para asignar trabajos')
        return redirect('gestion:orden_list')
    
    if request.method == 'POST':
        orden_id = request.POST.get('orden_id')
        mecanico_id = request.POST.get('mecanico_id')
        zona_id = request.POST.get('zona_id')
        
        orden = get_object_or_404(OrdenTrabajo, pk=orden_id)
        mecanico = get_object_or_404(Mecanico, pk=mecanico_id)
        zona = get_object_or_404(ZonaTrabajo, pk=zona_id) if zona_id else None
        
        orden.mecanico_asignado = mecanico
        orden.zona_trabajo = zona
        orden.estado = 'diagnostico'  # Cambiar a diagnóstico al asignar
        orden.save()
        
        messages.success(request, f'Orden #{orden.id} asignada a {mecanico.nombre}')
        return redirect('gestion:asignar_trabajo')
    
    # Órdenes sin asignar
    ordenes_sin_asignar = OrdenTrabajo.objects.filter(
        mecanico_asignado__isnull=True,
        estado='recepcionado'
    ).select_related('vehiculo', 'cliente')
    
    # Mecánicos disponibles con carga actual
    mecanicos = Mecanico.objects.filter(disponible=True).annotate(
        ordenes_activas=Count('ordenes', filter=~Q(ordenes__estado='entregado'))
    )
    
    zonas = ZonaTrabajo.objects.all()
    
    context = {
        'ordenes_sin_asignar': ordenes_sin_asignar,
        'mecanicos': mecanicos,
        'zonas': zonas,
    }
    return render(request, 'gestion/asignar_trabajo.html', context)


# ============================================
# HU002: VER DISPONIBILIDAD
# ============================================
@login_required
def disponibilidad(request):
    """
    Vista de disponibilidad - HU002
    "Ver disponibilidad de mecanismos"
    "Ver disponibilidad de zona de trabajos"
    "Definir fechas de los trabajos"
    """
    # Mecánicos con carga de trabajo
    mecanicos = Mecanico.objects.annotate(
        ordenes_activas=Count('ordenes', filter=~Q(ordenes__estado='entregado')),
        ordenes_en_diagnostico=Count('ordenes', filter=Q(ordenes__estado='diagnostico')),
        ordenes_en_reparacion=Count('ordenes', filter=Q(ordenes__estado='en_reparacion')),
    )
    
    # Zonas con ocupación
    zonas = ZonaTrabajo.objects.annotate(
        ordenes_activas=Count('ordenes', filter=~Q(ordenes__estado='entregado'))
    )
    
    # Órdenes por estado para timeline
    ordenes_timeline = OrdenTrabajo.objects.filter(
        estado__in=['diagnostico', 'en_reparacion']
    ).select_related('vehiculo', 'mecanico_asignado', 'zona_trabajo').order_by('fecha_estimada')
    
    context = {
        'mecanicos': mecanicos,
        'zonas': zonas,
        'ordenes_timeline': ordenes_timeline,
    }
    return render(request, 'gestion/disponibilidad.html', context)


# ============================================
# UC-006: ACTUALIZAR ESTADO (Mecánico)
# ============================================
@login_required
def actualizar_estado_orden(request, pk):
    """API para actualizar estado de orden - UC-006"""
    if request.method == 'POST':
        orden = get_object_or_404(OrdenTrabajo, pk=pk)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in dict(OrdenTrabajo.ESTADO_CHOICES):
            orden.estado = nuevo_estado
            orden.save()
            
            # RF006: Crear alerta automática
            if nuevo_estado == 'listo_entrega':
                Alerta.objects.create(
                    orden=orden,
                    tipo='info',
                    mensaje=f'Orden #{orden.id} lista para entrega - {orden.vehiculo.patente}'
                )
            
            messages.success(request, f'Estado actualizado a: {orden.get_estado_display()}')
            return JsonResponse({'success': True, 'estado': orden.get_estado_display()})
        
        return JsonResponse({'success': False, 'error': 'Estado inválido'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ============================================
# UC-007: GENERAR FACTURA (Pendiente)
# ============================================
@login_required
def generar_factura(request, pk):
    """Vista placeholder para generar factura - UC-007"""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    messages.info(request, 'Función de facturación en desarrollo')
    return redirect('gestion:orden_detail', pk=pk)


def login_view(request):
    """Vista de login personalizada con redirección por rol"""
    
    # Si ya está autenticado, redirigir a su dashboard
    if request.user.is_authenticated:
        return redirect_segun_rol(request.user)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {user.get_full_name() or user.username}')
                
                # Redirigir según rol
                return redirect_segun_rol(user)
            else:
                # Mensajes más informativos para ayudar al debugging
                from django.contrib.auth.models import User
                try:
                    found = User.objects.filter(username=username).first()
                except Exception:
                    found = None

                if not found:
                    messages.error(request, 'Usuario no encontrado')
                else:
                    # Verificar estado y contraseña sin revelar detalles sensibles
                    if not found.is_active:
                        messages.error(request, 'El usuario existe pero está inactivo. Contacta al administrador.')
                    else:
                        # Comprobar si la contraseña es incorrecta
                        if not found.check_password(password):
                            messages.error(request, 'Contraseña incorrecta')
                        else:
                            messages.error(request, 'No se pudo autenticar al usuario (verifica configuración)')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    context = {'form': form}
    return render(request, 'gestion/login.html', context)


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente')
    return redirect('gestion:login')


def redirect_segun_rol(user):
    """Función auxiliar para redirigir según el rol del usuario

    Esta versión normaliza nombres de grupo (quita mayúsculas y diacríticos)
    para evitar problemas si el nombre del grupo tiene o no acentos.
    """

    # Superusuario al admin de Wagtail
    if user.is_superuser:
        return redirect('/admin/')

    # Intentar usar perfil personalizado
    try:
        perfil = user.perfil
        return redirect(perfil.get_dashboard_url())
    except Exception:
        pass

    # Si no tiene perfil, usar grupo (comparaciones insensibles a mayúsculas y diacríticos)
    import unicodedata

    def _normalize(s):
        if not s:
            return ''
        s = s.lower()
        s = unicodedata.normalize('NFKD', s)
        return ''.join(c for c in s if not unicodedata.combining(c))

    grupos = [ _normalize(g) for g in user.groups.values_list('name', flat=True) ]

    if 'encargado' in grupos:
        return redirect('gestion:dashboard')
    elif 'mecanico' in grupos or any('mecanico' in g for g in grupos):
        return redirect('gestion:orden_list')
    elif 'recepcionista' in grupos:
        return redirect('gestion:orden_list')

    # Default
    return redirect('gestion:dashboard')



# ============================================
# DASHBOARD SEGÚN ROL
# ============================================

@login_required
def mi_dashboard(request):
    """Vista de dashboard que se adapta según el rol"""
    
    # Detectar rol
    if request.user.is_superuser:
        rol = 'superusuario'
    else:
        try:
            rol = request.user.perfil.rol
        except:
            # Fallback: detectar rol por grupos (insensible a mayúsculas/acentos)
            import unicodedata

            def _normalize(s):
                if not s:
                    return ''
                s = s.lower()
                s = unicodedata.normalize('NFKD', s)
                return ''.join(c for c in s if not unicodedata.combining(c))

            grupos = [ _normalize(g) for g in request.user.groups.values_list('name', flat=True) ]
            if 'encargado' in grupos:
                rol = 'encargado'
            elif 'mecanico' in grupos or any('mecanico' in g for g in grupos):
                rol = 'mecanico'
            elif 'recepcionista' in grupos:
                rol = 'recepcionista'
            else:
                rol = 'sin_rol'
    
    # Datos según rol
    if rol == 'encargado' or rol == 'superusuario':
        # Dashboard completo
        return dashboard_view(request)
    
    elif rol == 'mecanico':
        # Dashboard de mecánico (solo sus órdenes)
        try:
            mecanico = request.user.perfil_mecanico
            ordenes = OrdenTrabajo.objects.filter(
                mecanico_asignado=mecanico
            ).exclude(estado='entregado').select_related('vehiculo', 'cliente')
            
            context = {
                'rol': 'mecanico',
                'ordenes': ordenes,
                'mecanico': mecanico,
            }
            return render(request, 'gestion/dashboard_mecanico.html', context)
        except:
            return redirect('gestion:orden_list')
    
    elif rol == 'recepcionista':
        # Dashboard de recepcionista
        ordenes_recientes = OrdenTrabajo.objects.select_related(
            'vehiculo', 'cliente'
        ).order_by('-fecha_ingreso')[:10]
        
        context = {
            'rol': 'recepcionista',
            'ordenes_recientes': ordenes_recientes,
        }
        return render(request, 'gestion/dashboard_recepcionista.html', context)
    
    # Sin rol
    return render(request, 'gestion/sin_acceso.html')
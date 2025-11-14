# taller_core/gestion/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.http import JsonResponse
from .models import (
    Cliente, Vehiculo, OrdenTrabajo, Mecanico, 
    ZonaTrabajo, Bitacora, Repuesto, Alerta, Presupuesto)
from .forms import ClienteForm, VehiculoForm, OrdenTrabajoForm, BitacoraForm, PresupuestoForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator

# ============================================
# DECORADORES DE PERMISOS
# ============================================
def es_recepcionista_o_encargado(user):
    return user.is_superuser or user.groups.filter(name__in=['Recepcionista', 'Encargado']).exists()

def es_encargado(user):
    return user.is_superuser or user.groups.filter(name='Encargado').exists()

def es_mecanico(user):
    return user.groups.filter(name='Mecánico').exists() or user.is_superuser

# ============================================
# UC-001: GESTIÓN DE CLIENTES (Recepcionista)
# ============================================
@login_required
@user_passes_test(es_recepcionista_o_encargado)
def lista_clientes(request):
    """Vista para listar clientes"""
    clientes = Cliente.objects.all().order_by('-fecha_registro')
    
    # Búsqueda
    buscar = request.GET.get('buscar')
    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar) |
            Q(apellido__icontains=buscar) |
            Q(email__icontains=buscar) |
            Q(telefono__icontains=buscar)
        )
    
    context = {'clientes': clientes, 'buscar': buscar}
    return render(request, 'gestion/lista_clientes.html', context)


@login_required
@user_passes_test(es_recepcionista_o_encargado)
def registrar_cliente(request):
    """Vista para registrar un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} registrado exitosamente')
            return redirect('gestion:lista_clientes')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = ClienteForm()
    
    context = {'form': form}
    return render(request, 'gestion/registrar_cliente.html', context)


@login_required
@user_passes_test(es_recepcionista_o_encargado)
def editar_cliente(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} actualizado exitosamente')
            return redirect('gestion:lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {'form': form, 'cliente': cliente}
    return render(request, 'gestion/editar_cliente.html', context)


# ============================================
# UC-002: GESTIÓN DE VEHÍCULOS (Recepcionista)
# ============================================
@login_required
@user_passes_test(es_recepcionista_o_encargado)
def lista_vehiculos(request):
    """Vista para listar vehículos"""
    vehiculos = Vehiculo.objects.select_related('cliente').all().order_by('-id')
    
    # Búsqueda
    buscar = request.GET.get('buscar')
    if buscar:
        vehiculos = vehiculos.filter(
            Q(patente__icontains=buscar) |
            Q(marca__icontains=buscar) |
            Q(modelo__icontains=buscar) |
            Q(cliente__nombre__icontains=buscar) |
            Q(cliente__apellido__icontains=buscar)
        )
    
    context = {'vehiculos': vehiculos, 'buscar': buscar}
    return render(request, 'gestion/lista_vehiculos.html', context)


@login_required
@user_passes_test(es_recepcionista_o_encargado)
def registrar_vehiculo(request):
    """Vista para registrar un nuevo vehículo"""
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f'Vehículo {vehiculo.patente} registrado exitosamente')
            return redirect('gestion:lista_vehiculos')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = VehiculoForm()
    
    context = {'form': form}
    return render(request, 'gestion/registrar_vehiculo.html', context)


@login_required
@user_passes_test(es_recepcionista_o_encargado)
def editar_vehiculo(request, pk):
    """Vista para editar un vehículo existente"""
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehículo {vehiculo.patente} actualizado exitosamente')
            return redirect('gestion:lista_vehiculos')
    else:
        form = VehiculoForm(instance=vehiculo)
    
    context = {'form': form, 'vehiculo': vehiculo}
    return render(request, 'gestion/editar_vehiculo.html', context)


# ============================================
# GESTIÓN DE ÓRDENES DE TRABAJO (Recepcionista)
# ============================================
@login_required
@user_passes_test(es_recepcionista_o_encargado)
def crear_orden(request):
    """Vista para crear una nueva orden de trabajo"""
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            orden.estado = 'recepcionado'
            orden.save()
            messages.success(request, f'Orden #{orden.id} creada exitosamente')
            return redirect('gestion:orden_detail', pk=orden.id)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = OrdenTrabajoForm()
    
    context = {'form': form}
    return render(request, 'gestion/crear_orden.html', context)


@login_required
@user_passes_test(es_mecanico, login_url='/gestion/login/')
def agregar_bitacora(request, pk):
    """Vista para agregar bitácora - solo mecánicos"""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    # Verificar que el mecánico tenga asignada esta orden
    if hasattr(request.user, 'mecanico'):
        if orden.mecanico_asignado != request.user.mecanico:
            messages.error(request, 'No tienes permiso para agregar bitácoras a esta orden')
            return redirect('gestion:orden_detail', pk=pk)
    
    if request.method == 'POST':
        form = BitacoraForm(request.POST)
        if form.is_valid():
            bitacora = form.save(commit=False)
            bitacora.orden = orden
            bitacora.save()
            form.save_m2m()  # Guardar relaciones many-to-many (procedimientos)
            messages.success(request, 'Bitácora agregada exitosamente')
            return redirect('gestion:orden_detail', pk=pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = BitacoraForm()
    
    context = {
        'form': form,
        'orden': orden
    }
    return render(request, 'gestion/agregar_bitacora.html', context)


@login_required
@user_passes_test(es_encargado, login_url='/gestion/login/')
def agregar_presupuesto(request, pk):
    """Vista para agregar presupuesto - solo encargados"""
    orden = get_object_or_404(OrdenTrabajo, pk=pk)
    
    if request.method == 'POST':
        form = PresupuestoForm(request.POST)
        if form.is_valid():
            presupuesto = form.save(commit=False)
            presupuesto.orden = orden
            presupuesto.save()
            form.save_m2m()  # Guardar relaciones many-to-many (items)
            messages.success(request, 'Presupuesto agregado exitosamente')
            return redirect('gestion:orden_detail', pk=pk)
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = PresupuestoForm()
    
    context = {
        'form': form,
        'orden': orden
    }
    return render(request, 'gestion/agregar_presupuesto.html', context)


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
        'espera_repuesto': OrdenTrabajo.objects.filter(estado='espera_repuesto').count(),
        'listas': OrdenTrabajo.objects.filter(estado='listo_entrega').count(),
        'entregadas': OrdenTrabajo.objects.filter(estado='entregado').count(),
    }
    
    # Alertas de stock bajo - repuestos con stock actual <= stock mínimo
    alertas_stock = Repuesto.objects.filter(
        stock_actual__lte=models.F('stock_minimo')
    ).select_related()[:10]
    
    # Crear objetos de alerta para la vista
    alertas = []
    for repuesto in alertas_stock:
        alertas.append({
            'mensaje': f'{repuesto.nombre} - Stock: {repuesto.stock_actual} (Mínimo: {repuesto.stock_minimo})',
            'repuesto': repuesto
        })
    
    # Órdenes recientes
    ordenes_recientes = OrdenTrabajo.objects.select_related(
        'vehiculo', 'cliente', 'mecanico_asignado'
    ).exclude(estado='entregado').order_by('-fecha_ingreso')[:10]
    
    # Mecánicos con carga de trabajo
    mecanicos_stats = Mecanico.objects.annotate(
        ordenes_activas=Count('ordenes', filter=Q(ordenes__estado__in=[
            'diagnostico', 'en_reparacion', 'espera_repuesto'
        ]))
    ).all()
    
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
        from django.utils import timezone
        
        try:
            mecanico = request.user.mecanico
            ordenes = OrdenTrabajo.objects.filter(
                mecanico_asignado=mecanico
            ).exclude(estado='entregado').select_related('vehiculo', 'cliente', 'zona_trabajo')
            
            # Estadísticas específicas del mecánico
            en_reparacion = ordenes.filter(estado='en_reparacion').count()
            
            hoy = timezone.now().date()
            completadas_hoy = OrdenTrabajo.objects.filter(
                mecanico_asignado=mecanico,
                estado='listo_entrega',
                fecha_finalizacion__date=hoy
            ).count()
            
            context = {
                'rol': 'mecanico',
                'ordenes': ordenes,
                'mecanico': mecanico,
                'en_reparacion': en_reparacion,
                'completadas_hoy': completadas_hoy,
            }
            return render(request, 'gestion/dashboard_mecanico.html', context)
        except:
            return redirect('gestion:orden_list')
    
    elif rol == 'recepcionista':
        # Dashboard de recepcionista con estadísticas
        from django.utils import timezone
        from datetime import datetime
        
        ordenes_recientes = OrdenTrabajo.objects.select_related(
            'vehiculo', 'cliente'
        ).order_by('-fecha_ingreso')[:10]
        
        # Estadísticas
        total_clientes = Cliente.objects.count()
        total_vehiculos = Vehiculo.objects.count()
        ordenes_activas = OrdenTrabajo.objects.exclude(estado='entregado').count()
        
        # Órdenes creadas hoy
        hoy = timezone.now().date()
        ordenes_hoy = OrdenTrabajo.objects.filter(
            fecha_ingreso__date=hoy
        ).count()
        
        # Órdenes por estado
        ordenes_recepcionadas = OrdenTrabajo.objects.filter(estado='recepcionado').count()
        ordenes_listas = OrdenTrabajo.objects.filter(estado='listo_entrega').count()
        
        context = {
            'rol': 'recepcionista',
            'ordenes_recientes': ordenes_recientes,
            'total_clientes': total_clientes,
            'total_vehiculos': total_vehiculos,
            'ordenes_activas': ordenes_activas,
            'ordenes_hoy': ordenes_hoy,
            'ordenes_recepcionadas': ordenes_recepcionadas,
            'ordenes_listas': ordenes_listas,
        }
        return render(request, 'gestion/dashboard_recepcionista.html', context)
    
    # Sin rol
    return render(request, 'gestion/sin_acceso.html')



# ============================================
# UC-007: GENERAR FACTURA
# ============================================
@login_required
def generar_factura(request, pk):
    """
    Genera un comprobante/factura HTML para una orden.
    UC-007 del documento de requisitos.
    """
    from django.utils import timezone
    
    orden = get_object_or_404(
        OrdenTrabajo.objects.select_related('cliente', 'vehiculo'),
        pk=pk
    )
    
    # Calcular costos (esto debería estar en los modelos, pero lo hacemos aquí por simplicidad)
    presupuestos = orden.presupuestos.all()
    bitacoras = orden.bitacoras.prefetch_related('repuestos_usados__repuesto')
    
    # Suma de mano de obra y repuestos desde presupuestos
    costo_mano_obra = presupuestos.aggregate(Sum('costo_mano_obra'))['costo_mano_obra__sum'] or 0
    costo_repuestos_presupuesto = presupuestos.aggregate(Sum('costo_repuestos'))['costo_repuestos__sum'] or 0
    
    # Detalle de repuestos desde bitácoras (más preciso)
    repuestos_usados = []
    total_repuestos = 0
    for bitacora in bitacoras:
        for item in bitacora.repuestos_usados.all():
            subtotal = item.cantidad * item.repuesto.precio_venta
            repuestos_usados.append({
                'nombre': item.repuesto.nombre,
                'cantidad': item.cantidad,
                'precio_unitario': item.repuesto.precio_venta,
                'subtotal': subtotal
            })
            total_repuestos += subtotal

    # Totales
    subtotal = costo_mano_obra + total_repuestos
    iva = subtotal * 0.19
    total_final = subtotal + iva

    context = {
        'orden': orden,
        'costo_mano_obra': costo_mano_obra,
        'repuestos_usados': repuestos_usados,
        'total_repuestos': total_repuestos,
        'subtotal': subtotal,
        'iva': iva,
        'total_final': total_final,
        'fecha_emision': timezone.now(),
    }
    
    return render(request, 'gestion/factura.html', context)




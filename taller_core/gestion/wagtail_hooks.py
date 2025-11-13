# taller_core/gestion/wagtail_hooks.py

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail import hooks
from wagtail.admin.ui.components import Component

from .models import (
    Cliente, Vehiculo, Mecanico, ZonaTrabajo, 
    OrdenTrabajo, Repuesto, Bitacora, Alerta, Presupuesto
)
from .models import PerfilUsuario

# ============================================
# SNIPPETS VIEWSETS - Gestión de Modelos
# ============================================

class ClienteSnippetViewSet(SnippetViewSet):
    model = Cliente
    menu_label = "Clientes"
    menu_icon = "user"
    menu_order = 300
    list_display = ("nombre", "apellido", "telefono", "email", "fecha_registro")
    search_fields = ("nombre", "apellido", "email", "telefono")
    list_filter = ("fecha_registro",)


class VehiculoSnippetViewSet(SnippetViewSet):
    model = Vehiculo
    menu_label = "Vehículos"
    menu_icon = "cogs"
    menu_order = 310
    list_display = ("patente", "marca", "modelo", "año", "cliente")
    search_fields = ("patente", "marca", "modelo", "cliente__nombre", "cliente__apellido")
    list_filter = ("marca", "año")


class MecanicoSnippetViewSet(SnippetViewSet):
    model = Mecanico
    menu_label = "Mecánicos"
    menu_icon = "user-shield"
    menu_order = 200
    list_display = ("nombre", "especialidad", "disponible", "telefono")
    search_fields = ("nombre", "especialidad", "email")
    list_filter = ("disponible", "especialidad")


class ZonaTrabajoSnippetViewSet(SnippetViewSet):
    model = ZonaTrabajo
    menu_label = "Zonas de Trabajo"
    menu_icon = "map-marker"
    menu_order = 210
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


class OrdenTrabajoSnippetViewSet(SnippetViewSet):
    model = OrdenTrabajo
    menu_label = "Órdenes de Trabajo"
    menu_icon = "clipboard-list"
    menu_order = 100  # Principal - va arriba
    list_display = ("id", "vehiculo", "cliente", "estado", "mecanico_asignado", "prioridad", "fecha_ingreso")
    search_fields = ("id", "vehiculo__patente", "cliente__nombre", "cliente__apellido", "descripcion_problema")
    list_filter = ("estado", "prioridad", "mecanico_asignado", "zona_trabajo", "fecha_ingreso")
    
    def get_queryset(self, request):
        """Filtra las órdenes según el rol del usuario"""
        qs = super().get_queryset(request)
        
        # Superusuarios ven todo
        if request.user.is_superuser:
            return qs
        
        # Mecánicos solo ven sus órdenes
        if request.user.groups.filter(name="Mecánico").exists():
            try:
                mecanico = request.user.perfil_mecanico
                return qs.filter(mecanico_asignado=mecanico)
            except AttributeError:
                return qs.none()
        
        # Encargados y Recepcionistas ven todo
        return qs


class RepuestoSnippetViewSet(SnippetViewSet):
    model = Repuesto
    menu_label = "Repuestos (Inventario)"
    menu_icon = "archive"
    menu_order = 400
    list_display = ("nombre", "codigo", "marca", "stock_actual", "stock_minimo", "precio_venta")
    search_fields = ("nombre", "codigo", "marca", "descripcion")
    list_filter = ("marca",)
    
    # Resaltar repuestos con stock bajo
    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return list_display + ("estado_stock",)
    
    def estado_stock(self, obj):
        if obj.stock_actual <= obj.stock_minimo:
            return f"⚠️ STOCK BAJO ({obj.stock_actual})"
        return f"✓ OK ({obj.stock_actual})"
    estado_stock.short_description = "Estado Stock"


class BitacoraSnippetViewSet(SnippetViewSet):
    model = Bitacora
    menu_label = "Bitácoras"
    menu_icon = "doc-full"
    menu_order = 110
    list_display = ("id", "orden", "mecanico", "fecha", "procedimientos_cortos")
    search_fields = ("orden__id", "mecanico__nombre", "procedimientos", "observaciones")
    list_filter = ("mecanico", "fecha")
    
    # La lógica ahora está en el modelo como una propiedad.


class PresupuestoSnippetViewSet(SnippetViewSet):
    model = Presupuesto
    menu_label = "Presupuestos"
    menu_icon = "doc-full-inverse"
    menu_order = 120
    list_display = ("id", "orden", "estado", "total_calculado", "fecha_creacion")
    search_fields = ("orden__id", "descripcion")
    list_filter = ("estado", "fecha_creacion")
    
    def total_calculado(self, obj):
        return f"${obj.total:,.0f}"
    total_calculado.short_description = "Total"


class AlertaSnippetViewSet(SnippetViewSet):
    model = Alerta
    menu_label = "Alertas"
    menu_icon = "warning"
    menu_order = 50  # Arriba de todo
    list_display = ("tipo", "mensaje", "orden", "fecha_creacion", "resuelta")
    search_fields = ("mensaje", "orden__id")
    list_filter = ("tipo", "resuelta", "fecha_creacion")
    
    def get_queryset(self, request):
        """Mostrar solo alertas no resueltas por defecto"""
        qs = super().get_queryset(request)
        # Si no hay filtro aplicado, mostrar solo no resueltas
        if not request.GET.get('resuelta'):
            return qs.filter(resuelta=False)
        return qs


class PerfilUsuarioSnippetViewSet(SnippetViewSet):
    model = PerfilUsuario
    menu_label = "Perfiles de Usuario"
    menu_icon = "user"
    menu_order = 500  # Al final del menú
    list_display = ("usuario", "rol", "activo", "fecha_creacion")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name")
    list_filter = ("rol", "activo")
# ============================================
# REGISTRO DE SNIPPETS
# ============================================

register_snippet(AlertaSnippetViewSet)           # Orden 50
register_snippet(OrdenTrabajoSnippetViewSet)     # Orden 100
register_snippet(BitacoraSnippetViewSet)         # Orden 110
register_snippet(PresupuestoSnippetViewSet)      # Orden 120
register_snippet(MecanicoSnippetViewSet)         # Orden 200
register_snippet(ZonaTrabajoSnippetViewSet)      # Orden 210
register_snippet(ClienteSnippetViewSet)          # Orden 300
register_snippet(VehiculoSnippetViewSet)         # Orden 310
register_snippet(RepuestoSnippetViewSet)         # Orden 400
register_snippet(PerfilUsuarioSnippetViewSet)

# ============================================
# DASHBOARD PERSONALIZADO
# ============================================

class DashboardPanel(Component):
    """Panel personalizado en el dashboard de Wagtail"""
    order = 50
    template_name = "admin/dashboard_panel.html"

    def get_context_data(self, parent_context):
        request = parent_context["request"]
        context = super().get_context_data(parent_context)

        # Inicializar variables
        context['ordenes_asignadas'] = None
        context['ordenes_activas'] = None
        context['alertas_activas'] = None
        context['is_recepcionista'] = False
        context['user_role'] = None

        if not request.user.is_authenticated:
            return context

        # Alertas activas (para todos)
        context['alertas_activas'] = Alerta.objects.filter(resuelta=False).order_by('-fecha_creacion')[:5]

        # Superusuario o Encargado - ven todas las órdenes activas
        if request.user.is_superuser or request.user.groups.filter(name="Encargado").exists():
            context['user_role'] = 'Encargado'
            context['ordenes_activas'] = OrdenTrabajo.objects.exclude(
                estado='entregado'
            ).select_related('vehiculo', 'cliente', 'mecanico_asignado').order_by('-fecha_ingreso')[:10]
            
            # Estadísticas adicionales
            context['stats'] = {
                'total_activas': OrdenTrabajo.objects.exclude(estado='entregado').count(),
                'en_reparacion': OrdenTrabajo.objects.filter(estado='en_reparacion').count(),
                'listas': OrdenTrabajo.objects.filter(estado='listo_entrega').count(),
            }

        # Mecánico - solo sus órdenes
        elif request.user.groups.filter(name="Mecánico").exists():
            try:
                mecanico = request.user.perfil_mecanico
                context['user_role'] = f'Mecánico - {mecanico.nombre}'
                context['ordenes_asignadas'] = OrdenTrabajo.objects.filter(
                    mecanico_asignado=mecanico,
                ).exclude(estado='entregado').select_related('vehiculo', 'cliente').order_by('-fecha_ingreso')
                
                context['stats'] = {
                    'asignadas': context['ordenes_asignadas'].count(),
                    'en_curso': context['ordenes_asignadas'].filter(estado='en_reparacion').count(),
                }
            except AttributeError:
                context['user_role'] = 'Mecánico (sin perfil)'

        # Recepcionista
        elif request.user.groups.filter(name="Recepcionista").exists():
            context['user_role'] = 'Recepcionista'
            context['is_recepcionista'] = True
            context['ordenes_recientes'] = OrdenTrabajo.objects.select_related(
                'vehiculo', 'cliente'
            ).order_by('-fecha_ingreso')[:10]

        return context
    



@hooks.register('construct_homepage_panels')
def add_dashboard_panel(request, panels):
    """Agrega el panel personalizado al dashboard"""
    panels.append(DashboardPanel())


# ============================================
# HOOKS ADICIONALES
# ============================================

@hooks.register('construct_main_menu')
def hide_default_items(request, menu_items):
    """Personalizar el menú principal"""
    # Puedes ocultar items que no necesites
    # menu_items[:] = [item for item in menu_items if item.name not in ['documents', 'images']]
    pass


@hooks.register('after_edit_snippet')
def log_snippet_edit(request, instance):
    """Log cuando se edita un snippet importante"""
    if isinstance(instance, OrdenTrabajo):
        print(f"✏️ Orden #{instance.id} editada por {request.user.username}")
    elif isinstance(instance, Alerta) and instance.resuelta:
        print(f"✓ Alerta #{instance.id} marcada como resuelta")


# ============================================
# MENSAJE DE CARGA
# ============================================

print("=" * 50)
print("✓ WAGTAIL HOOKS CARGADOS CORRECTAMENTE")
print(f"  - {len([ClienteSnippetViewSet, VehiculoSnippetViewSet, MecanicoSnippetViewSet, ZonaTrabajoSnippetViewSet, OrdenTrabajoSnippetViewSet, RepuestoSnippetViewSet, BitacoraSnippetViewSet, AlertaSnippetViewSet, PresupuestoSnippetViewSet])} Snippets registrados")
print(f"  - Dashboard personalizado activado")
print("=" * 50)


# 2. Registramos el panel en el dashboard
@hooks.register('construct_homepage_panels')
def add_my_dashboard_panel(request, panels):
    panels.append(DashboardPanel())
print("==========================================")
print("!!! ARCHIVO wagtail_hooks.py CARGADO !!!")
print("==========================================")
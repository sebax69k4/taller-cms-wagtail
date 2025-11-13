from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
# --- Importa los nuevos modelos ---
from .models import Cliente, Vehiculo, Mecanico, ZonaTrabajo, OrdenTrabajo, Repuesto, Bitacora, Alerta


class ClienteSnippetViewSet(SnippetViewSet):
    model = Cliente
    menu_label = "Clientes"
    menu_icon = "user"
    list_display = ("nombre", "apellido", "telefono", "email")
    search_fields = ("nombre", "apellido", "email", "telefono")


class VehiculoSnippetViewSet(SnippetViewSet):
    model = Vehiculo
    menu_label = "Vehículos"
    menu_icon = "cogs"
    list_display = ("patente", "marca", "modelo", "año", "cliente")
    search_fields = ("patente", "marca", "modelo", "cliente__nombre", "cliente__apellido")

# --- PEGA ESTAS NUEVAS CLASES ---

class MecanicoSnippetViewSet(SnippetViewSet):
    model = Mecanico
    menu_label = "Mecánicos"
    menu_icon = "user-shield" # Un ícono diferente
    list_display = ("nombre", "especialidad", "disponible")
    search_fields = ("nombre", "especialidad")

class ZonaTrabajoSnippetViewSet(SnippetViewSet):
    model = ZonaTrabajo
    menu_label = "Zonas de Trabajo"
    menu_icon = "map-marker"
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)

class OrdenTrabajoSnippetViewSet(SnippetViewSet):
    model = OrdenTrabajo
    # Este es el modelo principal, lo ponemos arriba del todo
    menu_order = 100 # (Números bajos van más arriba)
    menu_label = "Órdenes de Trabajo"
    menu_icon = "clipboard-list"
    list_display = ("id", "vehiculo", "cliente", "estado", "mecanico_asignado", "fecha_ingreso")
    search_fields = ("id", "vehiculo__patente", "cliente__nombre", "cliente__apellido")
    list_filter = ("estado", "mecanico_asignado", "prioridad") # ¡Para filtrar!
    def get_queryset(self, request):
        """Filtra la lista de órdenes según el rol del usuario."""

        # 1. Obtiene la lista completa de órdenes
        qs = super().get_queryset(request)

        # 2. Si el usuario es SuperAdmin, que vea todo
        if request.user.is_superuser:
            return qs

        # 3. Si el usuario está en el grupo "Mecánico"
        if request.user.groups.filter(name="Mecánico").exists():
            try:
                # Buscamos su "perfil_mecanico" (que creamos en el Paso 1)
                mecanico = request.user.perfil_mecanico
                # Filtramos la lista para mostrar SOLO las órdenes
                # donde "mecanico_asignado" sea él mismo.
                return qs.filter(mecanico_asignado=mecanico)
            except AttributeError:
                # Si el usuario no tiene un perfil de mecánico, no le mostramos nada.
                return qs.none()

        # 4. Si es otro rol (Recepcionista, Encargado), que vea todo
        # (Podemos refinar esto después)
        return qs


class RepuestoSnippetViewSet(SnippetViewSet):
    model = Repuesto
    menu_label = "Repuestos (Inventario)"
    menu_icon = "archive"
    menu_order = 200 # Para agruparlo con los de gestión
    list_display = ("nombre", "codigo", "stock_actual", "stock_minimo", "precio_venta")
    search_fields = ("nombre", "codigo", "marca")
    list_filter = ("marca",)

class BitacoraSnippetViewSet(SnippetViewSet):
    model = Bitacora
    menu_label = "Bitácoras"
    menu_icon = "tools"
    menu_order = 101 # Debajo de Órdenes de Trabajo
    list_display = ("id", "orden", "mecanico", "fecha")
    search_fields = ("orden__id", "mecanico__nombre")
    list_filter = ("mecanico", "fecha")

class AlertaSnippetViewSet(SnippetViewSet):
    model = Alerta
    menu_label = "Alertas"
    menu_icon = "warning"
    menu_order = 50 # Ponerlo arriba, es importante
    list_display = ("fecha_creacion", "tipo", "mensaje", "orden", "resuelta")
    search_fields = ("mensaje", "orden__id")
    list_filter = ("tipo", "resuelta")    

# --- Registra todo ---
register_snippet(ClienteSnippetViewSet)
register_snippet(VehiculoSnippetViewSet)
register_snippet(MecanicoSnippetViewSet)       
register_snippet(ZonaTrabajoSnippetViewSet)
register_snippet(OrdenTrabajoSnippetViewSet) 
register_snippet(RepuestoSnippetViewSet)  
register_snippet(BitacoraSnippetViewSet)
register_snippet(AlertaSnippetViewSet)

from wagtail import hooks
from wagtail.admin.ui.components import Component
# Importamos las órdenes para la lógica
from .models import OrdenTrabajo

# 1. Definimos una clase para nuestro panel HTML
class DashboardPanel(Component):
    order = 50 # Posición en el dashboard
    template_name = "admin/dashboard_panel.html" # Un nuevo template que crearemos

    # Pasamos datos al template
    def get_context_data(self, parent_context):
        request = parent_context["request"]
        context = super().get_context_data(parent_context)

        # -- Esta es la misma lógica de 'get_context' de antes --
        context['ordenes_asignadas'] = None
        context['ordenes_activas'] = None
        context['is_recepcionista'] = False

        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.groups.filter(name="Encargado").exists():
                context['ordenes_activas'] = OrdenTrabajo.objects.exclude(
                    estado='entregado'
                ).order_by('fecha_ingreso')[:10]

            elif request.user.groups.filter(name="Mecánico").exists():
                try:
                    mecanico = request.user.perfil_mecanico
                    context['ordenes_asignadas'] = OrdenTrabajo.objects.filter(
                        mecanico_asignado=mecanico,
                    ).exclude(estado='entregado').order_by('fecha_ingreso')
                except AttributeError:
                    pass

            elif request.user.groups.filter(name="Recepcionista").exists():
                context['is_recepcionista'] = True
        # ----------------------------------------------------

        return context

# 2. Registramos el panel en el dashboard
@hooks.register('construct_homepage_panels')
def add_my_dashboard_panel(request, panels):
    panels.append(DashboardPanel())
print("==========================================")
print("!!! ARCHIVO wagtail_hooks.py CARGADO !!!")
print("==========================================")
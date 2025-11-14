# DOCUMENTACIÓN TÉCNICA - SISTEMA DE GESTIÓN DE TALLER

## 🏗️ ARQUITECTURA DEL SISTEMA

### Stack Tecnológico
- **Backend:** Django 5.2.7
- **CMS:** Wagtail >= 6.0
- **Database:** SQLite3
- **Frontend:** Bootstrap 5.3.0
- **Icons:** Font Awesome 6.4.0
- **Python:** 3.x

### Estructura del Proyecto
```
taller_core/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── gestion/                    # App principal
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Lógica de vistas
│   ├── forms.py               # Django ModelForms
│   ├── urls.py                # Rutas de la app
│   ├── wagtail_hooks.py       # Configuración de Wagtail Snippets
│   ├── admin.py               # (Deshabilitado, se usa Wagtail)
│   ├── signals.py             # Signals para lógica de negocio
│   ├── templatetags/
│   │   └── auth_extras.py     # Custom template tag: has_group
│   ├── management/commands/
│   │   ├── setup_initial_data.py      # Crear usuarios de prueba
│   │   └── fix_user_permissions.py    # Corregir permisos
│   ├── templates/gestion/
│   │   ├── base.html          # Template base con navbar
│   │   ├── dashboard.html     # Dashboard del encargado
│   │   ├── lista_clientes.html
│   │   ├── registrar_cliente.html
│   │   ├── editar_cliente.html
│   │   ├── lista_vehiculos.html
│   │   ├── registrar_vehiculo.html
│   │   ├── editar_vehiculo.html
│   │   ├── orden_list.html
│   │   ├── orden_detail.html
│   │   ├── crear_orden.html
│   │   ├── agregar_bitacora.html
│   │   └── agregar_presupuesto.html
│   └── static/gestion/
│       ├── css/
│       └── js/
├── home/                      # App para página de bienvenida
│   ├── views.py
│   └── templates/home/
│       └── welcome_page.html  # Página de inicio
└── taller_core/               # Configuración del proyecto
    ├── settings/
    │   └── base.py            # Settings principales
    ├── urls.py                # URLs raíz
    └── wsgi.py
```

---

## 📊 MODELOS DE DATOS

### Cliente
```python
class Cliente(models.Model):
    rut = CharField(max_length=12, unique=True)
    nombre = CharField(max_length=100)
    telefono = CharField(max_length=15, blank=True)
    email = EmailField(blank=True)
    direccion = TextField(blank=True)
```

### Vehiculo
```python
class Vehiculo(models.Model):
    patente = CharField(max_length=10, unique=True)
    cliente = ForeignKey(Cliente)
    marca = CharField(max_length=50)
    modelo = CharField(max_length=50)
    anio = IntegerField(null=True, blank=True)
    color = CharField(max_length=30, blank=True)
    kilometraje_actual = DecimalField(max_digits=10, decimal_places=2)
    observaciones = TextField(blank=True)
```

### OrdenTrabajo
```python
class OrdenTrabajo(ClusterableModel):
    cliente = ForeignKey(Cliente)
    vehiculo = ForeignKey(Vehiculo)
    mecanico_asignado = ForeignKey(Mecanico, null=True, blank=True)
    zona_trabajo = ForeignKey(ZonaTrabajo, null=True, blank=True)
    
    fecha_ingreso = DateTimeField(auto_now_add=True)
    fecha_estimada = DateTimeField(null=True, blank=True)
    fecha_finalizacion = DateTimeField(null=True, blank=True)
    
    descripcion_problema = TextField()
    estado = CharField(max_length=20, choices=ESTADO_CHOICES, default='recepcionado')
    prioridad = CharField(max_length=10, choices=[...], default='media')
    
    # Relaciones inversas:
    # - bitacoras (InlinePanel)
    # - presupuestos (InlinePanel)
```

**Estados disponibles:**
- `recepcionado`: Vehículo ingresado, sin asignación
- `diagnostico`: En proceso de diagnóstico
- `en_reparacion`: Trabajo en curso
- `espera_repuesto`: Bloqueado por falta de repuestos
- `listo_entrega`: Terminado, listo para cliente
- `entregado`: Completado

### Bitacora
```python
class Bitacora(ClusterableModel):
    orden = ParentalKey(OrdenTrabajo, related_name='bitacoras')
    fecha = DateField()
    descripcion = TextField()
    horas_trabajadas = DecimalField(max_digits=5, decimal_places=2, null=True)
    procedimientos = ParentalManyToManyField(Procedimiento)
    
    @property
    def procedimientos_cortos(self):
        """Retorna lista de procedimientos en formato corto"""
        return ", ".join([p.nombre for p in self.procedimientos.all()[:3]])
```

### Presupuesto
```python
class Presupuesto(ClusterableModel):
    orden = ParentalKey(OrdenTrabajo, related_name='presupuestos')
    fecha = DateField()
    descripcion = TextField()
    total_mano_obra = DecimalField(max_digits=10, decimal_places=2)
    total_repuestos = DecimalField(max_digits=10, decimal_places=2)
    validez_dias = IntegerField(default=30)
    estado_aprobacion = CharField(
        max_length=20, 
        choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )
    items = ParentalManyToManyField(ItemPresupuesto)
```

### Mecanico
```python
class Mecanico(models.Model):
    usuario = OneToOneField(User, related_name='mecanico')
    nombre = CharField(max_length=100)
    especialidad = CharField(max_length=100, blank=True)
    disponible = BooleanField(default=True)
```

---

## 🔐 SISTEMA DE AUTENTICACIÓN Y PERMISOS

### Grupos de Usuarios
El sistema utiliza grupos de Django para control de acceso:
- **Encargado**: Acceso completo
- **Mecánico**: Solo órdenes asignadas y bitácoras
- **Recepcionista**: Gestión de clientes, vehículos y creación de órdenes

### Custom Template Tag: `has_group`
**Archivo:** `gestion/templatetags/auth_extras.py`

```python
@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Verifica si el usuario pertenece a un grupo.
    Normaliza nombres de grupos para ignorar acentos y mayúsculas.
    """
    from unicodedata import normalize
    
    def normalizar(texto):
        nfkd = normalize('NFKD', texto)
        return ''.join([c for c in nfkd if not combining(c)]).lower()
    
    group_normalizado = normalizar(group_name)
    return user.groups.filter(
        name__iregex=r'^' + group_name.replace('á', '[aá]').replace('é', '[eé]') + r'$'
    ).exists()
```

**Uso en templates:**
```django
{% if user|has_group:"Encargado" %}
    <!-- Contenido solo para encargados -->
{% endif %}
```

### Decoradores de Permisos
**Archivo:** `gestion/views.py`

```python
def es_recepcionista_o_encargado(user):
    """Permite acceso a recepcionistas y encargados"""
    from unicodedata import normalize
    
    def normalizar(texto):
        nfkd = normalize('NFKD', texto)
        return ''.join([c for c in nfkd if not combining(c)]).lower()
    
    grupos_usuario = [normalizar(g.name) for g in user.groups.all()]
    return 'recepcionista' in grupos_usuario or 'encargado' in grupos_usuario

def es_encargado(user):
    """Permite acceso solo a encargados"""
    grupos_usuario = [normalizar(g.name) for g in user.groups.all()]
    return 'encargado' in grupos_usuario

def es_mecanico(user):
    """Permite acceso solo a mecánicos"""
    grupos_usuario = [normalizar(g.name) for g in user.groups.all()]
    return 'mecanico' in grupos_usuario
```

**Uso en vistas:**
```python
@login_required
@user_passes_test(es_recepcionista_o_encargado, login_url='/gestion/login/')
def lista_clientes(request):
    # Solo recepcionistas y encargados pueden acceder
    ...
```

---

## 📝 FORMS (CRUD)

### ClienteForm
```python
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'nombre', 'telefono', 'email', 'direccion']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
```

### VehiculoForm
```python
class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['patente', 'cliente', 'marca', 'modelo', 'anio', 'color', 
                  'kilometraje_actual', 'observaciones']
        widgets = {
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AB1234'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2030}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometraje_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
```

### OrdenTrabajoForm
```python
class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['vehiculo', 'cliente', 'prioridad', 'fecha_ingreso', 
                  'kilometraje_ingreso', 'descripcion_problema', 'observaciones_ingreso']
        widgets = {
            'vehiculo': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'fecha_ingreso': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'kilometraje_ingreso': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion_problema': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'observaciones_ingreso': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
```

---

## 🔄 VISTAS PRINCIPALES

### Vista de Lista (Ejemplo: lista_clientes)
```python
@login_required
@user_passes_test(es_recepcionista_o_encargado, login_url='/gestion/login/')
def lista_clientes(request):
    """Vista para listar clientes con búsqueda"""
    clientes = Cliente.objects.all().order_by('nombre')
    
    # Búsqueda
    buscar = request.GET.get('buscar', '').strip()
    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar) |
            Q(rut__icontains=buscar) |
            Q(telefono__icontains=buscar)
        )
    
    context = {'clientes': clientes}
    return render(request, 'gestion/lista_clientes.html', context)
```

### Vista de Creación (Ejemplo: registrar_cliente)
```python
@login_required
@user_passes_test(es_recepcionista_o_encargado, login_url='/gestion/login/')
def registrar_cliente(request):
    """Vista para registrar un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.nombre} registrado exitosamente')
            return redirect('gestion:lista_clientes')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = ClienteForm()
    
    context = {'form': form}
    return render(request, 'gestion/registrar_cliente.html', context)
```

### Vista de Edición (Ejemplo: editar_cliente)
```python
@login_required
@user_passes_test(es_recepcionista_o_encargado, login_url='/gestion/login/')
def editar_cliente(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente {cliente.nombre} actualizado exitosamente')
            return redirect('gestion:lista_clientes')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {'form': form, 'cliente': cliente}
    return render(request, 'gestion/editar_cliente.html', context)
```

### Vista con Validación de Mecánico (agregar_bitacora)
```python
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
            form.save_m2m()  # Guardar relaciones many-to-many
            messages.success(request, 'Bitácora agregada exitosamente')
            return redirect('gestion:orden_detail', pk=pk)
    else:
        form = BitacoraForm()
    
    context = {'form': form, 'orden': orden}
    return render(request, 'gestion/agregar_bitacora.html', context)
```

---

## 🗺️ RUTAS (URLs)

### Configuración Principal (`taller_core/urls.py`)
```python
from django.urls import path, include
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from home import views as home_views

urlpatterns = [
    path("", home_views.welcome_page, name='welcome'),  # Página de inicio
    path("admin/", include(wagtailadmin_urls)),          # Panel Wagtail
    path("gestion/", include("gestion.urls")),           # App principal
    path("pages/", include(wagtail_urls)),               # Páginas Wagtail
]
```

### URLs de Gestion (`gestion/urls.py`)
```python
from django.urls import path
from . import views

app_name = 'gestion'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.mi_dashboard, name='dashboard'),
    
    # Clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # Vehículos
    path('vehiculos/', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/registrar/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('vehiculos/<int:pk>/editar/', views.editar_vehiculo, name='editar_vehiculo'),
    
    # Órdenes de Trabajo
    path('ordenes/', views.orden_list, name='orden_list'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    path('ordenes/crear/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:pk>/agregar-bitacora/', views.agregar_bitacora, name='agregar_bitacora'),
    path('ordenes/<int:pk>/agregar-presupuesto/', views.agregar_presupuesto, name='agregar_presupuesto'),
    
    # Gestión (solo encargado)
    path('asignar/', views.asignar_trabajo, name='asignar_trabajo'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    path('factura/<int:pk>/', views.generar_factura, name='generar_factura'),
]
```

---

## 🎨 TEMPLATES

### Template Base (`base.html`)
Características principales:
- Bootstrap 5.3.0 CDN
- Font Awesome 6.4.0 CDN
- Navbar responsivo con dropdown
- Menú adaptativo según rol del usuario
- Badges de rol en el dropdown del usuario
- Footer sticky

**Bloques disponibles:**
```django
{% block title %}{% endblock %}
{% block extra_css %}{% endblock %}
{% block breadcrumb %}{% endblock %}
{% block content %}{% endblock %}
{% block extra_js %}{% endblock %}
```

### Ejemplo de Template de Lista
```django
{% extends "gestion/base.html" %}

{% block title %}Lista de Clientes{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Header con botón de acción -->
    <div class="row mb-4">
        <div class="col">
            <h2><i class="fas fa-users me-2"></i>Lista de Clientes</h2>
        </div>
        <div class="col-auto">
            <a href="{% url 'gestion:registrar_cliente' %}" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Nuevo Cliente
            </a>
        </div>
    </div>

    <!-- Barra de búsqueda -->
    <div class="row mb-3">
        <div class="col-md-6">
            <form method="get" class="input-group">
                <input type="text" name="buscar" class="form-control" 
                       placeholder="Buscar..." value="{{ request.GET.buscar }}">
                <button class="btn btn-outline-primary" type="submit">
                    <i class="fas fa-search"></i> Buscar
                </button>
            </form>
        </div>
    </div>

    <!-- Tabla -->
    <div class="card">
        <div class="card-body">
            {% if clientes %}
            <table class="table table-hover">
                <!-- ... -->
            </table>
            {% else %}
            <div class="alert alert-info">No hay clientes registrados.</div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

---

## ⚙️ COMANDOS DE GESTIÓN

### setup_initial_data.py
**Ubicación:** `gestion/management/commands/setup_initial_data.py`

**Función:** Crea o actualiza usuarios de prueba con credenciales conocidas

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Crea usuarios de prueba con grupos correctos'
    
    def handle(self, *args, **options):
        # Crear grupos si no existen
        encargado_group, _ = Group.objects.get_or_create(name='Encargado')
        mecanico_group, _ = Group.objects.get_or_create(name='Mecánico')
        recepcionista_group, _ = Group.objects.get_or_create(name='Recepcionista')
        
        # Usuario: Encargado
        encargado, created = User.objects.get_or_create(username='encargado')
        encargado.set_password('enc123')
        encargado.is_staff = True  # Puede acceder al admin de Wagtail
        encargado.save()
        encargado.groups.add(encargado_group)
        
        # Usuario: Mecánico
        mecanico, created = User.objects.get_or_create(username='mecanico')
        mecanico.set_password('mec123')
        mecanico.is_staff = False  # NO accede al admin
        mecanico.save()
        mecanico.groups.add(mecanico_group)
        
        # Usuario: Recepcionista
        recepcionista, created = User.objects.get_or_create(username='recepcionista')
        recepcionista.set_password('recep123')
        recepcionista.is_staff = False  # NO accede al admin
        recepcionista.save()
        recepcionista.groups.add(recepcionista_group)
        
        self.stdout.write(self.style.SUCCESS('✓ Usuarios creados/actualizados'))
```

**Uso:**
```bash
python manage.py setup_initial_data
```

### fix_user_permissions.py
**Ubicación:** `gestion/management/commands/fix_user_permissions.py`

**Función:** Corrige flags `is_staff` para usuarios no administrativos

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Corrige permisos is_staff para usuarios no administrativos'
    
    def handle(self, *args, **options):
        # Usuarios que NO deben tener is_staff=True
        usuarios_no_staff = ['mecanico', 'recepcionista']
        
        for username in usuarios_no_staff:
            try:
                user = User.objects.get(username=username)
                if user.is_staff:
                    user.is_staff = False
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ {username}: is_staff=False'))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Usuario {username} no existe'))
```

**Uso:**
```bash
python manage.py fix_user_permissions
```

---

## 🔧 CONFIGURACIÓN

### Settings Importantes (`taller_core/settings/base.py`)

```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Wagtail
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    'modelcluster',
    'taggit',
    
    # Third party
    'rest_framework',
    'django_filters',
    
    # Local apps
    'gestion.apps.GestionConfig',  # Importante: usar GestionConfig para template tags
    'home',
    'search',
]

# Redireccionamiento después de login/logout
LOGIN_URL = '/gestion/login/'
LOGIN_REDIRECT_URL = '/gestion/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Wagtail
WAGTAIL_SITE_NAME = 'Taller Mecánico'
```

---

## 🐛 DEBUGGING Y TESTING

### Comandos Útiles

**Verificar configuración:**
```bash
python manage.py check
```

**Crear migraciones:**
```bash
python manage.py makemigrations
```

**Aplicar migraciones:**
```bash
python manage.py migrate
```

**Crear superusuario:**
```bash
python manage.py createsuperuser
```

**Shell de Django:**
```bash
python manage.py shell
```

**Ejecutar servidor de desarrollo:**
```bash
python manage.py runserver
```

### Verificación de Permisos en Shell
```python
from django.contrib.auth.models import User

# Ver grupos de un usuario
user = User.objects.get(username='recepcionista')
print(user.groups.all())

# Verificar flag is_staff
print(f"is_staff: {user.is_staff}")

# Verificar pertenencia a grupo
print(user.groups.filter(name='Recepcionista').exists())
```

---

## 📦 DEPENDENCIAS PRINCIPALES

**Del archivo `requirements.txt`:**
```
Django>=5.2.7
wagtail>=6.0
djangorestframework>=3.16.1
django-filter>=25.2
pillow>=11.3.0
django-taggit>=6.1.0
django-modelcluster>=6.4
```

---

## 🚀 DEPLOYMENT

### Checklist Pre-Producción
- [ ] Cambiar `DEBUG = False` en settings
- [ ] Configurar `ALLOWED_HOSTS`
- [ ] Configurar base de datos de producción (PostgreSQL)
- [ ] Configurar `STATIC_ROOT` y ejecutar `collectstatic`
- [ ] Configurar `MEDIA_ROOT` para archivos subidos
- [ ] Configurar variables de entorno para secrets
- [ ] Habilitar HTTPS
- [ ] Configurar backup de base de datos
- [ ] Configurar logging adecuado

### Variables de Entorno Recomendadas
```bash
DJANGO_SECRET_KEY=<secret_key_here>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_URL=postgres://user:pass@host:port/dbname
```

---

## 📝 NOTAS TÉCNICAS

### ¿Por qué ClusterableModel y ParentalKey?
- **ClusterableModel:** Permite edición inline de modelos relacionados en Wagtail admin
- **ParentalKey:** Relación especial que mantiene los objetos relacionados en memoria para edición atómica

### Normalización Unicode en Grupos
Se implementó normalización de nombres de grupos para evitar problemas con:
- Acentos (Mecánico vs Mecanico)
- Mayúsculas (MECANICO vs mecanico)
- Variaciones regionales

### Uso de Messages Framework
Todas las vistas de creación/edición usan `django.contrib.messages` para feedback al usuario:
```python
from django.contrib import messages

messages.success(request, 'Operación exitosa')
messages.error(request, 'Error en la operación')
messages.warning(request, 'Advertencia')
messages.info(request, 'Información')
```

Los mensajes se renderizan automáticamente en `base.html` (si está implementado).

---

## 🔍 MEJORAS FUTURAS SUGERIDAS

### Funcionalidades
- [ ] Paginación en listas (Django Paginator)
- [ ] Exportación a PDF de facturas
- [ ] Envío de email con presupuestos
- [ ] Notificaciones push cuando orden está lista
- [ ] Historial de cambios de estado
- [ ] Gráficos y reportes con Chart.js
- [ ] API REST completa (ya está Django REST Framework)

### Técnicas
- [ ] Tests unitarios (Django TestCase)
- [ ] Tests de integración
- [ ] Caché con Redis
- [ ] Tareas asíncronas con Celery
- [ ] Búsqueda full-text con Elasticsearch
- [ ] Docker/Docker Compose para deployment
- [ ] CI/CD con GitHub Actions

### UX/UI
- [ ] Drag-and-drop para asignar órdenes
- [ ] AJAX para actualización sin recargar página
- [ ] Confirmación de eliminación con modal
- [ ] Autocompletado en búsquedas
- [ ] Tema oscuro/claro

---

**Última actualización:** 2025
**Autor:** Desarrollo Interno
**Licencia:** Uso Interno

# Create your models here.
from django.conf import settings
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from django.db import models
from wagtail.admin.panels import FieldPanel  
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)

    # --- AÑADIR ESTO ---
    # Paneles para el formulario de edición en Wagtail
    panels = [
        FieldPanel('nombre'),
        FieldPanel('apellido'),
        FieldPanel('telefono'),
        FieldPanel('email'),
        FieldPanel('direccion'),
    ]
    # ------------------

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vehiculos")
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField()
    color = models.CharField(max_length=30, blank=True)
    numero_motor = models.CharField(max_length=50, blank=True)

    # --- AÑADIR ESTO ---
    panels = [
        FieldPanel('cliente'), # Esto será un selector para el cliente
        FieldPanel('patente'),
        FieldPanel('marca'),
        FieldPanel('modelo'),
        FieldPanel('año'),
        FieldPanel('color'),
        FieldPanel('numero_motor'),
    ]
    # ------------------

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.patente})"

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
################################
# ... (El código de Cliente y Vehiculo debe estar arriba) ...
class ZonaTrabajo(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True)
    
    panels = [
        FieldPanel('nombre'),
        FieldPanel('descripcion'),
    ]

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Zona de Trabajo"
        verbose_name_plural = "Zonas de Trabajo"


class Mecanico(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="perfil_mecanico"
    )
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    disponible = models.BooleanField(default=True)

    panels = [
        FieldPanel('usuario'),
        FieldPanel('nombre'),
        FieldPanel('especialidad'),
        FieldPanel('telefono'),
        FieldPanel('email'),
        FieldPanel('disponible'),
    ]

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Mecánico"
        verbose_name_plural = "Mecánicos"


class OrdenTrabajo(ClusterableModel):
    # --- Estados de la orden (para el RF004) ---
    ESTADO_CHOICES = [
        ('recepcionado', 'Recepcionado'),
        ('diagnostico', 'En Diagnóstico'),
        ('espera_repuesto', 'Espera de Repuesto'),
        ('en_reparacion', 'En Reparación'),
        ('listo_entrega', 'Listo para Entrega'),
        ('entregado', 'Entregado'),
    ]

    # --- Relaciones ---
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="ordenes")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="ordenes")
    mecanico_asignado = models.ForeignKey(Mecanico, on_delete=models.SET_NULL, null=True, blank=True, related_name="ordenes")
    zona_trabajo = models.ForeignKey(ZonaTrabajo, on_delete=models.SET_NULL, null=True, blank=True, related_name="ordenes")

    # --- Información de la Orden ---
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_estimada = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    
    descripcion_problema = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recepcionado')
    prioridad = models.CharField(max_length=10, choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta')], default='media')

    panels = [
        # Usamos FieldPanel para las relaciones (ForeignKey)
        # Wagtail automáticamente mostrará un selector
        FieldPanel('cliente'),
        FieldPanel('vehiculo'),
        FieldPanel('mecanico_asignado'),
        FieldPanel('zona_trabajo'),
        FieldPanel('descripcion_problema'),
        FieldPanel('estado'),
        FieldPanel('prioridad'),
        FieldPanel('fecha_estimada'),

        InlinePanel('bitacoras', label="Bitácoras Registradas"),
        InlinePanel('presupuestos', label="Presupuestos Generados")
    ]

    def __str__(self):
        return f"Orden #{self.id} - {self.vehiculo.patente}"

    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ['-fecha_ingreso'] # Ordenar por más nuevas primero

class Repuesto(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50, blank=True)
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True)

    descripcion = models.TextField(blank=True)

    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=1)

    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    panels = [
        FieldPanel('nombre'),
        FieldPanel('codigo'),
        FieldPanel('marca'),
        FieldPanel('descripcion'),
        FieldPanel('stock_actual'),
        FieldPanel('stock_minimo'),
        FieldPanel('precio_venta'),
    ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos (Inventario)"      

# Este es el modelo "intermedio"
# Hereda de "Orderable" para poder usarse en un InlinePanel
class BitacoraRepuesto(Orderable):
    # Conectamos con la Bitácora (la "madre")
    bitacora = ParentalKey('gestion.Bitacora', on_delete=models.CASCADE, related_name='repuestos_usados')

    # Conectamos con el Repuesto del inventario
    repuesto = models.ForeignKey('gestion.Repuesto', on_delete=models.PROTECT)

    cantidad = models.PositiveIntegerField(default=1)

    # Paneles para el formulario *dentro* del InlinePanel
    panels = [
        FieldPanel('repuesto'),
        FieldPanel('cantidad'),
    ]

    class Meta:
        unique_together = ('bitacora', 'repuesto') # Evita duplicados


# Este es el modelo principal de la Bitácora
class Bitacora(ClusterableModel):
    # A qué orden pertenece este registro
    orden = ParentalKey(OrdenTrabajo, on_delete=models.PROTECT, related_name='bitacoras')

    # Quién hizo el trabajo
    mecanico = models.ForeignKey(Mecanico, on_delete=models.PROTECT, related_name='bitacoras')

    fecha = models.DateField(auto_now_add=True)
    procedimientos = models.TextField(verbose_name="Procedimientos Realizados")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    panels = [
        FieldPanel('orden'),
        FieldPanel('mecanico'),
        FieldPanel('procedimientos'),
        FieldPanel('observaciones'),

        # --- ¡AQUÍ ESTÁ LA MAGIA! ---
        # Esto crea la sección "Repuestos Utilizados" dentro del formulario de Bitácora
        InlinePanel('repuestos_usados', label="Repuestos Utilizados"),
    ]

    def __str__(self):
        return f"Bitácora para Orden #{self.orden.id} (Por {self.mecanico.nombre})"

    class Meta:
        verbose_name = "Bitácora de Trabajo"
        verbose_name_plural = "Bitácoras de Trabajo"          

class Presupuesto(Orderable): # Hereda de Orderable para el InlinePanel
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    # Conectamos a la Orden de Trabajo
    orden = ParentalKey('gestion.OrdenTrabajo', on_delete=models.CASCADE, related_name='presupuestos')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    
    costo_mano_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_repuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    
    panels = [
        FieldPanel('descripcion'),
        FieldPanel('costo_mano_obra'),
        FieldPanel('costo_repuestos'),
        FieldPanel('estado'),
    ]

    # Propiedad para calcular el total automáticamente
    @property
    def total(self):
        return self.costo_mano_obra + self.costo_repuestos

    def __str__(self):
        return f"Presupuesto #{self.id} para Orden #{self.orden.id}"

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"


class Alerta(models.Model):
    TIPO_CHOICES = [
        ('stock', 'Stock Bajo'),
        ('atraso', 'Atraso en Orden'),
        ('info', 'Informativa'),
    ]

    # La conectamos a una orden (opcionalmente)
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    mensaje = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    resuelta = models.BooleanField(default=False)

    panels = [
        FieldPanel('orden'),
        FieldPanel('tipo'),
        FieldPanel('mensaje'),
        FieldPanel('resuelta'),
    ]

    def __str__(self):
        return f"Alerta ({self.get_tipo_display()}): {self.mensaje}"

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-fecha_creacion']        



class PerfilUsuario(models.Model):
    """Perfil extendido para manejar roles y redirecciones"""
    
    ROLES = [
        ('encargado', 'Encargado de Taller'),
        ('mecanico', 'Mecánico'),
        ('recepcionista', 'Recepcionista'),
    ]
    
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='perfil',
        verbose_name="Usuario"
    )
    
    rol = models.CharField(
        max_length=20, 
        choices=ROLES,
        verbose_name="Rol en el sistema"
    )
    
    # URL de redirección después del login
    dashboard_url = models.CharField(
        max_length=200,
        blank=True,
        default='/gestion/',
        verbose_name="URL del Dashboard",
        help_text="Página a la que se redirige tras iniciar sesión"
    )
    
    # Información adicional
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil"
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Teléfono"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    # Paneles para Wagtail Admin
    panels = [
        FieldPanel('usuario'),
        FieldPanel('rol'),
        FieldPanel('dashboard_url'),
        FieldPanel('foto_perfil'),
        FieldPanel('telefono'),
        FieldPanel('activo'),
    ]
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.get_rol_display()}"
    
    def get_dashboard_url(self):
        """Retorna la URL del dashboard según el rol"""
        urls_por_rol = {
            'encargado': '/gestion/',
            'mecanico': '/gestion/ordenes/',
            'recepcionista': '/gestion/ordenes/',
        }
        return self.dashboard_url or urls_por_rol.get(self.rol, '/gestion/')


# Signal para crear perfil automáticamente
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un usuario"""
    if created and not instance.is_superuser:
        # Detectar rol por grupo
        grupo = instance.groups.first()
        rol_mapa = {
            'Encargado': 'encargado',
            'Mecánico': 'mecanico',
            'Recepcionista': 'recepcionista',
        }
        
        rol = 'recepcionista'  # Default
        if grupo:
            rol = rol_mapa.get(grupo.name, 'recepcionista')
        
        PerfilUsuario.objects.create(
            usuario=instance,
            rol=rol
        )
        print(f"✓ Perfil creado para {instance.username} con rol {rol}")
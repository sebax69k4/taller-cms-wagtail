# SISTEMA DE GESTIÓN DE TALLER MECÁNICO
## Documentación de Acceso y Funcionalidades

### 🔑 CREDENCIALES DE ACCESO

#### Usuario: Encargado (Administrador)
- **Usuario:** `encargado`
- **Contraseña:** `enc123`
- **Permisos:** Acceso completo a todas las funcionalidades

#### Usuario: Mecánico
- **Usuario:** `mecanico`
- **Contraseña:** `mec123`
- **Permisos:** Ver órdenes asignadas, agregar bitácoras

#### Usuario: Recepcionista
- **Usuario:** `recepcionista`
- **Contraseña:** `recep123`
- **Permisos:** Gestión de clientes, vehículos y creación de órdenes

---

## 📋 FUNCIONALIDADES POR ROL

### 👔 ENCARGADO (Administrador)
Acceso completo al sistema con las siguientes capacidades:

#### Dashboard
- ✅ Ver métricas y estadísticas del taller
- ✅ Monitorear alertas de stock
- ✅ Visualizar órdenes recientes
- ✅ Ver carga de trabajo de mecánicos

#### Gestión de Clientes
- ✅ Ver lista de clientes (con búsqueda)
- ✅ Registrar nuevos clientes
- ✅ Editar información de clientes

#### Gestión de Vehículos
- ✅ Ver lista de vehículos (con búsqueda)
- ✅ Registrar nuevos vehículos
- ✅ Editar información de vehículos

#### Gestión de Órdenes de Trabajo
- ✅ Ver todas las órdenes (con filtros)
- ✅ Crear nuevas órdenes
- ✅ Ver detalle de órdenes
- ✅ Asignar mecánicos a órdenes
- ✅ Marcar órdenes como listas para entrega
- ✅ Generar facturas

#### Presupuestos
- ✅ Agregar presupuestos a órdenes
- ✅ Aprobar/rechazar presupuestos
- ✅ Ver historial de presupuestos

#### Disponibilidad
- ✅ Ver disponibilidad de mecánicos
- ✅ Gestionar zonas de trabajo

---

### 🔧 MECÁNICO
Acceso enfocado en el trabajo técnico:

#### Órdenes Asignadas
- ✅ Ver lista de órdenes asignadas
- ✅ Ver detalle de cada orden
- ✅ Filtrar por estado

#### Bitácoras de Trabajo
- ✅ Agregar bitácoras a órdenes asignadas
- ✅ Registrar procedimientos realizados
- ✅ Registrar repuestos utilizados
- ✅ Registrar horas trabajadas

**RESTRICCIÓN:** Solo puede agregar bitácoras a órdenes que le fueron asignadas explícitamente.

---

### 📝 RECEPCIONISTA
Acceso a la interfaz de atención al cliente:

#### Gestión de Clientes
- ✅ Ver lista de clientes (con búsqueda por nombre, RUT, teléfono)
- ✅ Registrar nuevos clientes
- ✅ Editar información de clientes existentes

#### Gestión de Vehículos
- ✅ Ver lista de vehículos (con búsqueda por patente, marca, modelo)
- ✅ Registrar nuevos vehículos
- ✅ Editar información de vehículos

#### Órdenes de Trabajo
- ✅ Ver lista de órdenes
- ✅ Crear nuevas órdenes de trabajo
- ✅ Ver detalle de órdenes
- ✅ Filtrar órdenes por estado/prioridad

**RESTRICCIÓN:** No puede asignar mecánicos ni agregar bitácoras. Solo crear y ver órdenes.

---

## 🚀 CÓMO USAR EL SISTEMA

### Inicio de Sesión
1. Acceder a la página principal: `http://localhost:8000/`
2. Click en el botón **"Iniciar Sesión"**
3. Ingresar credenciales según el rol deseado
4. El sistema redirigirá automáticamente al dashboard correspondiente

### Crear un Cliente (Recepcionista/Encargado)
1. En el menú superior, click en **"Clientes"** → **"Nuevo Cliente"**
2. Completar el formulario:
   - RUT (obligatorio)
   - Nombre completo (obligatorio)
   - Teléfono (opcional)
   - Email (opcional)
   - Dirección (opcional)
3. Click en **"Guardar Cliente"**

### Registrar un Vehículo (Recepcionista/Encargado)
1. En el menú superior, click en **"Vehículos"** → **"Nuevo Vehículo"**
2. Completar el formulario:
   - Patente (obligatorio, ej: AB1234 o LMNT12)
   - Cliente (obligatorio, seleccionar de la lista)
   - Marca (obligatorio)
   - Modelo (obligatorio)
   - Año (opcional)
   - Color (opcional)
   - Kilometraje actual (opcional)
   - Observaciones (opcional)
3. Click en **"Guardar Vehículo"**

### Crear una Orden de Trabajo (Recepcionista/Encargado)
1. En el menú superior, click en **"Nueva Orden"**
2. Completar el formulario:
   - Vehículo (obligatorio, seleccionar de la lista)
   - Cliente (se completa automáticamente al seleccionar vehículo)
   - Prioridad (baja/media/alta)
   - Fecha de ingreso (obligatorio)
   - Kilometraje de ingreso (opcional)
   - Descripción del problema (obligatorio)
   - Observaciones al ingreso (opcional)
3. Click en **"Crear Orden"**
4. La orden se crea en estado **"Recepcionado"**

### Asignar Mecánico a una Orden (Solo Encargado)
1. En **"Órdenes"**, seleccionar una orden
2. En el detalle de la orden, buscar sección **"Asignar Mecánico"**
3. Seleccionar mecánico de la lista
4. Click en **"Asignar"**

### Agregar Bitácora de Trabajo (Solo Mecánico)
1. En **"Órdenes"**, ver órdenes asignadas
2. Click en una orden asignada
3. Click en **"Agregar Bitácora"**
4. Completar el formulario:
   - Fecha (obligatorio)
   - Descripción del trabajo realizado (obligatorio)
   - Horas trabajadas (opcional)
   - Procedimientos/repuestos utilizados (opcional, múltiple selección)
5. Click en **"Guardar Bitácora"**

**NOTA:** El mecánico solo puede agregar bitácoras a órdenes que le fueron asignadas.

### Agregar Presupuesto (Solo Encargado)
1. En el detalle de una orden, click en **"Agregar Presupuesto"**
2. Completar el formulario:
   - Fecha (obligatorio)
   - Descripción (obligatorio)
   - Items/servicios/repuestos (opcional, múltiple selección)
   - Total mano de obra (obligatorio)
   - Total repuestos (obligatorio)
   - Validez en días (opcional, por defecto 30 días)
   - Observaciones (opcional)
3. Click en **"Guardar Presupuesto"**

---

## 🎨 CARACTERÍSTICAS DE LA INTERFAZ

### Búsqueda Inteligente
- **Clientes:** Buscar por nombre, RUT o teléfono
- **Vehículos:** Buscar por patente, marca o modelo
- **Órdenes:** Filtrar por estado, prioridad, mecánico

### Navegación por Roles
El menú se adapta automáticamente según el rol del usuario:
- **Encargado:** Acceso completo a todos los menús
- **Mecánico:** Solo menú de órdenes
- **Recepcionista:** Menús de clientes, vehículos y órdenes (sin asignación)

### Indicadores Visuales
- **Badges de rol:** Muestra el rol del usuario en la esquina superior derecha
- **Estados de órdenes:** Colores diferentes según el estado
  - Gris: Recepcionado
  - Azul: En diagnóstico
  - Amarillo: En reparación
  - Rojo: Esperando repuestos
  - Verde: Listo para entrega
  - Negro: Entregado

---

## ⚙️ COMANDOS DE GESTIÓN

### Crear/Actualizar Usuarios de Prueba
```bash
python manage.py setup_initial_data
```
Esto creará o actualizará los usuarios: encargado, mecanico, recepcionista

### Corregir Permisos de Usuarios
```bash
python manage.py fix_user_permissions
```
Esto corrige los flags `is_staff` para usuarios no administrativos

---

## 🛡️ SEGURIDAD Y PERMISOS

### Control de Acceso
- ✅ Todas las vistas requieren autenticación (`@login_required`)
- ✅ Decoradores de permiso por rol (`@user_passes_test`)
- ✅ Validación de permisos en templates con `{% if user|has_group:"..." %}`
- ✅ Normalización Unicode de nombres de grupos (robusto ante variaciones)

### Restricciones por Rol
- **Mecánicos:** No pueden crear órdenes, clientes ni vehículos
- **Recepcionistas:** No pueden asignar mecánicos ni agregar bitácoras
- **Verificación adicional:** Los mecánicos solo pueden agregar bitácoras a sus órdenes asignadas

---

## 📂 ESTRUCTURA DE ARCHIVOS CREADOS/MODIFICADOS

### Templates Creados
```
gestion/templates/gestion/
├── lista_clientes.html          # Lista de clientes con búsqueda
├── registrar_cliente.html       # Formulario para nuevo cliente
├── editar_cliente.html          # Formulario para editar cliente
├── lista_vehiculos.html         # Lista de vehículos con búsqueda
├── registrar_vehiculo.html      # Formulario para nuevo vehículo
├── editar_vehiculo.html         # Formulario para editar vehículo
├── crear_orden.html             # Formulario para nueva orden
├── agregar_bitacora.html        # Formulario para bitácora (mecánicos)
└── agregar_presupuesto.html     # Formulario para presupuesto (encargados)
```

### Archivos Python Modificados/Creados
```
gestion/
├── forms.py                     # ModelForms para CRUD
├── views.py                     # Vistas con decoradores de permisos
├── urls.py                      # Rutas para todas las vistas
├── models.py                    # Método get_estado_color agregado
├── templates/gestion/base.html  # Navbar actualizado con menús por rol
└── management/commands/
    ├── setup_initial_data.py    # Comando para crear usuarios
    └── fix_user_permissions.py  # Comando para corregir permisos
```

---

## ✅ CHECKLIST DE FUNCIONALIDADES IMPLEMENTADAS

### Frontend CRUD Completo
- [x] Lista de clientes con búsqueda
- [x] Registrar nuevos clientes
- [x] Editar clientes existentes
- [x] Lista de vehículos con búsqueda
- [x] Registrar nuevos vehículos
- [x] Editar vehículos existentes
- [x] Crear nuevas órdenes de trabajo
- [x] Agregar bitácoras (mecánicos)
- [x] Agregar presupuestos (encargados)

### Control de Acceso
- [x] Decoradores de permisos por rol
- [x] Menú adaptativo según rol
- [x] Validación de permisos en templates
- [x] Restricción de bitácoras por mecánico asignado

### Experiencia de Usuario
- [x] Bootstrap 5 con diseño responsivo
- [x] Iconos Font Awesome
- [x] Mensajes de éxito/error
- [x] Breadcrumbs y navegación clara
- [x] Indicadores visuales de estado
- [x] Badges de rol en navbar

---

## 🚨 IMPORTANTE

### Todo se hace desde el Frontend
- ✅ **NO es necesario acceder al panel de Wagtail** para operaciones diarias
- ✅ El panel de Wagtail (`/admin/`) solo es para:
  - Configuración de procedimientos
  - Gestión de repuestos e inventario
  - Configuración de zonas de trabajo
  - Administración de usuarios (por el superusuario)

### Flujo de Trabajo Típico
1. **Recepcionista** recibe al cliente
2. Si es nuevo, registra el cliente y su vehículo
3. Crea una orden de trabajo con la descripción del problema
4. **Encargado** revisa la orden y asigna un mecánico
5. **Mecánico** trabaja en el vehículo y registra bitácoras
6. **Encargado** genera presupuesto y marca como listo
7. **Recepcionista** o **Encargado** genera la factura y entrega

---

## 📞 SOPORTE

Para cualquier problema o consulta:
1. Verificar que el servidor esté corriendo: `python manage.py runserver`
2. Revisar credenciales de acceso en esta documentación
3. Ejecutar `python manage.py check` para verificar configuración
4. Revisar la consola del servidor para mensajes de error

---

**Última actualización:** 2025
**Versión del Sistema:** 1.0
**Framework:** Django 5.2.7 + Wagtail 6.0+

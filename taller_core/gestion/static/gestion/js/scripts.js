

// taller_core/gestion/static/gestion/js/scripts.js

console.log('✓ Sistema de Gestión de Taller cargado');

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
    
    // Confirmación en acciones importantes
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || '¿Estás seguro?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Búsqueda en tiempo real en tablas
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
    
    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Actualizar badge de alertas
    actualizarContadorAlertas();
    
    // Auto-refresh de dashboard cada 30 segundos (opcional)
    if (document.querySelector('[data-auto-refresh]')) {
        setInterval(() => {
            location.reload();
        }, 30000);
    }
});

// Función para actualizar contador de alertas
function actualizarContadorAlertas() {
    const alertBadge = document.getElementById('alertCount');
    if (alertBadge) {
        fetch('/api/alertas/count/') // Esta API la puedes crear después
            .then(res => res.json())
            .then(data => {
                if (data.count > 0) {
                    alertBadge.textContent = data.count;
                    alertBadge.style.display = 'inline';
                }
            })
            .catch(() => console.log('No se pudo obtener contador de alertas'));
    }
}

// Formatear moneda chilena
function formatearPrecio(valor) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(valor);
}

// Copiar al portapapeles
function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto).then(() => {
        mostrarNotificacion('Copiado al portapapeles', 'success');
    });
}

// Mostrar notificación toast
function mostrarNotificacion(mensaje, tipo = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${tipo} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${mensaje}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.querySelector('.toast-container') || crearToastContainer();
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toast = new bootstrap.Toast(toastContainer.lastElementChild);
    toast.show();
}

function crearToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

console.log('✅ Scripts cargados correctamente');

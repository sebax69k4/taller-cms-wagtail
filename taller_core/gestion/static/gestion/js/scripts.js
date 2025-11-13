// taller_core/gestion/static/gestion/js/scripts.js

console.log('✓ Scripts del sistema cargados');

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    });
});

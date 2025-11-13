# taller_core/gestion/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import OrdenTrabajo, Alerta, BitacoraRepuesto


@receiver(post_save, sender=OrdenTrabajo)
def crear_alerta_cambio_estado(sender, instance, created, **kwargs):
    """Crea alertas cuando cambia el estado de una orden"""
    if created:
        # Nueva orden recibida
        Alerta.objects.create(
            orden=instance,
            tipo='info',
            mensaje=f'Nueva orden #{instance.id} recibida - {instance.vehiculo.patente}'
        )
        print(f"✓ Alerta creada: Nueva orden #{instance.id}")
    else:
        # Orden actualizada
        if instance.estado == 'listo_entrega':
            # Verificar que no exista ya una alerta
            existe = Alerta.objects.filter(
                orden=instance,
                tipo='info',
                mensaje__contains='lista para entrega'
            ).exists()
            
            if not existe:
                Alerta.objects.create(
                    orden=instance,
                    tipo='info',
                    mensaje=f'Orden #{instance.id} lista para entrega - Cliente: {instance.cliente.nombre} {instance.cliente.apellido}'
                )
                print(f"✓ Alerta creada: Orden #{instance.id} lista")


@receiver(post_save, sender=BitacoraRepuesto)
def actualizar_stock_repuesto(sender, instance, created, **kwargs):
    """Descuenta del stock cuando se usa un repuesto"""
    if created:
        repuesto = instance.repuesto
        
        # Descontar del stock
        if repuesto.stock_actual >= instance.cantidad:
            repuesto.stock_actual -= instance.cantidad
            repuesto.save()
            
            # Crear alerta si stock está bajo
            if repuesto.stock_actual <= repuesto.stock_minimo:
                Alerta.objects.create(
                    tipo='stock',
                    mensaje=f'Stock bajo: {repuesto.nombre} - Quedan {repuesto.stock_actual} unidades'
                )
                print(f"⚠️ ALERTA: Stock bajo de {repuesto.nombre}")
        else:
            print(f"⚠️ ERROR: No hay suficiente stock de {repuesto.nombre}")


print("✓ Signals de gestion cargados correctamente")

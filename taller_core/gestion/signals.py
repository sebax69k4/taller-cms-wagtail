# taller_core/gestion/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import OrdenTrabajo, Alerta, BitacoraRepuesto, Repuesto


@receiver(post_save, sender=OrdenTrabajo)
def crear_alerta_cambio_estado(sender, instance, created, **kwargs):
    """
    Crea alertas cuando cambia el estado de una orden
    """
    if created:
        # Nueva orden recibida
        Alerta.objects.create(
            orden=instance,
            tipo='info',
            mensaje=f'Nueva orden #{instance.id} recibida - {instance.vehiculo.patente}'
        )
    else:
        # Orden actualizada - verificar cambios importantes
        if instance.estado == 'listo_entrega':
            Alerta.objects.create(
                orden=instance,
                tipo='info',
                mensaje=f'Orden #{instance.id} lista para entrega - Cliente: {instance.cliente.nombre} {instance.cliente.apellido}'
            )


@receiver(post_save, sender=BitacoraRepuesto)
def actualizar_stock_repuesto(sender, instance, created, **kwargs):
    """
    Descuenta del stock cuando se usa un repuesto en una bitácora
    y crea alerta si stock es bajo
    """
    if created:
        repuesto = instance.repuesto
        
        # Descontar del stock
        repuesto.stock_actual -= instance.cantidad
        repuesto.save()
        
        # Crear alerta si stock está bajo
        if repuesto.stock_actual <= repuesto.stock_minimo:
            Alerta.objects.create(
                tipo='stock',
                mensaje=f'Stock bajo: {repuesto.nombre} ({repuesto.codigo}) - Quedan {repuesto.stock_actual} unidades'
            )
            print(f"⚠️ ALERTA: Stock bajo de {repuesto.nombre}")


@receiver(pre_save, sender=OrdenTrabajo)
def detectar_atrasos(sender, instance, **kwargs):
    """
    Detecta órdenes atrasadas y crea alertas
    """
    from django.utils import timezone
    
    # Solo para órdenes existentes
    if instance.pk:
        # Si tiene fecha estimada y ya pasó
        if instance.fecha_estimada and instance.fecha_estimada < timezone.now():
            # Verificar si ya existe una alerta de atraso
            existe_alerta = Alerta.objects.filter(
                orden=instance,
                tipo='atraso',
                resuelta=False
            ).exists()
            
            if not existe_alerta and instance.estado not in ['listo_entrega', 'entregado']:
                Alerta.objects.create(
                    orden=instance,
                    tipo='atraso',
                    mensaje=f'Orden #{instance.id} atrasada - Estimada: {instance.fecha_estimada.strftime("%d/%m/%Y")}'
                )
                print(f"⚠️ ALERTA: Orden #{instance.id} atrasada")


print("✓ Signals de gestion cargados")

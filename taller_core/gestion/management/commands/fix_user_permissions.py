from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Corrige los permisos de los usuarios de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Corrigiendo permisos de usuarios...\n')
        
        # Usuarios que NO deben ser staff
        usuarios_normales = ['recepcionista', 'mecanico']
        
        for username in usuarios_normales:
            try:
                user = User.objects.get(username=username)
                
                # Mostrar estado actual
                self.stdout.write(f'\n{username}:')
                self.stdout.write(f'  - is_staff: {user.is_staff}')
                self.stdout.write(f'  - is_superuser: {user.is_superuser}')
                self.stdout.write(f'  - grupos: {[g.name for g in user.groups.all()]}')
                
                # Corregir permisos
                if user.is_staff or user.is_superuser:
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Permisos corregidos para {username}'))
                else:
                    self.stdout.write(f'  ✓ {username} ya tiene permisos correctos')
                    
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ✗ Usuario {username} no existe'))
        
        # Usuario encargado SÍ debe ser staff (para acceder al admin de Wagtail si es necesario)
        try:
            encargado = User.objects.get(username='encargado')
            self.stdout.write(f'\nencargado:')
            self.stdout.write(f'  - is_staff: {encargado.is_staff}')
            self.stdout.write(f'  - is_superuser: {encargado.is_superuser}')
            
            if not encargado.is_staff:
                encargado.is_staff = True
                encargado.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Permisos de staff habilitados para encargado'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'  ✗ Usuario encargado no existe'))
        
        self.stdout.write('\n' + self.style.SUCCESS('✓ Corrección de permisos completada'))

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Crea usuarios y grupos de prueba para el sistema'

    def handle(self, *args, **options):
        self.stdout.write('Configurando datos iniciales...\n')
        
        # Crear grupos si no existen
        grupos_data = [
            'Encargado',
            'Mecánico',
            'Recepcionista',
        ]
        
        for grupo_nombre in grupos_data:
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Grupo "{grupo_nombre}" creado'))
            else:
                self.stdout.write(f'  - Grupo "{grupo_nombre}" ya existe')
        
        # Crear usuarios de prueba
        usuarios_data = [
            {
                'username': 'encargado',
                'password': 'enc123',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'email': 'encargado@taller.com',
                'is_staff': True,  # Encargado SÍ puede acceder al admin
                'grupo': 'Encargado'
            },
            {
                'username': 'mecanico',
                'password': 'mec123',
                'first_name': 'Carlos',
                'last_name': 'González',
                'email': 'mecanico@taller.com',
                'is_staff': False,  # Mecánico NO debe acceder al admin
                'grupo': 'Mecánico'
            },
            {
                'username': 'recepcionista',
                'password': 'recep123',
                'first_name': 'María',
                'last_name': 'López',
                'email': 'recepcionista@taller.com',
                'is_staff': False,  # Recepcionista NO debe acceder al admin
                'grupo': 'Recepcionista'
            },
        ]
        
        self.stdout.write('\nCreando/actualizando usuarios...')
        
        for user_data in usuarios_data:
            username = user_data['username']
            password = user_data['password']
            grupo_nombre = user_data.pop('grupo')
            
            # Crear o actualizar usuario
            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'\n✓ Usuario "{username}" creado'))
            else:
                # Actualizar usuario existente
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.email = user_data['email']
                user.is_staff = user_data['is_staff']
                user.is_superuser = False
                user.is_active = True
                user.set_password(password)  # Actualizar contraseña
                user.save()
                self.stdout.write(self.style.SUCCESS(f'\n✓ Usuario "{username}" actualizado'))
            
            # Asignar al grupo
            grupo = Group.objects.get(name=grupo_nombre)
            user.groups.clear()  # Limpiar grupos anteriores
            user.groups.add(grupo)
            
            self.stdout.write(f'  - Nombre: {user.get_full_name()}')
            self.stdout.write(f'  - Email: {user.email}')
            self.stdout.write(f'  - Grupo: {grupo_nombre}')
            self.stdout.write(f'  - is_staff: {user.is_staff}')
            self.stdout.write(f'  - Contraseña: {password}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✓ CONFIGURACIÓN COMPLETADA'))
        self.stdout.write('='*50)
        self.stdout.write('\nCredenciales de acceso:')
        self.stdout.write('  • encargado / enc123')
        self.stdout.write('  • mecanico / mec123')
        self.stdout.write('  • recepcionista / recep123')
        self.stdout.write('')

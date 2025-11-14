from django import forms
from .models import Cliente, Vehiculo, OrdenTrabajo, Bitacora, BitacoraRepuesto, Presupuesto

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa'}),
        }

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['cliente', 'patente', 'marca', 'modelo', 'año', 'color', 'numero_motor']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'patente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AA-BB-12'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Toyota, Ford, etc.'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Corolla, Focus, etc.'}),
            'año': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2020'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rojo, Azul, etc.'}),
            'numero_motor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de motor'}),
        }

class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = ['cliente', 'vehiculo', 'descripcion_problema', 'prioridad', 'fecha_estimada']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion_problema': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa el problema...'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_estimada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay un cliente seleccionado, filtrar los vehículos
        if 'cliente' in self.data:
            try:
                cliente_id = int(self.data.get('cliente'))
                self.fields['vehiculo'].queryset = Vehiculo.objects.filter(cliente_id=cliente_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['vehiculo'].queryset = self.instance.cliente.vehiculos.all()

class BitacoraForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        fields = ['procedimientos', 'observaciones']
        widgets = {
            'procedimientos': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa los procedimientos realizados...'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales (opcional)'}),
        }

class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ['descripcion', 'costo_mano_obra', 'costo_repuestos', 'estado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del presupuesto...'}),
            'costo_mano_obra': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'costo_repuestos': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

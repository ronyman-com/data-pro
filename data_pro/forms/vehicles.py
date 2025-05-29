from django import forms
from models.vehicles import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'license_plate', 'vehicle_type', 
                 'capacity', 'status', 'last_maintenance', 'next_maintenance']
        widgets = {
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'next_maintenance': forms.DateInput(attrs={'type': 'date'}),
        }
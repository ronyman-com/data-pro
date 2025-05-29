from django import forms
from models.transports import Transport

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ['customer', 'vehicle', 'pickup_location', 'dropoff_location', 
                 'pickup_time', 'dropoff_time', 'distance', 'fare', 'status', 'notes']
        widgets = {
            'pickup_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'dropoff_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
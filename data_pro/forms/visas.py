from django import forms
from models.visas import Visa

class VisaForm(forms.ModelForm):
    class Meta:
        model = Visa
        fields = ['customer', 'visa_type', 'country', 'application_date', 
                 'expiry_date', 'status', 'notes']
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
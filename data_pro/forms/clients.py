from django import forms
from data_pro.models.clients import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['company_name', 'contact_person', 'email', 'phone', 'status']
        # Remove 'address' if it's not in your model
        # Or add it to your model if you need it
        
        widgets = {
            'status': forms.Select(choices=Client.STATUS_CHOICES),
        }
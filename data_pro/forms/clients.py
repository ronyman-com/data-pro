from django import forms
from models.clients import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['company_name', 'contact_person', 'email', 'phone', 'address', 'status']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
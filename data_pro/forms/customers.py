from django import forms
from data_pro.models.customers import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'status', 'client']
        # Remove 'address' since it's not in your model
        # Or add it to your model if you need it

        widgets = {
            'status': forms.Select(choices=Customer.STATUS_CHOICES),
            'client': forms.Select(attrs={'class': 'form-control'}),
        }